#!/usr/bin/env python3
"""Explicit, recoverable duplicate retirement with permanent legacy-ID lookup.

CSV replacement is atomic. CSV/registry publication is a Git-tree transaction;
an interrupted local two-file application is resumed by exact pre/post hashes.
No fields are merged and no identity is inferred from names or dates.
"""
import argparse
import csv
from datetime import datetime
import io
import json
import os
import re
from pathlib import Path
import tempfile
from uuid import UUID

from preview_legacy_identity import preview, require, row_hash, sha


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def registry_path(inventory):
    return inventory.parent/'identities/legacy-moratoria.jsonl'


def read_registry(raw):
    aliases, events = {}, set()
    prefix = b''
    for line in raw.splitlines(keepends=True):
        require(line.endswith(b'\n'), 'Registry must end with newline')
        event = json.loads(line)
        require(set(event) == {'schema_version', 'event_id', 'action', 'alias_id', 'canonical_id',
                'retired_record', 'retired_record_sha256', 'canonical_record', 'canonical_record_sha256',
                'inventory_before_sha256', 'inventory_after_sha256', 'previous_registry_sha256',
                'reviewer', 'reviewed_at', 'rationale', 'evidence'}, 'Wrong registry event fields')
        require(event['schema_version'] == 'legacy-moratorium-identity-1' and
                event['action'] == 'retire_duplicate', 'Unsupported registry event')
        alias, target = event['alias_id'], event['canonical_id']
        require(isinstance(alias, str) and alias and isinstance(target, str) and target and alias != target,
                'Invalid identity mapping')
        require(event['event_id'] not in events and alias not in aliases, 'Duplicate identity event or alias')
        require(str(UUID(event['event_id'])) == event['event_id'], 'Opaque canonical event UUID required')
        require(datetime.fromisoformat(event['reviewed_at'].replace('Z', '+00:00')).tzinfo is not None,
                'Reviewed timestamp requires timezone')
        for field in ('retired_record_sha256', 'canonical_record_sha256', 'inventory_before_sha256',
                      'inventory_after_sha256', 'previous_registry_sha256'):
            require(isinstance(event[field], str) and re.fullmatch('[0-9a-f]{64}', event[field]), 'Invalid identity fingerprint')
        require(event['previous_registry_sha256'] == sha(prefix), 'Registry history fingerprint changed')
        require(event['retired_record']['moratorium_id'] == alias and
                row_hash(event['retired_record']) == event['retired_record_sha256'], 'Retired observation changed')
        require(event['canonical_record']['moratorium_id'] == target and
                row_hash(event['canonical_record']) == event['canonical_record_sha256'], 'Canonical preimage changed')
        # Reuse explicit reviewer/date/evidence validation without pretending to
        # authenticate the legal interpretation or subsequent force of the act.
        require(event['reviewer'] and event['reviewed_at'] and event['rationale'] and event['evidence'],
                'Missing reviewed identity provenance')
        aliases[alias] = target
        events.add(event['event_id'])
        prefix += line
    for start in aliases:
        resolve(start, aliases)
    return aliases


def resolve(ident, aliases):
    seen = set()
    while ident in aliases:
        require(ident not in seen, 'Alias cycle')
        seen.add(ident)
        ident = aliases[ident]
    return ident


def load_aliases(inventory, current_ids):
    path = registry_path(inventory)
    aliases = read_registry(path.read_bytes()) if path.exists() else {}
    require(not set(aliases).intersection(current_ids), 'Retired alias still in current CSV; recover identity transaction')
    require(all(resolve(a, aliases) in current_ids for a in aliases), 'Alias has no surviving current target')
    return aliases


def lookup(inventory, ident):
    with inventory.open(newline='', encoding='utf-8-sig') as stream:
        rows = {r['moratorium_id']: r for r in csv.DictReader(stream)}
    aliases = load_aliases(inventory, set(rows))
    target = resolve(ident, aliases)
    require(target in rows, 'Unknown moratorium ID')
    return {'requested_id': ident, 'canonical_id': target, 'is_alias': ident != target, 'record': rows[target]}


def atomic_write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.'+path.name+'-', dir=path.parent)
    try:
        os.fchmod(fd, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if os.path.exists(name): os.unlink(name)


def retire(inventory, registry, plan, apply=False):
    require(set(plan) == {'schema_version', 'preview_plan', 'event_id', 'expected_registry_sha256',
                         'inventory_after_sha256', 'retired_record'}, 'Wrong retirement plan fields')
    require(plan['schema_version'] == 'legacy-moratorium-retirement-1', 'Unsupported retirement plan')
    reviewed = plan['preview_plan']
    require(len(reviewed['merges']) == 1 and len(reviewed['merges'][0]['alias_ids']) == 1,
            'One explicit duplicate per retirement transaction')
    merge = reviewed['merges'][0]
    alias, target = merge['alias_ids'][0], merge['canonical_id']
    require(plan['retired_record']['moratorium_id'] == alias and
            row_hash(plan['retired_record']) == merge['record_sha256'][alias], 'Retired preimage differs from review')
    current = inventory.read_bytes()
    current_rows = {r['moratorium_id']: r for r in csv.DictReader(io.StringIO(current.decode('utf-8-sig')))}
    registry_raw = registry.read_bytes() if registry.exists() else b''
    read_registry(registry_raw)
    before_registry = plan['expected_registry_sha256']
    retained = [json.loads(line) for line in registry_raw.splitlines() if
                json.loads(line)['event_id'] == plan['event_id']]
    if retained:
        event = retained[0]
        expected = {'alias_id': alias, 'canonical_id': target, 'retired_record': plan['retired_record'],
                    'retired_record_sha256': merge['record_sha256'][alias],
                    'canonical_record_sha256': merge['record_sha256'][target],
                    'inventory_before_sha256': reviewed['inventory_sha256'],
                    'inventory_after_sha256': plan['inventory_after_sha256'],
                    'previous_registry_sha256': before_registry, 'reviewer': reviewed['reviewer'],
                    'reviewed_at': reviewed['reviewed_at'], 'rationale': merge['rationale'], 'evidence': merge['evidence']}
        require(all(event[k] == v for k, v in expected.items()), 'Replay event differs from reviewed transaction')
        aliases = load_aliases(inventory, set(current_rows))
        require(resolve(alias, aliases) == resolve(target, aliases), 'Historical alias resolution changed incompatibly')
        return {'state': 'already_applied', 'alias_id': alias, 'canonical_id': resolve(alias, aliases),
                'inventory_after_sha256': event['inventory_after_sha256'],
                'current_inventory_sha256': sha(current), 'registry_after_sha256': sha(registry_raw),
                'scope': 'Exact retained identity event matched; later survivor edits are not rewritten or reaccepted.'}
    require(target in current_rows and row_hash(current_rows[target]) == merge['record_sha256'][target],
            'Canonical preimage differs from review')
    # Exact replay/resume: recover registry publication if CSV already replaced.
    if sha(current) == plan['inventory_after_sha256']:
        old_registry = registry_raw
        lines = registry_raw.splitlines(keepends=True)
        if lines and json.loads(lines[-1])['event_id'] == plan['event_id']:
            old_registry = b''.join(lines[:-1])
        require(sha(old_registry) == before_registry, 'Registry changed since review')
        state = 'already_applied' if old_registry != registry_raw else 'resume_registry'
    else:
        preview(current, reviewed)
        require(sha(registry_raw) == before_registry, 'Registry changed since review')
        old_registry, state = registry_raw, 'ready'
    event = {'schema_version': 'legacy-moratorium-identity-1', 'event_id': plan['event_id'],
             'action': 'retire_duplicate', 'alias_id': alias, 'canonical_id': target,
             'retired_record': plan['retired_record'], 'retired_record_sha256': merge['record_sha256'][alias],
             'canonical_record': current_rows[target],
             'canonical_record_sha256': merge['record_sha256'][target],
             'inventory_before_sha256': reviewed['inventory_sha256'],
             'inventory_after_sha256': plan['inventory_after_sha256'],
             'previous_registry_sha256': before_registry, 'reviewer': reviewed['reviewer'],
             'reviewed_at': reviewed['reviewed_at'], 'rationale': merge['rationale'], 'evidence': merge['evidence']}
    desired_registry = old_registry+(encode(event)+'\n').encode()
    aliases = read_registry(desired_registry)
    if state == 'already_applied':
        require(registry_raw == desired_registry, 'Replay event differs from reviewed transaction')
    if state == 'ready':
        reader = csv.DictReader(io.StringIO(current.decode('utf-8-sig')))
        rows, fields = list(reader), reader.fieldnames
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(r for r in rows if r['moratorium_id'] != alias)
        desired_csv = output.getvalue().encode()
        require(sha(desired_csv) == plan['inventory_after_sha256'], 'Retirement output differs from reviewed hash')
    else:
        desired_csv = current
    ids = {r['moratorium_id'] for r in csv.DictReader(io.StringIO(desired_csv.decode()))}
    require(alias not in ids and resolve(alias, aliases) in ids, 'Missing surviving canonical target')
    result = {'state': state, 'alias_id': alias, 'canonical_id': resolve(alias, aliases),
              'inventory_after_sha256': sha(desired_csv), 'registry_after_sha256': sha(desired_registry),
              'scope': 'One reviewed duplicate retired; all survivor fields unchanged. Alias/preimage retained; no legal-force renewal.'}
    if apply and state != 'already_applied':
        # Each file replacement is atomic. Exact pre/post fingerprints recover a
        # failure between the two writes; publish both together in one Git tree.
        if state == 'ready': atomic_write(inventory, desired_csv)
        atomic_write(registry, desired_registry)
        load_aliases(inventory, ids)
        result['state'] = 'applied'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('data/moratorium_inventory.csv'))
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--lookup')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if bool(args.plan) == bool(args.lookup): parser.error('Choose exactly one of --plan or --lookup')
    if args.lookup and args.apply: parser.error('--apply requires --plan')
    result = (lookup(args.inventory, args.lookup) if args.lookup else
              retire(args.inventory, registry_path(args.inventory), json.loads(args.plan.read_text()), args.apply))
    print(json.dumps(result, indent=2))
