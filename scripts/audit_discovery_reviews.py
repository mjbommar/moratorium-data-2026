#!/usr/bin/env python3
"""Independently check distributed discovery-review returns, without promotion."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from audit_refresh_returns import evidence_index, load_lines, pinned_evidence_index
from archive_research_attempts import public_source_url


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def audit_candidate(candidate, assigned, originals, index, validator, failed_index=None):
    issues = []
    key = candidate['candidate_key']
    if key not in assigned:
        return ['Candidate outside assignment'], []
    original = originals[key]
    if candidate.get('disposition') not in {'existing_same_instrument', 'distinct_supported_candidate',
                                          'distinct_historical_instrument', 'not_a_moratorium', 'unresolved'}:
        issues.append('Unknown review disposition')
    if not candidate.get('rationale'):
        issues.append('Missing substantive rationale')
    fingerprint = digest(json.dumps(original, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode())
    if fingerprint != assigned[key]['candidate_sha256'] or fingerprint != candidate.get('candidate_sha256'):
        issues.append('Original candidate fingerprint mismatch')
    proofs = []
    for check in candidate.get('source_checks', []):
        versions = [v for v in index.get(check.get('url'), [])
                    if v['attempt_id'] == check.get('attempt_id')
                    and v['body_sha256'] == check.get('body_sha256')
                    and v['text_sha256'] == check.get('text_sha256')]
        body_verified = bool(versions)
        failed_verified = (check.get('verified_success') is False
                           and any(v['attempt_id'] == check.get('attempt_id')
                                   and v['body_sha256'] == check.get('body_sha256')
                                   and v['text_sha256'] == check.get('text_sha256')
                                   for v in (failed_index or {}).get(check.get('url'), [])))
        quote = check.get('quote')
        span = check.get('quote_span')
        quote_verified = (bool(quote) and isinstance(span, list) and len(span) == 2
                          and all(type(n) is int for n in span)
                          and any(0 <= span[0] <= span[1] <= len(v['text'])
                                  and v['text'][span[0]:span[1]] == quote for v in versions))
        if not body_verified and not failed_verified:
            issues.append('Declared source version/attempt not independently verified: ' + str(check.get('attempt_id')))
        if quote and not quote_verified:
            issues.append('Exact quote span mismatch: ' + str(check.get('attempt_id')))
        proofs.append({'attempt_id': check.get('attempt_id'), 'body_text_verified': body_verified,
                       'url': public_source_url(check.get('url', '')),
                       'declared_body_sha256': check.get('body_sha256'),
                       'declared_text_sha256': check.get('text_sha256'),
                       'failed_acquisition_verified': bool(failed_verified),
                       'quote_span_verified': bool(quote_verified),
                       'coordinator_visual_review_required': body_verified and not quote_verified})
    proposal = candidate.get('proposed_candidate')
    if proposal is not None:
        issues.extend('Proposed candidate schema: ' + e.message for e in validator.iter_errors(proposal))
    if not candidate.get('source_checks'):
        issues.append('No pinned source checks')
    return issues, proofs


def audit(queues, private_root, root, reusable_config=None, baseline_inventory=None):
    contract = json.loads((root / 'work/schemas/research_decision.schema.json').read_text())
    validator = Draft202012Validator({'$ref': '#/$defs/candidate', '$defs': contract['$defs']})
    reusable = {}
    reusable_hash = None
    if reusable_config:
        raw = reusable_config.read_bytes()
        config = json.loads(raw)
        reusable_hash = digest(raw)
        reusable, errors = pinned_evidence_index(Path(config['base']), Path(config['manifest']),
                                                config['manifest_sha256'], config['source_documents'])
        if errors:
            raise ValueError('Pinned reusable evidence failed verification: ' + str(errors))
        for entries in reusable.values():
            for entry in entries:
                sid = entry['attempt_id'].removeprefix('reused:')
                entry['attempt_id'] = config['attempt_aliases'][sid]
    baseline_path = baseline_inventory or root / 'data/moratorium_inventory.csv'
    live_hash = digest(baseline_path.read_bytes())
    indices = {}
    failures = {}
    outputs = []
    seen = Counter()
    expected = set()
    for queue_path in queues:
        queue = json.loads(queue_path.read_text())
        for job in queue['jobs']:
            directory = private_root / job['id']
            packet_path = directory / 'packet.json'
            packet_raw = packet_path.read_bytes()
            packet = json.loads(packet_raw)
            expected.update(r['candidate_key'] for r in packet['assigned_candidates'])
            review_path = directory / 'review.json'
            status_paths = [private_root / lane / job['id'] / 'status.json' for lane in ('runs', 'closure-runs')]
            status_path = next((s for s in status_paths if s.exists()), None)
            status = json.loads(status_path.read_text()) if status_path else {}
            if status.get('state') != 'finished' or status.get('exit_code') != 0:
                outputs.append({'job_id': job['id'], 'return_present': False,
                                'cli_state': status.get('state', 'not_started'),
                                'draft_review_present': review_path.exists()})
                continue
            if not review_path.exists():
                outputs.append({'job_id': job['id'], 'return_present': False})
                continue
            review_raw = review_path.read_bytes()
            review = json.loads(review_raw)
            assigned = {r['candidate_key']: r for r in packet['assigned_candidates']}
            originals = {}
            source_issues = []
            combined = {url: list(entries) for url, entries in reusable.items()}
            combined_failed = {}
            for state, folder in packet['returned_directories'].items():
                directory_state = Path(folder)
                if folder not in indices:
                    indices[folder] = evidence_index(directory_state)
                    failed = {}
                    for event in load_lines(directory_state / 'attempts.private.jsonl'):
                        if event.get('state') != 'finished' or event.get('kind') != 'fetch' or event.get('ok') is not False:
                            continue
                        artifact = Path(event['artifact']).resolve()
                        if not artifact.is_relative_to(directory_state.resolve()):
                            continue
                        stem = artifact.with_suffix('')
                        body = stem.with_suffix(stem.suffix + '.body')
                        text = stem.with_suffix(stem.suffix + '.txt')
                        if (body.is_file() and text.is_file()
                                and digest(body.read_bytes()) == event.get('body_sha256')
                                and digest(text.read_bytes()) == event.get('text_sha256')):
                            failed.setdefault(event['url'], []).append(event)
                    failures[folder] = failed
                index, errors, _ = indices[folder]
                source_issues.extend(errors)
                for url, entries in index.items():
                    combined.setdefault(url, []).extend(entries)
                for url, entries in failures[folder].items():
                    combined_failed.setdefault(url, []).extend(entries)
                answers = json.loads((directory_state / 'answers.json').read_text())
                originals.update({f'discovery-{state.lower()}:{i}': c
                                  for i, c in enumerate(answers.get('new_candidates', []))})
            returned = [r['candidate_key'] for r in review['candidates']]
            issues = []
            if digest(packet_raw) != job['packet_sha256']:
                issues.append('Packet fingerprint mismatch')
            if live_hash != queue['inventory_sha256'] or live_hash != review.get('baseline_inventory_sha256'):
                issues.append('Baseline inventory drift')
            records = []
            baseline_ids = {r['moratorium_id'] for r in packet['baseline_inventory_rows']}
            for candidate in review['candidates']:
                errors, proofs = audit_candidate(candidate, assigned, originals, combined, validator, combined_failed)
                if set(candidate.get('matched_inventory_ids', [])) - baseline_ids:
                    errors.append('Matched inventory ID outside frozen state baseline')
                seen[candidate['candidate_key']] += 1
                records.append({'candidate_key': candidate['candidate_key'],
                                'worker_disposition': candidate['disposition'],
                                'mechanical_issues': errors, 'source_proofs': proofs,
                                'scope': 'Worker recommendation only; coordinator substantive review and canonical promotion remain separate.'})
            outputs.append({'job_id': job['id'], 'return_present': True,
                            'review_sha256': digest(review_raw), 'packet_sha256': digest(packet_raw),
                            'assigned': len(assigned), 'returned': len(returned),
                            'missing_keys': sorted(set(assigned) - set(returned)),
                            'extra_keys': sorted(set(returned) - set(assigned)),
                            'duplicate_keys': sorted(k for k, count in Counter(returned).items() if count > 1),
                            'issues': issues, 'source_directory_issues': source_issues, 'candidates': records})
    return {'baseline_inventory_sha256': live_hash, 'jobs': outputs,
            'baseline_inventory_path': str(baseline_path),
            'reusable_evidence_config_sha256': reusable_hash,
            'duplicate_candidate_keys_across_returns': sorted(k for k, count in seen.items() if count > 1),
            'distinct_returned_candidates': len(seen),
            'expected_distinct_candidates': len(expected),
            'not_returned_anywhere': sorted(expected - set(seen)),
            'scope': 'Independent identity/hash/schema/span checks only. Partial returns remain partial; '
                     'worker dispositions are not substantive acceptance or canonical changes. '
                     'Visual assertions require independent coordinator review.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue', type=Path, action='append', required=True)
    p.add_argument('--private-root', type=Path, required=True)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reusable-evidence-config', type=Path, help='Explicit coordinator-pinned reusable artifact manifest and aliases')
    p.add_argument('--baseline-inventory', type=Path, help='Explicit retained frozen inventory; default checks current canonical CSV')
    args = p.parse_args()
    result = audit(args.queue, args.private_root, args.root, args.reusable_evidence_config, args.baseline_inventory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'distinct_returned_candidates': result['distinct_returned_candidates'],
                      'duplicate_candidate_keys': result['duplicate_candidate_keys_across_returns']}))
