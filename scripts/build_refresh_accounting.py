#!/usr/bin/env python3
"""Inventory collection/edit accounting; never a source or legal-force acceptance gate."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import datetime as dt
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


def receipt_paths(root, dates):
    for value in dates:
        if len(value)!=8 or not value.isdigit():raise ValueError('Receipt dates must be YYYYMMDD')
        dt.datetime.strptime(value,'%Y%m%d')
    return sorted({p for value in dates for pattern in
                   ('apply-'+value+'*.json','apply-legislation-'+value+'*.json')
                   for p in (root/'work/audit').glob(pattern)})


def policy_aliases(receipts):
    aliases={}
    for receipt,data in receipts:
        for change in data.get('changes',[]):
            key=change.get('bill_key')
            if key and change.get('column')=='bill' and isinstance(change.get('after'),str):
                state,before=key.split(':',1)
                if change.get('before')!=before:raise ValueError('Bill rename baseline differs from ledger key')
                target=state+':'+change['after']
                if key!=target:
                    if key in aliases and aliases[key]!=target:raise ValueError('Conflicting policy ledger aliases')
                    aliases[key]=target
    for key in aliases:resolve_policy_alias(key,aliases)
    return aliases


def resolve_policy_alias(key, aliases):
    seen=set()
    while key in aliases:
        if key in seen:raise ValueError('Cyclic policy ledger aliases')
        seen.add(key);key=aliases[key]
    return key


def field_lineage(record, changes):
    latest={}
    for receipt,change in changes:
        column=change.get('column')
        if column in record and 'after' in change:
            latest[column]=(receipt,change['after'])
    result=[]
    for column,(receipt,value) in sorted(latest.items()):
        after='' if value is None else str(value)
        current=record[column]
        result.append({'column':column,'last_receipt':receipt,
                       'last_applied_value_sha256':hashlib.sha256(after.encode()).hexdigest(),
                       'current_value_sha256':hashlib.sha256(current.encode()).hexdigest(),
                       'current_matches_last_applied_value':after==current})
    return result


def build(queue_path, audit_path, root=ROOT, receipt_dates=('20261105',), include_fields=False):
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
    receipts = receipt_paths(root, receipt_dates)
    field_edits = defaultdict(list)
    loaded_receipts=[(p,json.loads(p.read_text())) for p in receipts]
    aliases=policy_aliases(loaded_receipts)
    for receipt,data in loaded_receipts:
        hashes['apply_receipts'][str(receipt.relative_to(root))] = sha(receipt)
        for change in data.get('changes', []):
            if change.get('moratorium_id'):
                edits[('inventory', change['moratorium_id'])].append(str(receipt.relative_to(root)))
                field_edits[('inventory', change['moratorium_id'])].append((str(receipt.relative_to(root)),change))
            elif change.get('bill_key'):
                edits[('state_policy', resolve_policy_alias(change['bill_key'],aliases))].append(str(receipt.relative_to(root)))
                field_edits[('state_policy', resolve_policy_alias(change['bill_key'],aliases))].append((str(receipt.relative_to(root)),change))
    tables = {}
    for table, filename, id_key in [('inventory', 'moratorium_inventory.csv', 'moratorium_id'),
                                   ('state_policy', 'state_legislation.csv', 'policy_action_id')]:
        path = root / 'data' / filename
        hashes[filename] = sha(path)
        records = []
        with path.open(newline='', encoding='utf-8') as stream:
            input_records=list(csv.DictReader(stream))
        for record in input_records:
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
            if include_fields:
                records[-1]['applied_field_lineage']=field_lineage(record,field_edits.get((table,ledger_key),[]))
        if len({r['record_id'] for r in records}) != len(records):
            raise ValueError('Duplicate canonical IDs: ' + table)
        tables[table] = {'total': len(records),
                         'collection_counts': dict(Counter(r['collection_stage'] for r in records)),
                         'editorial_counts': dict(Counter(r['editorial_stage'] for r in records)),
                         'records': records}
        if include_fields:
            fields=[field for record in records for field in record['applied_field_lineage']]
            tables[table]['field_lineage_counts']={
                'last_applied_field_values':len(fields),
                'matching_current_values':sum(field['current_matches_last_applied_value'] for field in fields),
                'differing_current_values':sum(not field['current_matches_last_applied_value'] for field in fields)}
    return {'observed_at': audit['observed_at'], 'receipt_dates': list(receipt_dates),
            'field_lineage_included': include_fields, 'explicit_policy_ledger_aliases': aliases, 'input_sha256': hashes,
            'scope': 'Canonical inventory/state-policy collection and edit accounting. Each count dimension is disjoint and sums to its own table total. Job evidence gates are mechanical diagnostics, not substantive acceptance. Apply receipts show historical edits, not complete current rows or fresh legal force. Unassigned new records may have coordinator research outside this queue. This is not the completed freshness funnel required for release.',
            'job_counts': audit['job_states'], 'not_started_jobs': audit['not_started_jobs'],
            'tables': tables}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--receipt-date', action='append', help='YYYYMMDD; repeat explicitly. Default retains historical November5only.')
    parser.add_argument('--include-fields', action='store_true', help='Report last applied field fingerprints; not substantive acceptance.')
    args = parser.parse_args()
    result = build(args.queue, args.audit, receipt_dates=args.receipt_date or ('20261105',), include_fields=args.include_fields)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: {x: v[x] for x in ('total', 'collection_counts', 'editorial_counts')}
                      for k, v in result['tables'].items()}, indent=2))
