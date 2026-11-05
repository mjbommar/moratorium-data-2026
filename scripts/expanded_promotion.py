#!/usr/bin/env python3
"""Publish explicitly reviewed expanded tables as an immutable atomic snapshot.

Identity, schema validation and factual review are separate gates. No search or
model output is promoted merely because it validates. Dry-run is the default.
"""
import argparse
from contextlib import ExitStack, nullcontext
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

from expanded_data import IDS, validate
from expanded_identity import Registry, read_events, encode
from audit_refresh_returns import evidence_index, audit_expanded_evidence

DOMAIN = {'jurisdictions', 'elections', 'ballot_measures', 'measure_provisions',
          'measure_results', 'local_restrictions', 'instrument_events', 'measure_instrument_links'}
IMMUTABLE = set(IDS) - {'jurisdictions', 'elections', 'ballot_measures', 'measure_provisions',
                         'local_restrictions'}
ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def serialized(rows):
    return {table: ''.join(encode(row)+'\n' for _, row in sorted(records.items())).encode()
            for table, records in sorted(rows.items())}


def fingerprint(files):
    return digest(encode({name: digest(raw) for name, raw in sorted(files.items())}).encode())


def read_snapshot(path):
    """Resolve the pointer once so a reader cannot mix publication generations."""
    resolved = path.resolve(strict=True)
    return {name: (resolved/(name+'.jsonl')).read_bytes() for name in IDS}


def review_gate(rows, registry, plan, proofs, previous):
    reviews = {}
    for review in plan['record_reviews']:
        require(set(review) == {'table', 'id', 'record_sha256', 'previous_sha256',
                                'accepted_fields', 'unresolved_fields', 'publication'},
                'Invalid record review fields')
        key = review['table'], review['id']
        require(key not in reviews, 'Duplicate record review')
        reviews[key] = review
    expected = {(table, key) for table, records in rows.items() for key in records}
    require(set(reviews) == expected, 'Every snapshot record needs exactly one pinned publication review')
    verified = {p['claim_id'] for p in proofs if p['evidence_verified']}
    require(verified == set(rows['claims']), 'Every claim needs independently verified text or visual evidence')
    decisions = list(rows['review_decisions'].values())
    superseded = {d['supersedes_id'] for d in decisions if d['supersedes_id']}
    for table, records in rows.items():
        for key, record in records.items():
            review = reviews[table, key]
            require(review['record_sha256'] == digest(encode(record).encode()), 'Record fingerprint changed')
            old = previous[table].get(key)
            require(review['previous_sha256'] == (digest(encode(old).encode()) if old else None),
                    'Record baseline changed')
            if old and table in IMMUTABLE:
                require(record == old, 'Historical observations, claims and decisions are immutable')
            entity = registry.entities.get(key)
            require(entity and entity['table'] == table, 'Record lacks allocated identity: '+table+'/'+key)
            require(registry.resolve(key) == {key} or record == old, 'Ambiguous or retired identity')
            require(review['publication'] in {'public_record', 'reviewed_excerpt', 'reviewed_metadata'},
                    'Explicit public rights disposition required')
            accepted, unresolved = review['accepted_fields'], review['unresolved_fields']
            require(isinstance(accepted, list) and isinstance(unresolved, list)
                    and len(set(accepted)) == len(accepted) and len(set(unresolved)) == len(unresolved)
                    and not set(accepted) & set(unresolved), 'Invalid field review partition')
            fields = set(record) - {IDS[table], 'schema_version'}
            require(set(accepted) | set(unresolved) == fields, 'Every field requires an explicit disposition')
            for field in unresolved:
                value = record[field]
                require(value is None or value in ('unknown', 'unresolved') or value == [] or value == {},
                        'Unresolved field contains a factual assertion: '+table+'/'+field)
            if table not in DOMAIN:
                continue
            for field in accepted:
                if field == 'claim_ids':
                    continue
                live = [d for d in decisions if d['target'] == {'table': table, 'id': key}
                        and d['scope'] == field and d['decision_id'] not in superseded]
                require(len(live) == 1 and live[0]['disposition'] == 'accepted',
                        'Field lacks current scoped acceptance: '+table+'/'+key+'/'+field)
                supporting = [rows['claims'][cid] for cid in live[0]['claim_ids']]
                require(any(c['predicate'] in (field, 'source_excerpt:'+field) for c in supporting),
                        'Field acceptance lacks predicate-scoped evidence: '+field)
    for table, records in previous.items():
        require(set(records) <= set(rows[table]), 'Records cannot silently disappear: '+table)


def publish(destination, candidate, registry_path, plan, evidence_directories,
            apply=False, visual_reviews=None, moratoria=None, state_actions=None):
    require(set(plan) == {'schema_version', 'expected_sha256', 'registry_sha256', 'snapshot_sha256',
                          'reviewer', 'reviewed_at', 'rationale', 'record_reviews'}, 'Invalid plan fields')
    require(plan['schema_version'] == '1.0.0', 'Unsupported plan version')
    require(all(isinstance(plan[k], str) and plan[k].strip() for k in ('reviewer', 'rationale')),
            'Explicit reviewer and rationale required')
    require(datetime.fromisoformat(plan['reviewed_at'].replace('Z', '+00:00')).tzinfo is not None,
            'Review timestamp must include timezone')
    # Canonical publication only creates/swaps a symlink; it never replaces a directory.
    require(not destination.exists() or destination.is_symlink(), 'Destination must be absent or a snapshot pointer')
    require(not destination.is_symlink() or destination.exists(), 'Dangling snapshot pointer')
    if apply:
        destination.parent.mkdir(parents=True, exist_ok=True)
    context = (destination.parent/('.'+destination.name+'.lock')).open('a+b') if apply else nullcontext()
    with ExitStack() as stack:
        lock = stack.enter_context(context)
        if apply:
            fcntl.flock(lock, fcntl.LOCK_EX)
            identity_lock = stack.enter_context(registry_path.with_suffix(registry_path.suffix+'.lock').open('a+b'))
            fcntl.flock(identity_lock, fcntl.LOCK_SH)
        registry_raw = registry_path.read_bytes()
        require(digest(registry_raw) == plan['registry_sha256'], 'Identity registry changed since review')
        registry = Registry(read_events(registry_raw))
        errors, rows = validate(candidate.resolve(), moratoria, state_actions)
        require(not errors, 'Invalid candidate: '+'; '.join(errors))
        files = serialized(rows); target_hash = fingerprint(files)
        require(target_hash == plan['snapshot_sha256'], 'Candidate snapshot changed since review')
        current_files = read_snapshot(destination) if destination.exists() else None
        current_hash = fingerprint(current_files) if current_files else None
        # An exact replay verifies retained bytes and the original publication plan.
        replay = current_hash == target_hash
        require(replay or current_hash == plan['expected_sha256'], 'Snapshot changed since review')
        previous = {table: {} for table in IDS}
        if current_files and not replay:
            for table, raw in current_files.items():
                previous[table] = {r[IDS[table]]: r for r in map(json.loads, raw.decode().splitlines())}
        if replay:
            require(current_files == files, 'Published snapshot bytes are not canonical')
            retained = json.loads((destination.resolve()/'publication.json').read_text())
            require(retained['plan_sha256'] == digest(encode(plan).encode()), 'Replay plan differs from publication')
            # The originally applied baseline was already validated; do not reinterpret it.
            return {'state': 'already_applied', 'sha256': target_hash}
        index = {}
        for directory in evidence_directories:
            entries, issues, _ = evidence_index(directory)
            require(not issues, 'Evidence integrity errors: '+str(issues))
            for url, versions in entries.items():
                index.setdefault(url, []).extend(versions)
        issues, proofs = audit_expanded_evidence(rows, index, visual_reviews)
        require(not issues, 'Evidence version errors: '+str(issues))
        review_gate(rows, registry, plan, proofs, previous)
        result = {'state': 'ready', 'sha256': target_hash,
                  'records': {table: len(records) for table, records in rows.items()}}
        if not apply:
            return result
        snapshots = destination.parent/(destination.name+'-snapshots')
        snapshots.mkdir(exist_ok=True)
        final = snapshots/target_hash
        require(not final.exists(), 'Unreferenced snapshot exists; inspect recovery inputs before retry')
        with tempfile.TemporaryDirectory(prefix='.staging-', dir=snapshots) as temporary:
            stage = Path(temporary)/'snapshot'; stage.mkdir()
            for table, raw in files.items():
                with (stage/(table+'.jsonl')).open('wb') as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
            receipt = {'schema_version': '1.0.0', 'sha256': target_hash,
                       'plan_sha256': digest(encode(plan).encode()), 'plan': plan,
                       'evidence': [{k: v for k, v in proof.items() if k != 'verified_text_artifact'} for proof in proofs]}
            with (stage/'publication.json').open('w') as f:
                json.dump(receipt, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
            fsync_directory(stage)
            stage.rename(final); fsync_directory(snapshots)
        # A unique sibling pointer lets concurrent readers retain a complete generation.
        with tempfile.TemporaryDirectory(prefix='.pointer-', dir=destination.parent) as temporary:
            pointer = Path(temporary)/'current'
            pointer.symlink_to(os.path.relpath(final, destination.parent))
            pointer.replace(destination)
        fsync_directory(destination.parent)
        return dict(result, state='applied')


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--registry', type=Path, default=ROOT/'data/identities/expanded.jsonl')
    p.add_argument('--destination', type=Path, default=ROOT/'data/expanded')
    p.add_argument('--evidence-directory', action='append', type=Path, default=[])
    p.add_argument('--visual-reviews', type=Path)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    visual = None
    if a.visual_reviews:
        visual = {}
        for entry in json.loads(a.visual_reviews.read_text()):
            receipt = json.loads(Path(entry).read_text())
            visual[receipt['claim_id']] = receipt
    print(json.dumps(publish(a.destination, a.candidate, a.registry, json.loads(a.plan.read_text()),
                             a.evidence_directory, a.apply, visual, ROOT/'data/moratorium_inventory.csv',
                             ROOT/'data/state_legislation.csv'), indent=2))
