"""Prepare source-reviewed compound clauses and a profile upgrade; never promote."""
import argparse,copy,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'scripts'))
from expanded_data import IDS,validate,profile_path
from expanded_identity import apply_plan,encode
from expanded_promotion import read_snapshot,serialized,fingerprint,evidence_fingerprint
from audit_refresh_returns import evidence_index,audit_expanded_evidence
from verify_reviews import verify

p=argparse.ArgumentParser();p.add_argument('--scratch',type=Path,required=True);a=p.parse_args()
packet=Path(__file__).resolve().parent
assert not (packet/'context.private.json').exists(),'Prepared once; inspect retained IDs, do not reallocate'
private=Path('/data0/moratorium-refresh-2026/frozen-domain-evaluation/compound-source-adjudicated.private.json')
verified=verify(private);selection=json.loads((packet/'selection.json').read_text());assert verified['artifact_sha256']==selection['adjudicated_sha256']
adjudicated=json.loads(private.read_text())
old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(ROOT/'data/expanded').items()}
rows=copy.deepcopy(old);prior_raw=(ROOT/'data/expanded/publication.json').read_bytes();prior=json.loads(prior_raw)
assert prior['plan']['validation_profile']['name']=='1.0.2'
a.scratch.mkdir(parents=True,exist_ok=False);candidate=a.scratch/'candidate';candidate.mkdir()
stamp=datetime.now(timezone.utc).isoformat();sha=lambda value:hashlib.sha256(encode(value).encode()).hexdigest()
new=[];allocations=[];modified=[];bindings=[]
by_text={s['text_sha256']:s for s in rows['source_documents'].values()}
subjects={'bp-f7852025abec20c9':'5073484c-5748-487e-8443-d50f3664e2bf','bp-e0efdc31b0b81e45':'a83cfd23-a651-4651-b50a-11eeea110be1'}
def add(table,record,source):
 key=record[IDS[table]];assert key not in rows[table];rows[table][key]=record;new.append((table,key))
 allocations.append(dict(schema_version='1.0.0',event_id=str(uuid4()),action='allocate',table=table,inputs=[],outputs=[key],aliases=[dict(namespace='compound-source-review-2026-11-06',source_id=key,record_sha256=sha(record))],assignments=[],reviewer='coordinator',reviewed_at=stamp,rationale='Source-reviewed proposed compound-clause claim or scoped acceptance identity; no new legal instrument or force finding.',evidence=[dict(url=source['url'],body_sha256=source['body_sha256'],locator='Retained proposed legal text; exact source quotations and additional support spans in the source review')]))
for case in adjudicated['cases']:
 key=subjects[case['case_id']];target=dict(table='measure_provisions',id=key);record=rows['measure_provisions'][key]
 assert 'condition_clauses' not in record
 source=by_text[case['text_sha256']];claims=[]
 for item in case['clauses']:
  cid=str(uuid4());start,end=item['source_spans'][0]
  claim=dict(schema_version='1.0.0',claim_id=cid,subject=target,predicate='proposed_condition_clause',value=dict(clause=item['contract'],interpretive_limits=item['unresolved']),source_document_id=source['source_document_id'],quote=item['contract']['source_text'],span=f'utf8-text-codepoints:{start}:{end}',temporal_support=dict(earliest=None,latest=None,precision='unknown',original_text=None),extraction_provenance='Coordinator direct retained-source review, reconciled with two independent Terra clause drafts. Source-proposed clauses only; no operative applicability or legal simplification accepted. Exact primary and additional definition/limitation support spans retained in the source review.')
  add('claims',claim,source);claims.append(cid)
  did=str(uuid4());decision=dict(schema_version='1.0.0',decision_id=did,target=dict(table='claims',id=cid),scope='proposed_condition_clause',claim_ids=[cid],disposition='accepted',supersedes_id=None,reviewer='coordinator',method='direct retained proposed-text review and PDF context; independent Terra drafts reconciled',rationale='Accept descriptive source clause with preserved purpose, proposed context, conjunction/cardinality, definition gates and explicit interpretation limits. Do not accept current force or resolve capacity/demand/water comparison ambiguity.',decided_at=stamp)
  add('review_decisions',decision,source)
  bindings.append(dict(clause_id=item['clause_id'],claim_id=cid,decision_id=did,source_document_id=source['source_document_id'],source_spans=item['source_spans'],supporting_spans=item['supporting_spans'],interpretive_limits=item['unresolved']))
 record['condition_clauses']=[item['contract'] for item in case['clauses']];record['claim_ids']+=claims
 did=str(uuid4());decision=dict(schema_version='1.0.0',decision_id=did,target=target,scope='condition_clauses',claim_ids=claims,disposition='accepted',supersedes_id=None,reviewer='coordinator',method='source-qualified complete-group review under profile1.0.3',rationale='Accept selected descriptive proposed clauses as documented in the source review, retaining separate source-claim interpretation limits. Existing flat thresholds remain unchanged; no general execution/equivalence semantics or legal effect inferred.',decided_at=stamp)
 add('review_decisions',decision,source);modified.append(key)
registry=ROOT/'data/identities/expanded.jsonl';identity=dict(schema_version='1.0.0',expected_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),events=allocations)
preview=a.scratch/'registry-preview.jsonl';preview.write_bytes(registry.read_bytes());apply_plan(preview,identity,True)
for table,raw in serialized(rows).items():(candidate/(table+'.jsonl')).write_bytes(raw)
errors,_=validate(candidate,ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv',profile='1.0.3');assert not errors,errors
roots_path=Path('/data0/moratorium-refresh-2026/frozen-domain-evaluation/event-validity-evidence-roots.private.json');roots=json.loads(roots_path.read_text());index={}
for directory in map(Path,roots):
 entries,issues,_=evidence_index(directory);assert not issues,issues
 for url,versions in entries.items():index.setdefault(url,[]).extend(versions)
visual_paths=json.loads((ROOT/'work/research/2026-11-06/event-validity-migration/visual-reviews.json').read_text());visual={}
for path in visual_paths:
 receipt=json.loads(Path(path).read_text());visual[receipt['claim_id']]=receipt
issues,proofs=audit_expanded_evidence(rows,index,visual);assert not issues,issues
assert len(proofs)==len(rows['claims']) and all(p['evidence_verified'] for p in proofs)
reviews=[]
for review in prior['plan']['record_reviews']:
 r=copy.deepcopy(review);r['previous_sha256']=r['record_sha256']
 if r['table']=='measure_provisions' and r['id'] in modified:
  r['record_sha256']=sha(rows[r['table']][r['id']]);r['accepted_fields']=sorted(r['accepted_fields']+['condition_clauses'])
 reviews.append(r)
for table,key in new:
 record=rows[table][key]
 reviews.append(dict(table=table,id=key,record_sha256=sha(record),previous_sha256=None,accepted_fields=sorted(set(record)-{'schema_version',IDS[table]}),unresolved_fields=[],historical_fields=[],publication='reviewed_excerpt' if table=='claims' else 'reviewed_metadata'))
plan=dict(schema_version='1.0.3',validation_profile=dict(name='1.0.3',schema_sha256=hashlib.sha256(profile_path('1.0.3').read_bytes()).hexdigest(),semantics='event-validity-conditions-v1'),expected_sha256=fingerprint(serialized(old)),expected_publication_sha256=hashlib.sha256(prior_raw).hexdigest(),registry_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),snapshot_sha256=fingerprint(serialized(rows)),evidence_sha256=evidence_fingerprint(proofs),reviewer='coordinator',reviewed_at=stamp,rationale='Source-reviewed descriptive proposed compound clauses for existing Mandan/Harwood provisions, with exact source and interpretation limits. Activate optional profile1.0.3, preserve all other field values and every prior record; no new measure, result, event, force or acceptance of final ballot qualification.',record_reviews=reviews)
for table in old:
 for key,record in old[table].items():
  if table=='measure_provisions' and key in modified:
   after=copy.deepcopy(rows[table][key]);after.pop('condition_clauses');after['claim_ids']=record['claim_ids'];assert after==record
  else:assert rows[table][key]==record

def dump(name,value):(packet/name).write_text(json.dumps(value,indent=2)+'\n')
dump('identity-plan.json',identity);dump('publication-plan.json',plan);dump('claim-bindings.json',bindings)
dump('visual-reviews.json',visual_paths)
dump('source-preflight.json',dict(claims=len(proofs),verified_claims=sum(p['evidence_verified'] for p in proofs),source_documents=len(rows['source_documents']),evidence_directories=len(roots),evidence_config_sha256=hashlib.sha256(roots_path.read_bytes()).hexdigest(),public_evidence_sha256=plan['evidence_sha256'],source_reacquisitions=0,extraction_provider_calls=0))
dump('context.private.json',dict(candidate=str(candidate),scratch=str(a.scratch),prepared_at=stamp,evidence_config=str(roots_path),legacy_csv_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv']}))
dump('preservation-preflight.json',dict(prior_generation=(ROOT/'data/expanded').resolve().name,modified_provisions=modified,clauses=sum(len(c['clauses']) for c in adjudicated['cases']),new_claims=12,new_review_decisions=14,new_identities=len(allocations),all_prior_records_retained=True,all_other_prior_fields_unchanged=True,counts={t:len(r) for t,r in rows.items()}))
print(json.dumps(dict(candidate_table_sha256=plan['snapshot_sha256'],verified_claims=len(proofs),clauses=12,new_identity_events=len(allocations)),indent=2))
