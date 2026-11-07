"""Prepare the reviewed five-event validity migration, never canonical promotion."""
import argparse,copy,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path('scripts').resolve()))
from expanded_data import IDS,profile_path,validate
from expanded_identity import apply_plan,encode
from expanded_promotion import read_snapshot,serialized,fingerprint,evidence_fingerprint
from audit_refresh_returns import evidence_index,audit_expanded_evidence

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',type=Path,required=True);p.add_argument('--evidence-config',type=Path,required=True);a=p.parse_args()
packet=Path(__file__).resolve().parent
assert not (packet/'context.json').exists(),'Prepared once; inspect retained IDs instead of reallocating'
roots=json.loads(a.evidence_config.read_text());assert roots
old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(Path('data/expanded')).items()}
assert len(old['instrument_events'])==5
rows=copy.deepcopy(old);prior_raw=(Path('data/expanded')/'publication.json').read_bytes();prior=json.loads(prior_raw)
assert prior['plan']['validation_profile']['name']=='1.0.1'
a.scratch.mkdir(parents=True,exist_ok=True);candidate=a.scratch/'candidate';candidate.mkdir(exist_ok=True)
stamp=datetime.now(timezone.utc).isoformat();new=[];summary=[];allocations=[]
sha=lambda r:hashlib.sha256(encode(r).encode()).hexdigest()
for key,event in sorted(old['instrument_events'].items()):
 cid=event['claim_ids'][0];claim=old['claims'][cid]
 assert claim['predicate']=='instrument_event' and claim['value']=={f:event[f] for f in ('instrument','action','occurrence')}
 source=old['source_documents'][claim['source_document_id']]
 reason=('Direct original signed-act review supports the historical adoption date and existing instrument identity. ' if event['action']=='adopted' else
         'Direct original signed-act and express immediate-effect clause review supports source-declared historical effectiveness on the dated passage/adoption day. ')
 reason+='Retain original event/claim values, day precision, unknown publication time and observation time. This is current review acceptance of a historical event, not current instrument enforceability. Later amendments/extensions/termination, actual expiry and current legal force remain unresolved.'
 if event['instrument']['id']=='wa-whitman-county-2025':reason+=' The May ordinance is distinct from the January wind pause; the execution line says dated, read together with the board-passage clause. Original July7 endpoint is not a verified current operative end.'
 if event['instrument']['id']=='il-stephenson-county-2026':reason+=' Effectiveness under applicable law and the operative endpoint remain unresolved; no effectiveness event is added.'
 did=str(uuid4());decision=dict(schema_version='1.0.0',decision_id=did,target=dict(table='instrument_events',id=key),scope='event_validity',claim_ids=[cid],disposition='accepted',supersedes_id=None,
                              reviewer='coordinator',method='direct retained original-PDF visual review, reconciled with independent terra adoption/effectiveness reviews',rationale=reason,decided_at=stamp)
 rows['review_decisions'][did]=decision;new.append(did)
 allocations.append(dict(schema_version='1.0.0',event_id=str(uuid4()),action='allocate',table='review_decisions',inputs=[],outputs=[did],aliases=[dict(namespace='event-validity-migration-2026-11-06',source_id=did,record_sha256=sha(decision))],assignments=[],reviewer='coordinator',reviewed_at=stamp,rationale='Explicit scoped historical event-validity review identity; no event, instrument, claim or source identity changes.',evidence=[dict(url=source['url'],body_sha256=source['body_sha256'],locator='Existing exact event claim and original title/signed-date/operative-clause pages')]))
 summary.append(dict(event_id=key,claim_id=cid,decision_id=did,instrument=event['instrument'],action=event['action'],occurrence=event['occurrence'],source_document_id=claim['source_document_id'],scope='Accepted original event only; no current-force finding.'))
registry=Path('data/identities/expanded.jsonl');identity=dict(schema_version='1.0.0',expected_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),events=allocations)
preview=a.scratch/'registry-preview.jsonl';preview.write_bytes(registry.read_bytes());apply_plan(preview,identity,True)
for table,raw in serialized(rows).items():(candidate/(table+'.jsonl')).write_bytes(raw)
errors,_=validate(candidate,Path('data/moratorium_inventory.csv'),Path('data/state_legislation.csv'),profile='1.0.2');assert not errors,errors
visual_paths=json.loads(Path('work/research/2026-11-06/instrument-event-migration/visual-reviews.json').read_text());visual={}
for path in visual_paths:
 receipt=json.loads(Path(path).read_text());visual[receipt['claim_id']]=receipt
index={}
for directory in map(Path,roots):
 entries,issues,_=evidence_index(directory);assert not issues,issues
 for url,versions in entries.items():index.setdefault(url,[]).extend(versions)
issues,proofs=audit_expanded_evidence(rows,index,visual);assert not issues,issues
assert len(proofs)==len(rows['claims']) and all(p['evidence_verified'] for p in proofs),'Every retained claim must verify'
reviews=[]
for review in prior['plan']['record_reviews']:
 review=copy.deepcopy(review);review['previous_sha256']=review['record_sha256'];review['historical_fields']=[];reviews.append(review)
for did in new:
 d=rows['review_decisions'][did];fields=sorted(set(d)-{'schema_version','decision_id'})
 reviews.append(dict(table='review_decisions',id=did,record_sha256=sha(d),previous_sha256=None,accepted_fields=fields,unresolved_fields=[],historical_fields=[],publication='reviewed_metadata'))
plan=dict(schema_version='1.0.2',validation_profile=dict(name='1.0.2',schema_sha256=hashlib.sha256(profile_path('1.0.2').read_bytes()).hexdigest(),semantics='event-validity-v1'),
          expected_sha256=fingerprint(serialized(old)),expected_publication_sha256=hashlib.sha256(prior_raw).hexdigest(),registry_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),snapshot_sha256=fingerprint(serialized(rows)),evidence_sha256=evidence_fingerprint(proofs),reviewer='coordinator',reviewed_at=stamp,
          rationale='Explicit source-reviewed validity acceptance for five unchanged historical events. No new event or inferred current force; preserve every prior record. Separately qualify Whitman original endpoint in the legacy CSV.',record_reviews=reviews)
assert all(rows[t][key]==record for t in old for key,record in old[t].items())
def dump(name,value):(packet/name).write_text(json.dumps(value,indent=2)+'\n')
dump('identity-plan.json',identity);dump('publication-plan.json',plan);dump('cohort.json',dict(events=summary,prior_generation=Path('data/expanded').resolve().name,prior_table_snapshot=plan['expected_sha256'],prior_publication_sha256=plan['expected_publication_sha256'],new_records={'review_decisions':5},all_prior_records_unchanged=True))
dump('visual-reviews.json',visual_paths);dump('source-preflight.json',dict(source_document_records=len(rows['source_documents']),claims=len(proofs),verified_claims=sum(p['evidence_verified'] for p in proofs),evidence_directories=len(roots),evidence_config_sha256=hashlib.sha256(a.evidence_config.read_bytes()).hexdigest(),public_evidence_sha256=plan['evidence_sha256'],source_reacquisitions=0,extraction_model_calls=0))
dump('context.json',dict(candidate=str(candidate),scratch=str(a.scratch),prepared_at=stamp,evidence_config=str(a.evidence_config),legacy_csv_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('data/moratorium_inventory.csv'),Path('data/state_legislation.csv')]}))
print(json.dumps({'candidate_table_sha256':plan['snapshot_sha256'],'verified_claims':len(proofs),'new_decisions':len(new)},indent=2))
