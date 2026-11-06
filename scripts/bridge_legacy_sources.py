#!/usr/bin/env python3
"""Inventory legacy source versions; optionally replay verified retained bytes to bc-store.

No retrieval, rights decision, factual review or source-date renewal occurs here.
Missing payloads remain explicit gaps rather than hash-only payload references.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

from archive_research_attempts import public_source_url


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(root, manifests):
    root = root.resolve()
    records = []
    inputs = {}
    cache = {}
    for manifest in sorted(manifests):
        raw = manifest.read_bytes()
        label = str(manifest.resolve().relative_to(root))
        inputs[label] = sha(raw)
        for number, line in enumerate(raw.splitlines(keepends=True), 1):
            if not line.strip():
                raise ValueError('Blank manifest line needs an explicit mapping: ' + label)
            row = json.loads(line)
            files = []
            missing = []
            for filename in row.get('files', []):
                path = root / filename
                # Legacy body symlinks intentionally resolve to admitted external archives.
                if not path.absolute().is_relative_to(root) or '..' in Path(filename).parts:
                    raise ValueError('Source path escapes repository: ' + filename)
                if not path.is_file():
                    missing.append(filename)
                    continue
                if filename not in cache:
                    body = path.read_bytes()
                    cache[filename] = (sha(body), len(body))
                digest, size = cache[filename]
                files.append({'path': filename, 'sha256': digest, 'bytes': size})
            payload = next((f for f in files if f['sha256'] == row.get('sha256')), None)
            text = None
            text_candidates = [f for f in files if Path(f['path']).suffix in ('.txt', '.md')]
            if row.get('text_sha256'):
                text = next((f for f in text_candidates if f['sha256'] == row['text_sha256']), None)
            elif text_candidates:
                text = next((f for f in text_candidates if f['path'].endswith('.txt')), text_candidates[0])
            issues = []
            if not payload:
                issues.append('original_body_not_retained_or_hash_not_matched')
            if row.get('text_sha256') and not text:
                issues.append('asserted_text_hash_not_matched')
            try:
                stamp = datetime.fromisoformat(row['fetched_at'].replace('Z', '+00:00'))
                if stamp.tzinfo is None:
                    raise ValueError('Naive timestamp')
                at = stamp.timestamp()
            except (KeyError, TypeError, ValueError):
                at = None
                issues.append('missing_or_invalid_timezone_bearing_retrieval_time')
            if not isinstance(row.get('ok'), bool):
                issues.append('missing_explicit_acquisition_outcome')
            record = {'manifest': label, 'line': number, 'legacy_key': row.get('key'),
                      'row_sha256': sha(line), 'url': public_source_url(row['url']),
                      'original_body_sha256': row.get('sha256'),
                      'original_text_sha256': row.get('text_sha256'),
                      'fetched_at': row.get('fetched_at'), 'published': row.get('published'),
                      'payload': payload, 'text': text, 'missing_files': missing,
                      'issues': issues, 'at': at, '_row': row, '_line': line}
            if record['url'] != row['url']:
                record['retrieval_url_sha256'] = sha(row['url'].encode())
            records.append(record)
    groups = defaultdict(list)
    for record in records:
        if record['at'] is not None:
            groups[(record['_row']['url'], record['at'])].append(record)
    for group in groups.values():
        # Native observation identity is source/kind/time; never invent a timestamp
        # to squeeze conflicting historical bodies into the same observation.
        if len({r['original_body_sha256'] for r in group}) > 1:
            for record in group:
                record['issues'].append('native_observation_identity_body_conflict')
    return records, inputs


def migrate(root, records, store_path):
    from bc_store import Store
    from bc_core.ids import stable_id

    eligible = sorted((r for r in records if not r['issues']), key=lambda r: r['at'])
    # Validate the complete batch and existing observation identities before writes.
    with Store(store_path) as store:
        for record in eligible:
            source_id = stable_id('source', record['_row']['url'])
            oid = stable_id('observation', source_id, 'fetch', record['at'])
            existing = store.observation(oid)
            if existing and existing.payload_sha256 != record['payload']['sha256']:
                raise ValueError('Existing observation payload conflict: ' + oid)
            for descriptor in (record['payload'], record['text']):
                if descriptor and sha((root / descriptor['path']).read_bytes()) != descriptor['sha256']:
                    raise ValueError('Retained bytes changed after inventory')
        for record in eligible:
            row = record['_row']
            prior_source = store.source_by_key(row['url'])
            source = store.upsert_source(row['url'], row['url'],
                                         at=max(record['at'], prior_source.last_seen) if prior_source else record['at'])
            obs = store.record(source, payload=(root / record['payload']['path']).read_bytes(),
                               payload_sha256=record['payload']['sha256'], at=record['at'],
                               ok=row['ok'], status=row.get('status'), final_url=row.get('final_url'),
                               content_type=row.get('content_type'),
                               observation_scope='Legacy archived retrieval replay; not a fresh request')
            # Exact original line is private metadata; one producer per pinned row
            # preserves access flags, URLs, derivation lineage and unknown fields.
            derivation = store.derive(obs, 'metadata', payload=record['_line'],
                                     producer='legacy-manifest-row:' + record['row_sha256'], at=record['at'])
            record['observation_id'] = obs.id
            record['metadata_derivation_id'] = derivation.id
            if store.blobs.get(derivation.sha256) != record['_line']:
                raise ValueError('Original manifest-line readback mismatch')
            if record['text']:
                text = (root / record['text']['path']).read_bytes()
                d = store.derive(obs, 'text', payload=text,
                                 producer='legacy-text:' + record['text']['sha256'], at=record['at'])
                record['text_derivation_id'] = d.id
            if store.payload(obs) != (root / record['payload']['path']).read_bytes():
                raise ValueError('Store payload readback mismatch')
    return len(eligible)


def report(records, inputs, migrated=None):
    return {'manifest_sha256': inputs, 'record_count': len(records),
            'eligible_verified_body_records': sum(not r['issues'] for r in records),
            'gap_records': sum(bool(r['issues']) for r in records),
            'issue_counts': dict(Counter(issue for r in records for issue in r['issues'])),
            'migrated_records': migrated,
            'records': [{k: v for k, v in r.items() if not k.startswith('_') and k != 'at'} for r in records],
            'scope': 'Reversible legacy-manifest mapping and retained-byte verification only. '
                     'Original publication values are preserved, not reassessed. All store material remains '
                     'private; no source/legal acceptance, complete extraction, fresh acquisition or '
                     'automatic public export. Missing bodies are not migrated as hash-only payloads.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--manifest', action='append', type=Path)
    p.add_argument('--store', type=Path, help='Private bc-store root; requires admitted local SQLite and external blob routing')
    p.add_argument('--apply', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.apply and not args.store:
        p.error('--apply requires --store')
    records, inputs = inventory(args.root, args.manifest or list((args.root / 'work/sources').glob('*/manifest.jsonl')))
    migrated = migrate(args.root, records, args.store) if args.apply else None
    output = report(records, inputs, migrated)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k not in ('records', 'manifest_sha256', 'scope')}, indent=2))
