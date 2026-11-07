"""Prepare five explicitly reviewed source events; never apply canonical changes."""
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from uuid import uuid4
sys.path.insert(0,str(Path('scripts').resolve()))
from expanded_identity import encode,apply_plan
from expanded_promotion import IDS,read_snapshot,serialized,fingerprint
from audit_refresh_returns import evidence_index

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',type=Path,required=True);p.add_argument('--evidence-root',type=Path,required=True)
a=p.parse_args();packet=Path(__file__).resolve().parent
assert not (packet/'context.json').exists(),'Prepared once; do not silently reallocate identities'
cohort=json.loads((packet/'cohort.json').read_text());assert Path('data/expanded').resolve().name==cohort['baseline_snapshot']
assert hashlib.sha256(Path(cohort['profile']).read_bytes()).hexdigest()==cohort['profile_sha256']
a.scratch.mkdir(parents=True,exist_ok=True);candidate=a.scratch/'candidate';candidate.mkdir(exist_ok=True)
old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(Path('data/expanded')).items()};rows=copy.deepcopy(old)
prior=json.loads((Path('data/expanded')/'publication.json').read_text());reviews=[]
stamp=dt.datetime.now(dt.timezone.utc).isoformat();new=[];visuals=json.loads(Path('work/research/2026-11-06/ballot-semantic-lineage/visual-reviews.json').read_text())
sha=lambda r:hashlib.sha256(encode(r).encode()).hexdigest()
vsha=lambda r:hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def add(table,record):
    key=record[IDS[table]];assert key not in rows[table];rows[table][key]=record;new.append((table,key));return key
def decision(target,scope,cid,reason):
    add('review_decisions',dict(schema_version='1.0.0',decision_id=str(uuid4()),target=target,scope=scope,claim_ids=[cid],
        disposition='accepted',reviewer='coordinator',method='scoped direct retained-PDF event review',rationale=reason,decided_at=stamp,supersedes_id=None))
evidence_dirs=set();event_summary=[]
for case in cohort['cases']:
    source=case['source'];directory=a.evidence_root/'discovery'/case['candidate_key'].split(':')[0]
    evidence_dirs.add(str(directory));index,issues,_=evidence_index(directory);assert not issues,issues
    matches=[v for v in index[source['url']] if v['body_sha256']==source['body_sha256'] and v['text_sha256']==source['text_sha256']]
    assert matches,'Original source body/text version missing'
    attempts=[json.loads(s) for s in (directory/'attempts.private.jsonl').read_text().splitlines()]
    finished=next(r for r in attempts if r['attempt_id']==source['attempt_id'] and r['state']=='finished')
    prior_source=[s for s in old['source_documents'].values() if s['url']==source['url'] and s['body_sha256']==source['body_sha256'] and s['text_sha256']==source['text_sha256']]
    if prior_source:sid=prior_source[0]['source_document_id']
    else:
        sid=add('source_documents',dict(schema_version='1.0.0',source_document_id=str(uuid4()),url=source['url'],
            retrieved_at=finished['finished_at'],published_date=None,body_sha256=source['body_sha256'],text_sha256=source['text_sha256'],
            retrieval_method='Retained successful research_client acquisition; exact original transport in private ledger',
            extraction_version='Retained client text with scoped original-PDF visual review; not full-document extraction',
            access_classification='Publicly accessible ordinance; original payloads private',publication_classification='Official signed ordinance; curated metadata and reviewed values only'))
    key=case['candidate_key'].replace(':','-')
    for proposed in case['proposed_events']:
        eid=str(uuid4());cid=str(uuid4());target=dict(table='instrument_events',id=eid)
        reason=('Direct original-PDF title/execution review identifies the existing legacy instrument and signed adoption date. '
                if proposed['action']=='adopted' else
                'Direct original-PDF review of the express immediate-effect-upon-passage/adoption clause together with the dated signed act supports this separate source-declared effectiveness event. ')
        reason+='Day precision only. Later amendments, extension/termination, actual expiry and current legal force remain unresolved. No legacy row or ballot outcome changes.'
        event=dict(schema_version='1.0.0',event_id=eid,instrument=case['instrument'],action=proposed['action'],occurrence=proposed['occurrence'],
            observed_at=stamp,published_at=None,claim_ids=[cid]);add('instrument_events',event)
        claim=dict(schema_version='1.0.0',claim_id=cid,subject=target,predicate='instrument_event',
            value={f:copy.deepcopy(event[f]) for f in ('instrument','action','occurrence')},source_document_id=sid,quote=None,
            span='pdf-pages:'+','.join(map(str,sorted(set([proposed['primary_pdf_page']]+proposed['additional_pdf_pages'])))),
            temporal_support=copy.deepcopy(event['occurrence']),extraction_provenance=reason)
        add('claims',claim);decision(dict(table='claims',id=cid),'instrument_event',cid,reason)
        for field in ['instrument','action','occurrence','observed_at']:decision(target,field,cid,reason if field!='observed_at' else 'Coordinator observation/review time, distinct from source acquisition, legal occurrence and legal publication.')
        page=proposed['primary_pdf_page'];image=Path(f'/tmp/moratorium-event-{key}-{page}.png')
        receipt=dict(claim_id=cid,source_document_id=sid,claim_sha256=vsha(claim),values=claim['value'],disposition='accepted_visual_values',reviewer='coordinator',
            source_body_sha256=source['body_sha256'],pdf_page=page,render_parameters=dict(renderer='pdftoppm',page=page,dpi=150),
            render_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),reviewed_at=stamp,
            additional_pdf_pages=[dict(page=extra,dpi=150,render_sha256=hashlib.sha256(Path(f'/tmp/moratorium-event-{key}-{extra}.png').read_bytes()).hexdigest()) for extra in proposed['additional_pdf_pages']])
        path=packet/(cid+'-visual-review.json');path.write_text(json.dumps(receipt,indent=2)+'\n');visuals.append(str(path))
        event_summary.append(dict(event_id=eid,claim_id=cid,instrument=case['instrument'],action=proposed['action'],occurrence=proposed['occurrence'],source_document_id=sid))
for review in prior['plan']['record_reviews']:
    review=copy.deepcopy(review);review['previous_sha256']=review['record_sha256'];reviews.append(review)
events=[]
for table,key in new:
    record=rows[table][key];fields=set(record)-{IDS[table],'schema_version'}
    unresolved={f for f in fields if record[f] is None}
    reviews.append(dict(table=table,id=key,record_sha256=sha(record),previous_sha256=None,accepted_fields=sorted(fields-unresolved),unresolved_fields=sorted(unresolved),publication='reviewed_metadata'))
    source=record if table=='source_documents' else rows['source_documents'][record['source_document_id']] if table=='claims' else rows['source_documents'][rows['claims'][record['claim_ids'][0]]['source_document_id']]
    events.append(dict(schema_version='1.0.0',event_id=str(uuid4()),action='allocate',table=table,inputs=[],outputs=[key],aliases=[dict(namespace='instrument-event-migration-2026-11-06',source_id=key,record_sha256=sha(record))],assignments=[],reviewer='coordinator',reviewed_at=stamp,
        rationale='Explicit source/event/claim/review identity for a legacy-instrument event; no new legacy instrument or identity merge.',evidence=[dict(url=source['url'],body_sha256=source['body_sha256'],locator='Direct signed-act and operative-clause PDF review')]))
registry=Path('data/identities/expanded.jsonl');identity=dict(schema_version='1.0.0',expected_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),events=events)
preview=a.scratch/'registry-preview.jsonl';preview.write_bytes(registry.read_bytes());apply_plan(preview,identity,True)
files=serialized(rows)
for table,raw in files.items():(candidate/(table+'.jsonl')).write_bytes(raw)
plan=dict(schema_version='1.0.1',validation_profile=dict(name='1.0.1',schema_sha256=cohort['profile_sha256'],semantics='event-exact-accepted-v1'),
    expected_sha256=cohort['baseline_snapshot'],registry_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),snapshot_sha256=fingerprint(files),reviewer='coordinator',reviewed_at=stamp,
    rationale='First five explicitly source-supported legacy instrument events, separating adoption/effectiveness and withholding original-term expiry/current force. Preserve all prior records and both legacy CSVs.',record_reviews=reviews)
dump=lambda name,r:(packet/name).write_text(json.dumps(r,indent=2)+'\n')
dump('identity-plan.json',identity);dump('publication-plan.json',plan);dump('visual-reviews.json',visuals)
assert all(rows[t][k]==record for t in old for k,record in old[t].items())
dump('preservation-check.json',dict(all_prior_records_unchanged=True,baseline_snapshot=cohort['baseline_snapshot'],candidate_snapshot=plan['snapshot_sha256'],events=event_summary,
    new_records_by_table={t:len(rows[t])-len(old[t]) for t in IDS},legacy_csv_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('data/moratorium_inventory.csv'),Path('data/state_legislation.csv')]}))
dump('context.json',dict(candidate=str(candidate),scratch=str(a.scratch),additional_evidence_directories=sorted(evidence_dirs),prepared_at=stamp))
print(plan['snapshot_sha256'])
