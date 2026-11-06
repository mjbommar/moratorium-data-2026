#!/usr/bin/env python3
"""Validate explicit duration-review returns; never accept or apply recommendations."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row_hash(row):
    return sha(json.dumps(row, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_return(packet, answers, job_id, inventory_sha256):
    require(set(answers) == {'job_id', 'inventory_sha256', 'decisions'}, 'Wrong answer envelope')
    require(answers['job_id'] == job_id and answers['inventory_sha256'] == inventory_sha256,
            'Answer baseline mismatch')
    expected = {x['record']['moratorium_id']: x for x in packet}
    require(len(expected) == len(packet), 'Duplicate packet ID')
    decisions = answers['decisions']
    require(isinstance(decisions, list), 'Decisions must be an array')
    seen, reviewed = set(), []
    fields = {'moratorium_id', 'record_sha256', 'recommendation', 'original_duration_text',
              'proposed_duration_kind', 'proposed_duration_days', 'rationale', 'evidence', 'limitations'}
    for decision in decisions:
        require(isinstance(decision, dict) and set(decision) == fields, 'Wrong decision fields')
        ident = decision['moratorium_id']
        require(ident in expected and ident not in seen, 'Unknown or duplicate decision ID')
        seen.add(ident)
        item = expected[ident]
        record = item['record']
        require(row_hash(record) == item['record_sha256'] == decision['record_sha256'], 'Row fingerprint mismatch')
        require(decision['original_duration_text'] == record['duration'], 'Original duration changed')
        recommendation = decision['recommendation']
        require(recommendation in {'calendar_term', 'keep_fixed_days', 'withhold'}, 'Unknown recommendation')
        proposed = decision['proposed_duration_kind'], decision['proposed_duration_days']
        target = {'calendar_term': ('calendar_term', ''),
                  'keep_fixed_days': ('fixed_days', record['duration_days']), 'withhold': (None, None)}
        require(proposed == target[recommendation], 'Recommendation changes unsupported fields or day count')
        require(isinstance(decision['rationale'], str) and decision['rationale'].strip(), 'Missing rationale')
        require(isinstance(decision['limitations'], list) and
                all(isinstance(x, str) and x.strip() for x in decision['limitations']), 'Invalid limitations')
        evidence = decision['evidence']
        require(isinstance(evidence, list) and (evidence or recommendation == 'withhold'),
                'Non-withheld recommendation needs inspected evidence')
        checks = []
        for reference in evidence:
            require(isinstance(reference, dict) and set(reference) ==
                    {'url', 'body_sha256', 'text_sha256', 'text_artifact', 'locator', 'support_scope'},
                    'Wrong evidence fields')
            require(all(isinstance(v, str) and v.strip() for v in reference.values()), 'Empty evidence value')
            matches = [p for p in item['retained_worker_evidence_proofs']
                       if all(p.get(k) == reference[k] for k in ('url', 'body_sha256', 'text_sha256', 'text_artifact'))]
            require(bool(matches), 'Evidence not tied to this record retained source version')
            text = Path(reference['text_artifact'])
            body = text.parent/(matches[0]['attempt_id']+'.private.body')
            require(sha(text.read_bytes()) == reference['text_sha256'], 'Retained text hash drift')
            require(sha(body.read_bytes()) == reference['body_sha256'], 'Retained body hash drift')
            checks.append({k: reference[k] for k in ('url', 'body_sha256', 'text_sha256')})
        reviewed.append({'moratorium_id': ident, 'record_sha256': decision['record_sha256'],
                         'recommendation': recommendation, 'verified_source_versions': checks,
                         'substantive_acceptance': 'not_assessed; coordinator must inspect original-term support'})
    require(seen == set(expected), 'Missing decision IDs')
    return reviewed


def audit(queue_path, inventory, runs):
    queue = json.loads(queue_path.read_text())
    raw = inventory.read_bytes()
    require(sha(raw) == queue['inventory_sha256'], 'Canonical inventory changed since queue freeze')
    with inventory.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    records = {r['moratorium_id']: r for r in rows}
    require(len(records) == len(rows), 'Duplicate canonical IDs')
    reports, assigned = [], set()
    for job in queue['jobs']:
        spec_path = Path(job['spec'])
        spec = json.loads(spec_path.read_text())
        require(spec['record_ids'] == list(job['record_fingerprints']), 'Spec/queue ID mismatch')
        require(not assigned.intersection(spec['record_ids']), 'Overlapping job assignments')
        assigned.update(spec['record_ids'])
        packet_path = Path(spec['owned_paths'][0])/'packet.json'
        require(sha(packet_path.read_bytes()) == spec['packet_sha256'], 'Packet bytes changed')
        packet = json.loads(packet_path.read_text())
        require([p['record']['moratorium_id'] for p in packet] == spec['record_ids'], 'Packet/spec ID mismatch')
        for item in packet:
            require(row_hash(item['record']) == item['record_sha256'] ==
                    job['record_fingerprints'][item['record']['moratorium_id']], 'Packet/queue row mismatch')
        for ident, fingerprint in job['record_fingerprints'].items():
            require(ident in records and row_hash(records[ident]) == fingerprint, 'Canonical row changed')
        status_path = runs/job['id']/'status.json'
        status = json.loads(status_path.read_text()) if status_path.exists() else {'state': 'not_started'}
        report = {'job_id': job['id'], 'execution_state': status['state'], 'assigned': len(packet),
                  'spec_sha256': sha(spec_path.read_bytes()), 'packet_sha256': spec['packet_sha256']}
        answers_path = packet_path.parent/'answers.json'
        if status['state'] not in {'finished', 'failed'}:
            report['return_state'] = 'await_terminal_execution'
        elif not answers_path.exists():
            report['return_state'] = 'missing_answers'
        else:
            reviewed = validate_return(packet, json.loads(answers_path.read_text()), job['id'], sha(raw))
            report.update(return_state='mechanically_valid_requires_coordinator_review',
                          answers_sha256=sha(answers_path.read_bytes()),
                          recommendations=dict(Counter(d['recommendation'] for d in reviewed)), records=reviewed)
        reports.append(report)
    require(len(assigned) == queue['candidate_count'], 'Queue candidate count mismatch')
    return {'scope': 'Mechanical input/return/source-byte verification only. No source quote interpretation, original-term acceptance, canonical edit or legal-force renewal.',
            'queue_sha256': sha(queue_path.read_bytes()), 'inventory_sha256': sha(raw), 'jobs': reports}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, default=Path('data/moratorium_inventory.csv'))
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.queue, args.inventory, args.runs)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(Counter(j['return_state'] for j in result['jobs'])))
