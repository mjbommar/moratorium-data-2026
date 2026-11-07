#!/usr/bin/env python3
"""Check retained public snapshot bytes, identity history and review receipts offline.

This verifies internal publication consistency. It does not reacquire sources,
repeat visual judgments, authenticate reviewers or establish current legal force.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from expanded_promotion import sealed_generation, IDS, ROOT, digest, encode, fingerprint, read_snapshot, require, review_gate, validate_plan
from expanded_data import validate
from expanded_identity import Registry, read_events

HASH = re.compile(r'[0-9a-f]{64}')


def check(destination, registry_path, moratoria=None, state_actions=None, *, generation_path=None):
    require(destination.is_symlink(), 'Canonical expanded path must be a snapshot pointer')
    require(not destination.readlink().is_absolute(), 'Snapshot pointer must be relative for portable restore')
    target = destination.resolve(strict=True) if generation_path is None else generation_path.resolve(strict=True)
    snapshots = (destination.parent/(destination.name+'-snapshots')).resolve(strict=True)
    require(destination.resolve(strict=True).parent == snapshots, 'Snapshot pointer escapes its generation directory')
    require(target.parent == snapshots, 'Selected generation escapes its generation directory')
    raw = registry_path.read_bytes()
    Registry(read_events(raw))  # Validate all history, including later append-only decisions.
    prefixes = {digest(b''): 0}
    state = hashlib.sha256(); offset = 0
    for line in raw.splitlines(keepends=True):
        state.update(line); offset += len(line)
        prefixes[state.hexdigest()] = offset
    visited = set()

    def generation(path):
        require(path.parent == snapshots and HASH.fullmatch(path.name), 'Invalid generation path')
        require(path.is_dir() and not path.is_symlink(), 'Generation must be a retained directory')
        require(path.name not in visited, 'Cyclic snapshot history')
        visited.add(path.name)
        require({p.stem for p in path.glob('*.jsonl')} == set(IDS), 'Snapshot table set differs from contract')
        require(all((path/(t+'.jsonl')).is_file() and not (path/(t+'.jsonl')).is_symlink() for t in IDS),
                'Snapshot tables must be retained regular files')
        files = read_snapshot(path)
        actual = fingerprint(files)
        receipt_path = path/'publication.json'
        require(receipt_path.is_file() and not receipt_path.is_symlink(), 'Publication receipt must be retained')
        receipt_raw=receipt_path.read_bytes()
        receipt = json.loads(receipt_raw)
        require(set(receipt) == {'schema_version', 'sha256', 'plan_sha256', 'plan', 'evidence'}
                and receipt['schema_version'] == '1.0.0', 'Invalid publication receipt')
        plan = receipt['plan']
        validate_plan(plan)
        expected_name=sealed_generation(actual,digest(receipt_raw)) if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3') else actual
        require(path.name==expected_name,'Publication/table fingerprint differs from generation name')
        require(receipt['sha256'] == actual == plan['snapshot_sha256'], 'Receipt snapshot fingerprint differs')
        require(receipt['plan_sha256'] == digest(encode(plan).encode()), 'Publication plan fingerprint differs')
        require(plan['registry_sha256'] in prefixes, 'Published identity baseline is not retained registry history')
        prefix = prefixes[plan['registry_sha256']]
        historical = Registry(read_events(raw[:prefix]))
        errors, rows = validate(path, moratoria, state_actions,
                                profile=plan.get('validation_profile',{}).get('name','1.0.0'))
        require(not errors, 'Invalid published tables: '+'; '.join(errors))
        proofs = receipt['evidence']
        require(isinstance(proofs, list) and len(proofs) == len(rows['claims'])
                and {p['claim_id'] for p in proofs} == set(rows['claims']), 'Publication proof coverage differs')
        for proof in proofs:
            claim = rows['claims'][proof['claim_id']]
            require(proof['source_document_id'] == claim['source_document_id'], 'Proof source differs from claim')
            require(proof['evidence_verified'] is True and
                    (proof['quote_located'] is True or proof['visual_verified'] is True),
                    'Publication proof lacks verified support')
            if proof['quote_located']:
                span = proof['verified_span']
                require(isinstance(claim['quote'], str) and bool(claim['quote'])
                        and isinstance(span, list) and len(span) == 2
                        and all(type(n) is int for n in span) and 0 <= span[0] < span[1],
                        'Invalid retained quote location')
        previous = {t: {} for t in IDS}
        previous_reviewed_at=None
        if plan['expected_sha256'] is not None:
            require(isinstance(plan['expected_sha256'], str) and HASH.fullmatch(plan['expected_sha256']),
                    'Invalid predecessor fingerprint')
            prior_path=snapshots/plan['expected_sha256']
            if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3'):
                expected_receipt=plan['expected_publication_sha256']
                choices=[prior_path,snapshots/sealed_generation(plan['expected_sha256'],expected_receipt)]
                choices=[p for p in choices if (p/'publication.json').is_file() and digest((p/'publication.json').read_bytes())==expected_receipt]
                require(len(choices)==1,'Pinned predecessor publication receipt missing or changed')
                prior_path=choices[0]
            previous = generation(prior_path)
            prior=json.loads((prior_path/'publication.json').read_text())['plan']
            previous_reviewed_at=prior['reviewed_at']
            if prior.get('validation_profile',{}).get('name')=='1.0.3':
                require(plan.get('validation_profile',{}).get('name')=='1.0.3','Cannot downgrade condition publication profile')
            if prior.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3'):
                require(plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3'),'Cannot downgrade event-validity publication profile')
        review_gate(rows, historical, plan, proofs, previous, previous_reviewed_at)
        return rows

    rows = generation(target)
    return {'state': 'consistent', 'snapshot_sha256': target.name,
            'generations_checked': len(visited), 'records': {t: len(v) for t, v in rows.items()},
            'scope': 'Offline publication/receipt consistency only; no source reacquisition, renewed factual acceptance or current-force confirmation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=ROOT/'data/expanded')
    parser.add_argument('--registry', type=Path, default=ROOT/'data/identities/expanded.jsonl')
    args = parser.parse_args()
    print(json.dumps(check(args.destination, args.registry, ROOT/'data/moratorium_inventory.csv',
                           ROOT/'data/state_legislation.csv'), indent=2))
