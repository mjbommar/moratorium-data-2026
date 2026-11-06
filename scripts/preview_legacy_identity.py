#!/usr/bin/env python3
"""Preview explicitly reviewed legacy identity mappings; never mutate authority.

This checks frozen records and mapping structure, not legal identity evidence.
Source interpretation, field reconciliation and consumer integration are separate.
"""
import argparse
from collections import Counter
from datetime import datetime
import csv
import hashlib
import io
import json
from pathlib import Path
import re


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def row_hash(row):
    return sha(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def preview(raw, plan):
    require(set(plan) == {'schema_version', 'inventory_sha256', 'reviewer', 'reviewed_at', 'merges'},
            'Wrong plan fields')
    require(plan['schema_version'] == 'legacy-identity-preview-1', 'Unsupported plan version')
    require(sha(raw) == plan['inventory_sha256'], 'Inventory changed since identity review')
    require(isinstance(plan['reviewer'], str) and plan['reviewer'].strip(), 'Explicit reviewer required')
    require(datetime.fromisoformat(plan['reviewed_at'].replace('Z', '+00:00')).tzinfo is not None,
            'Timezone required')
    records = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    rows = {r['moratorium_id']: r for r in records}
    require(len(rows) == len(records), 'Duplicate raw IDs')
    require(isinstance(plan['merges'], list) and plan['merges'], 'Explicit mapping required')
    aliases = {}
    for merge in plan['merges']:
        require(set(merge) == {'canonical_id', 'alias_ids', 'record_sha256', 'evidence', 'rationale'},
                'Wrong mapping fields')
        canonical = merge['canonical_id']
        members = merge['alias_ids']
        require(isinstance(members, list) and members and len(members) == len(set(members)),
                'Explicit unique alias IDs required')
        require(canonical in rows and canonical not in members and all(m in rows for m in members),
                'Unknown ID or self alias')
        require(set(merge['record_sha256']) == {canonical, *members}, 'Exact reviewed member fingerprints required')
        for ident, fingerprint in merge['record_sha256'].items():
            require(row_hash(rows[ident]) == fingerprint, 'Reviewed record fingerprint changed')
        require(isinstance(merge['rationale'], str) and merge['rationale'].strip(), 'Mapping rationale required')
        require(isinstance(merge['evidence'], list) and merge['evidence'], 'Identity evidence required')
        for evidence in merge['evidence']:
            require(set(evidence) == {'url', 'body_sha256', 'locator'} and
                    isinstance(evidence['url'], str) and evidence['url'].startswith(('https://', 'http://')) and
                    isinstance(evidence['body_sha256'], str) and re.fullmatch('[0-9a-f]{64}', evidence['body_sha256']) and
                    isinstance(evidence['locator'], str) and evidence['locator'].strip(), 'Invalid evidence reference')
        for member in members:
            require(member not in aliases, 'Alias assigned more than once')
            aliases[member] = canonical

    def resolve(ident):
        seen = set()
        while ident in aliases:
            require(ident not in seen, 'Alias cycle')
            seen.add(ident)
            ident = aliases[ident]
        return ident

    resolved = {ident: resolve(ident) for ident in rows}
    roots = set(resolved.values())
    return {'state': 'preview_only_not_applied', 'inventory_sha256': sha(raw),
            'scope': 'Explicit mapping structure and frozen-row verification only. No identity evidence reauthentication, field merging, ID deletion, canonical publication, count change or renewed current-force acceptance.',
            'raw_retained_records': len(records), 'projected_canonical_records': len(roots),
            'projected_aliases': {k: resolved[k] for k in sorted(aliases)},
            'projected_status_counts': dict(sorted(Counter(rows[k]['enacted_status'] for k in roots).items())),
            'requirements_before_application': ['Compatible ID/alias persistence and lookup',
                'Explicit survivor field reconciliation without unreviewed project attribution or operative dates',
                'Consistent public counts, maps, exports, baseline comparisons, release assets and consumer handling']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('data/moratorium_inventory.csv'))
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    plan_raw = args.plan.read_bytes()
    result = preview(args.inventory.read_bytes(), json.loads(plan_raw))
    result['plan_sha256'] = sha(plan_raw)
    print(json.dumps(result, indent=2))
