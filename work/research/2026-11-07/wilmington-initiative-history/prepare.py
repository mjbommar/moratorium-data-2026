"""Build a pinned offline Wilmington candidate and private registry preview, never publish."""
import argparse,copy,hashlib,json,sys,uuid
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; PACKET=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from expanded_data import IDS,validate,profile_path
from expanded_identity import apply_plan,encode
from expanded_promotion import read_snapshot,serialized,fingerprint,evidence_fingerprint
from audit_refresh_returns import evidence_index,audit_expanded_evidence
p=argparse.ArgumentParser();p.add_argument('--scratch',type=Path,required=True);a=p.parse_args()
assert not (PACKET/'identity-plan.json').exists(), 'Already allocated; preserve pinned plan'
a.scratch.mkdir(parents=True,exist_ok=False);candidate=a.scratch/'candidate';candidate.mkdir()
digest=lambda b:hashlib.sha256(b).hexdigest()
sha=lambda v:digest(encode(v).encode())
dump=lambda n,v:(PACKET/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(ROOT/'data/expanded').items()};rows=copy.deepcopy(old)
prior_raw=(ROOT/'data/expanded/publication.json').read_bytes();prior=json.loads(prior_raw);assert prior['plan']['validation_profile']['name']=='1.0.3'
source_review=json.loads((ROOT/'work/research/2026-11-06/ohio-ballot-wave5-review/review.json').read_text())
source_path=Path('/data0/moratorium-refresh-2026/ohio-ballot-wave5-review');meta=json.loads((source_path/'102f8724b04545539c437b6ae371f005.private.json').read_text());assert meta['fetched_at']=='2026-11-06T08:42:15.629759Z'
url='https://www.supremecourt.ohio.gov/rod/docs/pdf/0/2026/2026-Ohio-3663.pdf';body='cd2b64c99e62a3a5f8954fae5241d03156d5f8f5eecfdbd41b42aa1297689812';txt='e7090c0c9fd93f85b31c980cfc7e2136041b7323695c0630f57870538f1d09a1'
assert digest((source_path/'102f8724b04545539c437b6ae371f005.private.body').read_bytes())==body
assert digest((source_path/'102f8724b04545539c437b6ae371f005.private.txt').read_bytes())==txt
stamp=datetime.now(timezone.utc).isoformat();new=[];events=[]
def add(t,r,alias):
 k=r[IDS[t]];assert k not in rows[t];rows[t][k]=r;new.append((t,k));events.append(dict(schema_version='1.0.0',event_id=str(uuid.uuid4()),action='allocate',table=t,inputs=[],outputs=[k],aliases=[dict(namespace='wilmington-initiative-history-2026-11-07',source_id=alias,record_sha256=sha(r))],assignments=[],reviewer='coordinator',reviewed_at=stamp,rationale='Distinct source-qualified historical initiative observation and scoped review; no current status or legal force.',evidence=[dict(url=url,body_sha256=body,locator='Ohio Supreme Court slip opinion 2026-Ohio-3663')]))
matches=[s for s in rows['source_documents'].values() if s['url']==url and s['body_sha256']==body and s['text_sha256']==txt]
assert len(matches)<=1
if matches: sid=matches[0]['source_document_id']
else:
 sid=str(uuid.uuid4());add('source_documents',dict(schema_version='1.0.0',source_document_id=sid,url=url,body_sha256=body,text_sha256=txt,retrieved_at=meta['fetched_at'],published_date=None,retrieval_method='research_client http',extraction_version='research_client retained text',access_classification='publicly accessible; raw artifacts private',publication_classification='official judicial primary; slip opinion subject to formal revision'),'oh5-review-court-opinion')
mid=str(uuid.uuid4());target=dict(table='ballot_measures',id=mid)
measure=dict(schema_version='1.0.0',measure_id=mid,jurisdiction_id='a678d929-6944-4bf2-bd60-ef0c3a3ebe98',election_id='d9ec705b-cc42-4127-9ec1-8baa301781c6',designation=None,wording=None,title='Proposed Wilmington Zoning Code Chapter 1161 initiative',placement_method='citizen_initiative',placement_source_term='initiative petition',legal_basis=None,lifecycle='litigated',bindingness='unresolved',sectors=['data_center'],yes_direction='unresolved',referendum_yes_effect='not_applicable',scope_note='The September 18, 2026 Ohio Supreme Court slip opinion reports that the board refused certification for the intended November 3, 2026 election on August 12 and reaffirmed its decision on August 26; the court denied mandamus on September 18. This is a dated litigation history; later and current status are unknown. The original petition, ordinance and administrative instruments, later case and election history, and legal force were not independently reviewed.')
add('ballot_measures',measure,'candidate:wilmington-ch1161-2026')
claims=[]
for item in source_review['claims']:
 if item['claim_id'] not in ['ohio-wave5-review-15','ohio-wave5-review-16','ohio-wave5-review-17']:continue
 cid=str(uuid.uuid4());value=copy.deepcopy(item['value'])
 claim=dict(schema_version='1.0.0',claim_id=cid,subject=target,predicate=item['predicate'],value=value,source_document_id=sid,quote=item['quote'],span=item['span'],temporal_support=dict(earliest=None,latest=None,precision='unknown',original_text=None),extraction_provenance='Coordinator source review of retained official judicial slip opinion; source-qualified historical account, later history unknown.')
 add('claims',claim,item['claim_id']);claims.append(cid)
 did=str(uuid.uuid4());add('review_decisions',dict(schema_version='1.0.0',decision_id=did,target=dict(table='claims',id=cid),scope=item['predicate'],claim_ids=[cid],disposition='accepted',supersedes_id=None,reviewer='coordinator',method='direct retained official judicial source review',rationale='Accept only the court-reported historical observation and its stated limits.',decided_at=stamp),'claim:'+item['claim_id'])
assert len(claims)==3
accepted=['jurisdiction_id','election_id','title','placement_method','placement_source_term','lifecycle','sectors','referendum_yes_effect','scope_note']
unresolved=['designation','wording','legal_basis','bindingness','yes_direction']
for field in accepted:
 ids=claims if field in ['scope_note','lifecycle','election_id'] else [claims[0]]
 did=str(uuid.uuid4());add('review_decisions',dict(schema_version='1.0.0',decision_id=did,target=target,scope=field,claim_ids=ids,disposition='accepted',supersedes_id=None,reviewer='coordinator',method='source-qualified field review',rationale='Dated court history and intended election only; no later status or legal force inferred.',decided_at=stamp),'field:'+field)
registry=ROOT/'data/identities/expanded.jsonl';identity=dict(schema_version='1.0.0',expected_sha256=digest(registry.read_bytes()),events=events);preview=a.scratch/'registry-preview.jsonl';preview.write_bytes(registry.read_bytes());apply_plan(preview,identity,True)
for t,raw in serialized(rows).items():(candidate/(t+'.jsonl')).write_bytes(raw)
errors,_=validate(candidate,ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv',profile='1.0.3');assert not errors,errors
roots_path=Path('/data0/moratorium-refresh-2026/frozen-domain-evaluation/event-validity-evidence-roots.private.json');roots=json.loads(roots_path.read_text())+[str(source_path)];index={}
for directory in map(Path,roots):
 entries,issues,_=evidence_index(directory);assert not issues,issues
 for u,versions in entries.items():index.setdefault(u,[]).extend(versions)
visual_paths=json.loads((ROOT/'work/research/2026-11-06/event-validity-migration/visual-reviews.json').read_text());visual={}
for path in visual_paths:
 path=Path(path);path=path if path.is_absolute() else ROOT/path
 receipt=json.loads(path.read_text());visual[receipt['claim_id']]=receipt
issues,proofs=audit_expanded_evidence(rows,index,visual);assert not issues,issues
assert len(proofs)==543 and all(p['evidence_verified'] for p in proofs)
reviews=[]
for review in prior['plan']['record_reviews']:
 r=copy.deepcopy(review);r['previous_sha256']=sha(old[r['table']][r['id']]);assert r['record_sha256']==r['previous_sha256'];reviews.append(r)
for t,k in new:
 record=rows[t][k];fields=sorted(set(record)-{'schema_version',IDS[t]});un=unresolved if t=='ballot_measures' else []
 reviews.append(dict(table=t,id=k,record_sha256=sha(record),previous_sha256=None,accepted_fields=[f for f in fields if f not in un],unresolved_fields=un,historical_fields=[],publication='reviewed_excerpt' if t=='claims' else 'reviewed_metadata'))
plan=dict(schema_version='1.0.3',validation_profile=dict(name='1.0.3',schema_sha256=digest(profile_path('1.0.3').read_bytes()),semantics='event-validity-conditions-v1'),expected_sha256=fingerprint(serialized(old)),expected_publication_sha256=digest(prior_raw),registry_sha256=digest(preview.read_bytes()),snapshot_sha256=fingerprint(serialized(rows)),evidence_sha256=evidence_fingerprint(proofs),reviewer='coordinator',reviewed_at=stamp,rationale='Historical court-reported initiative and intended election only; no later status, result or legal effect.',record_reviews=reviews)
for t in old:
 for k,v in old[t].items():assert encode(rows[t][k])==encode(v)
dump('identity-plan.json',identity);dump('publication-plan.json',plan);dump('visual-reviews.json',visual_paths)
dump('context.private.json',dict(candidate=str(candidate),scratch=str(a.scratch),evidence_config=str(roots_path),extra_evidence=str(source_path),root=str(ROOT)))
dump('source-preflight.json',dict(claims=len(proofs),verified_claims=sum(p['evidence_verified'] for p in proofs),source_documents=len(rows['source_documents']),evidence_directories=len(roots),evidence_config_sha256=digest(roots_path.read_bytes()),evidence_sha256=plan['evidence_sha256'],court_body_sha256=body,court_text_sha256=txt,retrieved_at=meta['fetched_at'],source_reacquisitions=0))
dump('preservation-preflight.json',dict(prior_generation=(ROOT/'data/expanded').resolve().name,all_prior_record_bytes_preserved=True,counts_before={t:len(v) for t,v in old.items()},counts_after={t:len(v) for t,v in rows.items()},legacy_csv_sha256={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv']},frozen_census_groups_delta=0,new_identity_events=len(events)))
print(json.dumps(dict(snapshot=plan['snapshot_sha256'],claims=len(proofs),identity_events=len(events)),indent=2))
