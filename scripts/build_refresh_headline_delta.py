"""Compare working data with a pinned baseline without overwriting historical reports."""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'dbaab04d84f8d679ba5a3d57bf45f32186109222'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def indexed(raw, key):
    reader = csv.DictReader(io.StringIO(raw.decode()))
    headers = reader.fieldnames
    if not headers or len(headers) != len(set(headers)) or any(not h for h in headers):
        raise ValueError('Invalid or duplicate CSV headers')
    if key not in headers:
        raise ValueError('Missing identity column: ' + key)
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) or not row[key] for row in rows):
        raise ValueError('Malformed CSV row or empty canonical ID')
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate canonical IDs: ' + key)
    return result


def schema_difference(before, after):
    old = next(csv.reader(io.StringIO(before.decode())))
    new = next(csv.reader(io.StringIO(after.decode())))
    return {'baseline_columns': old, 'current_columns': new,
            'added_columns': sorted(set(new)-set(old)),
            'removed_columns': sorted(set(old)-set(new)),
            'column_layout_changed': old != new}


def ballot_scope(root):
    projection = root / 'work/research/2026-11-05/ballot-census-review/canonical-projection-status.json'
    raw = projection.read_bytes()
    historical = json.loads(raw)
    snapshot = (root / 'data/expanded').resolve()
    tables = {p.stem: [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
              for p in sorted(snapshot.glob('*.jsonl'))}
    measures = {r['measure_id']: r for r in tables['ballot_measures']}
    if len(measures) != len(tables['ballot_measures']):
        raise ValueError('Duplicate current measure ID')
    frozen_ids = {g['canonical_measure_id'] for g in historical['groups']
                  if g.get('disposition') == 'scoped_canonical_publication'}
    if not frozen_ids <= measures.keys():
        raise ValueError('Frozen published identity missing from current snapshot')
    return {
        'snapshot': snapshot.name,
        'historical_projection': {'path': str(projection.relative_to(root)), 'sha256': sha(raw),
                                  'snapshot': historical['canonical_snapshot'], 'summary': historical['summary']},
        'current': {'proposal_measure_records': len(measures),
                    'lifecycle_counts': dict(collections.Counter(r['lifecycle'] for r in measures.values())),
                    'frozen_groups_with_retained_canonical_ids': len(frozen_ids),
                    'additional_record_ids_outside_frozen_publications': sorted(measures.keys() - frozen_ids)},
        'canonical_table_counts': {k: len(v) for k, v in tables.items()},
        'scope': 'Historical frozen census mapping is retained separately from current records, including non-voted proposals; neither is a complete national election census.'}


def build(root=ROOT, baseline=BASELINE):
    report = {'baseline_commit': git(root, 'rev-parse', baseline+'^{commit}').decode().strip(),
              'current_commit': git(root, 'rev-parse', 'HEAD').decode().strip(),
              'scope': 'Working CSV bytes versus a historical source baseline, not the last public release or complete freshness/legal-force verification.',
              'tables': {}}
    for name, filename, key, status in [
            ('local', 'moratorium_inventory.csv', 'moratorium_id', 'enacted_status'),
            ('state_policy', 'state_legislation.csv', 'policy_action_id', 'bill_status_category')]:
        path = Path('data') / filename
        before = git(root, 'show', baseline+':'+path.as_posix())
        after = (root/path).read_bytes()
        a, b = indexed(before, key), indexed(after, key)
        changed = [{'record_id': i, 'fields': {f: {'before': a[i].get(f), 'after': b[i].get(f)}
                    for f in sorted(a[i].keys() | b[i].keys()) if a[i].get(f) != b[i].get(f)}}
                   for i in sorted(a.keys() & b.keys()) if a[i] != b[i]]
        row = {'path': path.as_posix(), 'baseline_sha256': sha(before), 'current_sha256': sha(after),
               'schema': schema_difference(before, after),
               'before_total': len(a), 'after_total': len(b),
               'before_status_counts': dict(collections.Counter(r[status] for r in a.values())),
               'after_status_counts': dict(collections.Counter(r[status] for r in b.values())),
               'added_ids': sorted(b.keys()-a.keys()), 'removed_ids': sorted(a.keys()-b.keys()),
               'changed_existing_records': changed}
        if name == 'state_policy':
            row['before_record_type_counts'] = dict(collections.Counter(r['policy_instrument_type'] for r in a.values()))
            row['after_record_type_counts'] = dict(collections.Counter(r['policy_instrument_type'] for r in b.values()))
            row['record_type_scope'] = 'Policy record categories, not unique bills or enacted moratoria.'
        report['tables'][name] = row
    registry = root/'data/identities/legacy-moratoria.jsonl'
    if report['tables']['local']['removed_ids'] and not registry.is_file():
        raise ValueError('Missing identity registry for baseline ID removal')
    if registry.exists():
        from legacy_moratorium_identity import load_aliases
        inventory = root/'data/moratorium_inventory.csv'
        aliases = load_aliases(inventory, set(indexed(inventory.read_bytes(), 'moratorium_id')))
        removed = report['tables']['local']['removed_ids']
        if not all(i in aliases for i in removed):
            raise ValueError('Unexplained baseline ID removal')
        report['legacy_identity_retirements'] = {'path': str(registry.relative_to(root)), 'sha256': sha(registry.read_bytes()),
            'aliases': aliases, 'removed_baseline_ids': removed,
            'scope': 'Explicit duplicate retirements with original IDs and rows retained; historical counts not backcast.'}
    report['ballot_scope'] = ballot_scope(root)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default=BASELINE)
    parser.add_argument('--output', required=True, type=Path, help='New report path; existing reports are never overwritten')
    args = parser.parse_args()
    result = build(baseline=args.baseline)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: {f: v[f] for f in ('before_total', 'after_total', 'before_status_counts', 'after_status_counts')}
                      for k, v in result['tables'].items()}, indent=2))


if __name__ == '__main__':
    main()
