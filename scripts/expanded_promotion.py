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

from expanded_data import IDS, validate, profile_path
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


def publication_proofs(proofs):
    return [{k:v for k,v in p.items() if k!='verified_text_artifact'} for p in proofs]


def evidence_fingerprint(proofs):
    return digest(encode(sorted(publication_proofs(proofs),key=lambda p:p['claim_id'])).encode())


def fingerprint(files):
    return digest(encode({name: digest(raw) for name, raw in sorted(files.items())}).encode())


def receipt_bytes(receipt):
    return (json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode()


def sealed_generation(table_sha256,publication_sha256):
    return digest(encode({'tables_sha256':table_sha256,'publication_sha256':publication_sha256}).encode())


def read_snapshot(path):
    """Resolve the pointer once so a reader cannot mix publication generations."""
    resolved = path.resolve(strict=True)
    return {name: (resolved/(name+'.jsonl')).read_bytes() for name in IDS}


def review_gate(rows, registry, plan, proofs, previous, previous_reviewed_at=None):
    profile=plan.get('validation_profile',{}).get('name','1.0.0')
    withdrawn=set()
    if profile in ('1.0.2','1.0.3','1.0.4'):
        from instrument_event_maintenance import transition, instant
        state=transition(rows,previous)
        require(plan['evidence_sha256']==evidence_fingerprint(proofs),'Publication evidence proof fingerprint differs')
        if previous_reviewed_at is not None:
            require(instant(plan['reviewed_at'])>instant(previous_reviewed_at),'Publication review must follow predecessor review')
        withdrawn={r['event_id'] for r in state['statuses'] if r['review_state']=='withdrawn'}
        if previous['instrument_events']:
            require(previous_reviewed_at is not None,'Maintenance requires pinned predecessor review time')
        for key,decision in rows['review_decisions'].items():
            if key in previous['review_decisions']:continue
            target=decision['target'];event_id=target['id'] if target['table']=='instrument_events' else None
            if target['table']=='claims':
                claim=rows['claims'].get(target['id'],{})
                if claim.get('subject',{}).get('table')=='instrument_events':event_id=claim['subject']['id']
            if event_id is None:continue
            require(instant(decision['decided_at'])<=instant(plan['reviewed_at']),'Event review is later than publication review')
            if event_id in previous['instrument_events']:
                require(instant(decision['decided_at'])>instant(previous_reviewed_at),'Event maintenance backdates predecessor publication')
    if profile == '1.0.4':
        for key, event in rows['instrument_events'].items():
            if key in withdrawn or event.get('action') != 'policy_successor_adopted':
                continue
            refs = (event['instrument'], event['related_instrument']['instrument'])
            resolved = []
            for ref in refs:
                if ref['kind'] == 'restriction':
                    identity = registry.resolve(ref['id'])
                    require(len(identity) == 1, 'Policy succession restriction reference is ambiguous')
                    resolved.append(next(iter(identity)))
                else:
                    resolved.append(None)
            if all(value is not None for value in resolved):
                require(resolved[0] != resolved[1], 'Policy succession references resolve to the same identity')
    reviews = {}
    for review in plan['record_reviews']:
        required={'table','id','record_sha256','previous_sha256','accepted_fields','unresolved_fields','publication'}
        if profile in ('1.0.2','1.0.3','1.0.4'):required.add('historical_fields')
        require(set(review) == required,
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
                require((encode(record)==encode(old)) if profile in ('1.0.2','1.0.3','1.0.4') else record==old, 'Historical observations, claims and decisions are immutable')
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
            historical=review.get('historical_fields',[])
            require(isinstance(historical,list) and len(set(historical))==len(historical) and
                    not set(historical)&(set(accepted)|set(unresolved)),'Invalid historical field partition')
            require(set(accepted) | set(unresolved) | set(historical) == fields, 'Every field requires an explicit disposition')
            if historical:
                require(profile in ('1.0.2','1.0.3','1.0.4') and table=='instrument_events' and key in withdrawn and old is not None
                        and encode(old)==encode(record) and set(historical)==fields and not accepted and not unresolved,
                        'Historical fields require an unchanged previously published withdrawn event')
            if profile in ('1.0.2','1.0.3','1.0.4') and table=='instrument_events' and key in withdrawn:
                require(set(historical)==fields,'Withdrawn event fields must be explicitly historical')
            for field in unresolved:
                value = record[field]
                require(value is None or value in ('unknown', 'unresolved') or value == [] or value == {}
                        or value == {'earliest': None, 'latest': None, 'precision': 'unknown', 'original_text': None},
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
                # A reviewed interpretation (e.g. bindingness) may be supported by
                # an accepted wording claim. Structural validation checks the
                # claim's own predicate acceptance and exact subject separately.
                require(bool(live[0]['claim_ids']), 'Field acceptance requires supporting claims')
    for table, records in previous.items():
        require(set(records) <= set(rows[table]), 'Records cannot silently disappear: '+table)
    profile=plan.get('validation_profile',{}).get('name','1.0.0')
    if set(rows['instrument_events'])-set(previous['instrument_events']):
        require(profile in ('1.0.1','1.0.2','1.0.3','1.0.4'),'New instrument events require explicit validation profile 1.0.1 or 1.0.2')
    if profile=='1.0.1':
        for key,event in rows['instrument_events'].items():
            target={'table':'instrument_events','id':key}
            expected={f:event[f] for f in ('instrument','action','occurrence')}
            exact=set()
            for cid in event['claim_ids']:
                claim=rows['claims'][cid]
                accepted_claim=[d for d in decisions if d['target']=={'table':'claims','id':cid}
                    and d['scope']==claim['predicate'] and d['decision_id'] not in superseded]
                if (claim['subject']==target and claim['predicate']=='instrument_event' and claim['value']==expected
                    and len(accepted_claim)==1 and accepted_claim[0]['disposition']=='accepted'):
                    exact.add(cid)
            require(bool(exact),'Event lacks current accepted exact event claim')
            for field in ('instrument','action','occurrence'):
                live=[d for d in decisions if d['target']==target and d['scope']==field and d['decision_id'] not in superseded]
                require(len(live)==1 and live[0]['disposition']=='accepted' and bool(exact.intersection(live[0]['claim_ids'])),
                        'Event field must cite accepted exact event claim: '+field)


def validate_plan(plan):
    fields={'schema_version', 'expected_sha256', 'registry_sha256', 'snapshot_sha256',
            'reviewer', 'reviewed_at', 'rationale', 'record_reviews'}
    require(plan['schema_version'] in ('1.0.0','1.0.1','1.0.2','1.0.3','1.0.4'), 'Unsupported plan version')
    if plan['schema_version'] in ('1.0.1','1.0.2','1.0.3','1.0.4'):
        fields.add('validation_profile');profile=plan.get('validation_profile')
        require(isinstance(profile,dict) and set(profile)=={'name','schema_sha256','semantics'} and profile['name']==plan['schema_version']
                and profile['schema_sha256']==digest(profile_path(profile['name']).read_bytes())
                and profile['semantics']=={'1.0.1':'event-exact-accepted-v1','1.0.2':'event-validity-v1','1.0.3':'event-validity-conditions-v1','1.0.4':'event-validity-conditions-policy-succession-v1'}[plan['schema_version']],'Invalid validation profile pin')
    if plan['schema_version'] in ('1.0.2','1.0.3','1.0.4'):
        fields.update({'evidence_sha256','expected_publication_sha256'})
        import re
        prior=plan.get('expected_publication_sha256')
        require((plan['expected_sha256'] is None and prior is None) or (plan['expected_sha256'] is not None and isinstance(prior,str) and re.fullmatch('[a-f0-9]{64}',prior)),'Invalid predecessor publication fingerprint')
        require(isinstance(plan.get('evidence_sha256'),str) and re.fullmatch('[a-f0-9]{64}',plan['evidence_sha256']),'Invalid publication evidence fingerprint')
    require(set(plan)==fields,'Invalid plan fields')
    require(all(isinstance(plan[k], str) and plan[k].strip() for k in ('reviewer', 'rationale')),
            'Explicit reviewer and rationale required')
    require(datetime.fromisoformat(plan['reviewed_at'].replace('Z', '+00:00')).tzinfo is not None,
            'Review timestamp must include timezone')


def publish(destination, candidate, registry_path, plan, evidence_directories,
            apply=False, visual_reviews=None, moratoria=None, state_actions=None):
    validate_plan(plan)
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
        errors, rows = validate(candidate.resolve(), moratoria, state_actions,
                                profile=plan.get('validation_profile',{}).get('name','1.0.0'))
        require(not errors, 'Invalid candidate: '+'; '.join(errors))
        files = serialized(rows); target_hash = fingerprint(files)
        require(target_hash == plan['snapshot_sha256'], 'Candidate snapshot changed since review')
        current_files = read_snapshot(destination) if destination.exists() else None
        current_hash = fingerprint(current_files) if current_files else None
        # An exact replay verifies retained bytes and the original publication plan.
        replay = current_hash == target_hash
        if replay and plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
            current_receipt=json.loads((destination.resolve()/'publication.json').read_text())
            replay=(current_receipt.get('plan_sha256')==digest(encode(plan).encode()) and current_receipt.get('plan')==plan)
        require(replay or current_hash == plan['expected_sha256'], 'Snapshot changed since review')
        previous = {table: {} for table in IDS}
        if current_files and not replay:
            for table, raw in current_files.items():
                previous[table] = {r[IDS[table]]: r for r in map(json.loads, raw.decode().splitlines())}
        if replay:
            require(current_files == files, 'Published snapshot bytes are not canonical')
            retained = json.loads((destination.resolve()/'publication.json').read_text())
            require(retained['plan_sha256'] == digest(encode(plan).encode()), 'Replay plan differs from publication')
            require(retained['plan'] == plan and retained['sha256'] == target_hash
                    and retained['schema_version'] == '1.0.0', 'Retained publication receipt drift')
            # Recheck retained proofs/history under each original profile; no reacquisition.
            from check_expanded_publication import check
            check(destination,registry_path,moratoria,state_actions)
            result={'state':'already_applied','sha256':target_hash}
            if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
                result.update(generation_id=destination.resolve().name,publication_sha256=digest((destination.resolve()/'publication.json').read_bytes()))
            return result
        previous_reviewed_at=None
        if current_files:
            prior_raw=(destination.resolve()/'publication.json').read_bytes()
            prior_receipt=json.loads(prior_raw)
            if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
                require(digest(prior_raw)==plan['expected_publication_sha256'],'Predecessor publication receipt changed since review')
            previous_reviewed_at=prior_receipt['plan']['reviewed_at']
            if prior_receipt['plan'].get('validation_profile',{}).get('name') in ('1.0.3','1.0.4'):
                require(plan.get('validation_profile',{}).get('name') in (('1.0.3','1.0.4') if prior_receipt['plan'].get('validation_profile',{}).get('name')=='1.0.3' else ('1.0.4',)),'Cannot downgrade condition publication profile')
            from check_expanded_publication import check
            check(destination,registry_path,moratoria,state_actions)
            if prior_receipt['plan'].get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
                require(plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'),'Cannot downgrade event-validity publication profile')
        maintenance=any(d['target']['table']=='instrument_events' and d['scope']=='event_validity' for d in rows['review_decisions'].values()) or any(c.get('predicate') in ('event_validity','event_correction') for c in rows['claims'].values())
        if maintenance:require(plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'),'Event maintenance requires validation profile 1.0.2')
        if rows['instrument_events']:
            require(plan.get('validation_profile',{}).get('name') in ('1.0.1','1.0.2','1.0.3','1.0.4'),
                    'Publication containing instrument events cannot downgrade validation profile')
        index = {}
        for directory in evidence_directories:
            entries, issues, _ = evidence_index(directory)
            require(not issues, 'Evidence integrity errors: '+str(issues))
            for url, versions in entries.items():
                index.setdefault(url, []).extend(versions)
        issues, proofs = audit_expanded_evidence(rows, index, visual_reviews)
        require(not issues, 'Evidence version errors: '+str(issues))
        review_gate(rows, registry, plan, proofs, previous, previous_reviewed_at)
        result = {'state': 'ready', 'sha256': target_hash,
                  'records': {table: len(records) for table, records in rows.items()}}
        receipt = {'schema_version':'1.0.0','sha256':target_hash,'plan_sha256':digest(encode(plan).encode()),'plan':plan,'evidence':publication_proofs(proofs)}
        receipt_raw=receipt_bytes(receipt)
        generation=sealed_generation(target_hash,digest(receipt_raw)) if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4') else target_hash
        if plan.get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
            result.update(generation_id=generation,publication_sha256=digest(receipt_raw))
        if not apply:
            return result
        snapshots = destination.parent/(destination.name+'-snapshots')
        snapshots.mkdir(exist_ok=True)
        final = snapshots/generation
        require(not final.exists(), 'Unreferenced snapshot exists; inspect recovery inputs before retry')
        with tempfile.TemporaryDirectory(prefix='.staging-', dir=snapshots) as temporary:
            stage = Path(temporary)/'snapshot'; stage.mkdir()
            for table, raw in files.items():
                with (stage/(table+'.jsonl')).open('wb') as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
            with (stage/'publication.json').open('wb') as f:
                f.write(receipt_raw);f.flush();os.fsync(f.fileno())
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
