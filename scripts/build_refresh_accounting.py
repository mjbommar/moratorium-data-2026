#!/usr/bin/env python3
"""Inventory collection/edit accounting; never a source or legal-force acceptance gate."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collection_stage(job, outcome):
    if job is None:
        return 'queued'
    if job['cli_state'] not in ('finished', 'failed'):
        return 'running'
    if (job.get('checks') or 'schema_errors' not in job or job['schema_errors']
            or job.get('missing_ids') or job.get('extra_ids') or job.get('duplicate_ids')):
        return 'terminal_without_valid_complete_return'
    if outcome is None:
        return 'terminal_without_valid_complete_return'
    return 'returned_unresolved' if outcome == 'unresolvable' else 'returned_other_outcome'


def build(queue_path, audit_path, root=ROOT):
    queue = json.loads(queue_path.read_text())
    audit = json.loads(audit_path.read_text())
    audited = {j['job_id']: j for j in audit['jobs']}
    assignments = defaultdict(list)
    hashes = {'queue': sha(queue_path), 'return_audit': sha(audit_path),
              'job_specs': {}, 'terminal_answers': {}, 'packets': {}, 'apply_receipts': {}}
    for item in queue['jobs']:
        spec_path = Path(item['spec'])
        spec = json.loads(spec_path.read_text())
        hashes['job_specs'][item['id']] = sha(spec_path)
        table = spec.get('table')
        if table not in ('inventory', 'state_policy'):
            continue
        row = audited.get(item['id'])
        # Nonterminal artifacts are not finished returns, even if a file already exists.
        answers_path = Path(spec['owned_paths'][0]) / 'answers.json'
        answers = None
        if row and row['cli_state'] in ('finished', 'failed') and answers_path.exists():
            try:
                answers = json.loads(answers_path.read_text())
                hashes['terminal_answers'][item['id']] = sha(answers_path)
            except (ValueError, OSError):
                pass
        packet_path = Path(spec['owned_paths'][0]) / 'packet.json'
        packet = json.loads(packet_path.read_text()) if packet_path.exists() else []
        if packet_path.exists():
            hashes['packets'][item['id']] = sha(packet_path)
        public_keys = {r['policy_action_id']: r['state_abbrev'] + ':' + r['bill']
                       for r in packet} if table == 'state_policy' else {}
        key = 'moratorium_id' if table == 'inventory' else 'bill_key'
        decisions = {d.get(key): d.get('outcome') for d in answers.get('decisions', [])} if answers else {}
        for ident in spec['record_ids']:
            outcome = decisions.get(public_keys.get(ident, ident))
            assignments[(table, ident)].append({
                'job_id': item['id'], 'collection_stage': collection_stage(row, outcome),
                'worker_outcome': outcome,
                'job_mechanical_evidence_gate': row.get('mechanically_review_ready', False) if row else False,
            })
    edits = defaultdict(list)
    # A ledger change is not a complete reviewed/current record. Historical receipts are excluded.
    receipts = list((root / 'work/audit').glob('apply-20261105*.json'))
    receipts += list((root / 'work/audit').glob('apply-legislation-20261105*.json'))
    for receipt in sorted(receipts):
        data = json.loads(receipt.read_text())
        hashes['apply_receipts'][str(receipt.relative_to(root))] = sha(receipt)
        for change in data.get('changes', []):
            if change.get('moratorium_id'):
                edits[('inventory', change['moratorium_id'])].append(str(receipt.relative_to(root)))
            elif change.get('bill_key'):
                edits[('state_policy', change['bill_key'])].append(str(receipt.relative_to(root)))
    tables = {}
    for table, filename, id_key in [('inventory', 'moratorium_inventory.csv', 'moratorium_id'),
                                   ('state_policy', 'state_legislation.csv', 'policy_action_id')]:
        path = root / 'data' / filename
        hashes[filename] = sha(path)
        records = []
        for record in csv.DictReader(path.open()):
            ident = record[id_key]
            jobs = assignments.get((table, ident), [])
            if len(jobs) > 1:
                raise ValueError('Duplicate active queue assignment: ' + ident)
            pilot = ident in queue.get('completed_pilot_ids', {}).get(table, [])
            stage = jobs[0]['collection_stage'] if jobs else 'excluded_completed_pilot' if pilot else 'not_assigned_in_this_queue'
            ledger_key = ident if table == 'inventory' else record['state_abbrev'] + ':' + record['bill']
            receipts = sorted(set(edits.get((table, ledger_key), [])))
            records.append({'record_id': ident, 'state': record['state_abbrev'], 'collection_stage': stage,
                            'jobs': jobs, 'refresh_apply_receipts': receipts,
                            'editorial_stage': 'has_refresh_apply_change' if receipts else 'no_refresh_apply_change',
                            'legal_force_verification': 'not_assessed_by_this_mechanical_accounting'})
        if len({r['record_id'] for r in records}) != len(records):
            raise ValueError('Duplicate canonical IDs: ' + table)
        tables[table] = {'total': len(records),
                         'collection_counts': dict(Counter(r['collection_stage'] for r in records)),
                         'editorial_counts': dict(Counter(r['editorial_stage'] for r in records)),
                         'records': records}
    return {'observed_at': audit['observed_at'], 'input_sha256': hashes,
            'scope': 'Canonical inventory/state-policy collection and edit accounting. Each count dimension is disjoint and sums to its own table total. Job evidence gates are mechanical diagnostics, not substantive acceptance. Apply receipts show historical edits, not complete current rows or fresh legal force. Unassigned new records may have coordinator research outside this queue. This is not the completed freshness funnel required for release.',
            'job_counts': audit['job_states'], 'not_started_jobs': audit['not_started_jobs'],
            'tables': tables}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.queue, args.audit)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: {x: v[x] for x in ('total', 'collection_counts', 'editorial_counts')}
                      for k, v in result['tables'].items()}, indent=2))
