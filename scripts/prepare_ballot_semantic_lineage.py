"""Prepare this explicitly reviewed correction in ephemeral scratch; never apply.

Source bodies stay private. Existing immutable rows are retained. Publication
and identity application require their independent explicit gates.
"""
import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from expanded_identity import encode, apply_plan
from expanded_promotion import IDS, read_snapshot, serialized, fingerprint


def prepare(scratch, packet):
    if (packet/'context.json').exists():
        raise ValueError('Prepared once; inspect retained context rather than reallocating IDs')
    scratch.mkdir(parents=True,exist_ok=True);packet.mkdir(parents=True,exist_ok=True)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    sha=lambda record:hashlib.sha256(encode(record).encode()).hexdigest()
    old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())}
         for t,raw in read_snapshot(Path('data/expanded')).items()}
    rows=copy.deepcopy(old)
    prior=json.loads((Path('data/expanded').resolve()/'publication.json').read_text())
    prior_reviews={(r['table'],r['id']):r for r in prior['plan']['record_reviews']}
    superseded={d['supersedes_id'] for d in old['review_decisions'].values() if d['supersedes_id']}
    visuals=json.loads(Path('work/research/2026-11-06/el-dorado-sector-lineage/visual-reviews.json').read_text())
    visual_by_claim={json.loads(Path(p).read_text())['claim_id']:json.loads(Path(p).read_text()) for p in visuals}
    new_records=[];visual_new=[];replacements=[]

    def add(table,record):
        key=record[IDS[table]];assert key not in rows[table]
        rows[table][key]=record;new_records.append((table,key));return key

    def decision(target,scope,cids,reason,previous=None):
        return add('review_decisions',dict(schema_version='1.0.0',decision_id=str(uuid4()),
            target=target,disposition='accepted',scope=scope,claim_ids=cids,reviewer='coordinator',
            method='scoped retained primary-PDF visual review',rationale=reason,
            decided_at=stamp,supersedes_id=previous))

    def visual(claim,page):
        source=rows['source_documents'][claim['source_document_id']]
        image=Path(f"/tmp/moratorium-lineage-{source['body_sha256'][:12]}-{page}.png")
        receipt=dict(claim_id=claim['claim_id'],source_document_id=claim['source_document_id'],
            claim_sha256=hashlib.sha256(json.dumps(claim,sort_keys=True,separators=(',',':')).encode()).hexdigest(),disposition='accepted_visual_values',reviewer='coordinator',
            values=claim['value'],source_body_sha256=source['body_sha256'],pdf_page=page,
            render_parameters=dict(renderer='pdftoppm',page=page,dpi=150),
            render_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),reviewed_at=stamp)
        target=packet/(claim['claim_id']+'-visual-review.json')
        target.write_text(json.dumps(receipt,indent=2)+'\n');visual_new.append(str(target))

    def claim(target,predicate,value,source,page,reason):
        record=dict(schema_version='1.0.0',claim_id=str(uuid4()),subject=target,
            predicate=predicate,value=value,source_document_id=source,quote=None,
            span=f'pdf-page:{page}',temporal_support=dict(earliest=None,latest=None,precision='unknown',original_text=None),
            extraction_provenance=reason)
        cid=add('claims',record);visual(record,page)
        decision(dict(table='claims',id=cid),predicate,[cid],reason)
        return cid

    cases=[
        ('wrightstown','6dd428e5-1d3d-46d6-96ae-67739e34c087','f6887bdc-3d75-463f-8a4d-d6fc9a749423',1,
         'Coordinator direct review of reproduced resolution physical pages1–2: proposed advisory question concerns municipal infrastructure/services for large-scale development within or affecting the village. Classification applies to the reproduced proposed question, not an authenticated final printed ballot or blanket development approval. Page2 expressly excludes automatic contracts, expenditures, zoning approval, development agreement or utility extension.'),
        ('downe','ce0de8ba-df24-44f7-877c-a33ba3d9636a','6033a140-bc81-4750-b3cc-acc37a1c02de',1,
         'Coordinator direct sample-ballot page1 review: question asks support for data centers and interpretive statement gauges public sentiment. Advisory permission/support classification only; no ban or project authorization follows automatically and separate ordinance history remains unresolved.'),
        ('joliet','e0399024-e210-438e-9fad-6b1e4d6428dd','535c74ff-254b-4859-899f-2d0ad8d25436',1,
         'Coordinator direct county-clerk notice page1 review: advisory question asks Joliet Township voters whether the separate Joliet City Council should approve AI data-center construction. Development-support proposition, not actual council approval, territory equivalence or legal authorization.'),
        ('bloomington','f6a0b566-7810-4157-acbc-3d8f911db1b1','1a5a272e-2344-4c4f-b960-e5ff3eab0ab8',3,
         'Coordinator direct specimen page3 review: advisory question asks the City of Bloomington to implement a large-scale data-center moratorium. Development-opposition proposition, not a winning-side label, actual enactment, certification or township-city territory equivalence.'),
    ]
    for name,pid,sid,page,reason in cases:
        provision=rows['measure_provisions'][pid];target=dict(table='measure_provisions',id=pid)
        cid=claim(target,'mechanism',provision['mechanism'],sid,page,reason)
        current=[d for d in old['review_decisions'].values() if d['target']==target and d['scope']=='mechanism' and d['decision_id'] not in superseded]
        assert len(current)==1 and current[0]['disposition']=='accepted'
        decision(target,'mechanism',[cid],reason,current[0]['decision_id'])
        provision['claim_ids'].append(cid)
        replacements.append(dict(name=name,provision_id=pid,new_claim_id=cid,superseded_decision_id=current[0]['decision_id']))

    old_result_id='bbe595d2-2bb8-4bce-ae92-e65d467781a3'
    old_result=old['measure_results'][old_result_id];new_result=copy.deepcopy(old_result)
    rid=str(uuid4());new_result.update(result_observation_id=rid,observed_at=stamp,supersedes_id=old_result_id,
        reporting_scope=dict(kind='jurisdiction_total',description='City of Monterey Park Measure NDC: grand total in the final official contest canvass, including precinct and vote-by-mail totals.'))
    target=dict(table='measure_results',id=rid);claim_map={}
    for cid,original in old['claims'].items():
        if original['subject']!={'table':'measure_results','id':old_result_id}:continue
        cloned=copy.deepcopy(original);cloned.update(claim_id=str(uuid4()),subject=target,
            extraction_provenance=original['extraction_provenance']+' Retained value/evidence rebound to explicit scope-correction successor; no changed numeric value, certification phase or legal effect.')
        new_cid=add('claims',cloned);claim_map[cid]=new_cid
        decision(dict(table='claims',id=new_cid),cloned['predicate'],[new_cid],
            'Preserve the previously reviewed source assertion under the scope-corrected result identity; unchanged source version/value. Full source/evidence preflight required.')
        if cid in visual_by_claim:
            receipt=copy.deepcopy(visual_by_claim[cid]);receipt.update(claim_id=new_cid,claim_sha256=hashlib.sha256(json.dumps(cloned,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            receipt['rebound_from_claim_id']=cid
            path=packet/(new_cid+'-visual-review.json');path.write_text(json.dumps(receipt,indent=2)+'\n');visual_new.append(str(path))
    for method in new_result['value_methods'].values():method['claim_ids']=[claim_map[c] for c in method['claim_ids']]
    reason='Coordinator direct physical pages1,4,6,8 review: page8 is a final official City of Monterey Park Measure NDC contest statement with a grand total and separate precinct/VBM totals. This supports count completion at city-total scope independently of the separately retained county June26 and city-clerk June30 certification phases. No later amendment search, current legal force, changed count or new certification is asserted.'
    support=claim(target,'reporting_completion_scope',dict(reporting_status='complete',reporting_scope=new_result['reporting_scope']),
                  'f05687d3-775e-4e35-a52b-2cbe0f391fdb',8,reason)
    for field in ['reporting_status','reporting_scope']:
        new_result['value_methods'][field]=dict(method='visual',claim_ids=[support],note='Final official city-labelled Measure NDC contest grand-total canvass, physical page8; count completion and scope, not certification inferred from precinct reporting.')
    add('measure_results',new_result)
    current=[d for d in old['review_decisions'].values() if d['target']=={'table':'measure_results','id':old_result_id} and d['decision_id'] not in superseded]
    for original in current:
        assert original['disposition']=='accepted'
        field=original['scope'];cids=[claim_map[c] for c in original['claim_ids']]
        if field in ['reporting_status','value_methods']:cids=[support] if field=='reporting_status' else sorted(set(cids+[support]))
        decision(target,field,cids,reason if field in ['reporting_status','value_methods','observed_at','supersedes_id'] else
            'Retain previously reviewed field value in explicit scope-correction successor; source assertions rebound to this observation. No renewed current-force acceptance.')
    for field in ['reporting_scope','supersedes_id']:
        if not any(d['scope']==field for d in current):decision(target,field,[support],reason)
    files=serialized(rows)
    candidate=scratch/'candidate';candidate.mkdir(exist_ok=True)
    for table,raw in files.items():(candidate/(table+'.jsonl')).write_bytes(raw)
    reviews=[]
    for table,records in rows.items():
        for key,record in records.items():
            if key in old[table]:
                review=copy.deepcopy(prior_reviews[table,key]);review.update(record_sha256=sha(record),previous_sha256=sha(old[table][key]))
            elif table=='measure_results':
                review=copy.deepcopy(prior_reviews[table,old_result_id]);review.update(id=key,record_sha256=sha(record),previous_sha256=None)
                for field in ['reporting_scope','supersedes_id']:
                    review['unresolved_fields']=[f for f in review['unresolved_fields'] if f!=field]
                    review['accepted_fields']=sorted(set(review['accepted_fields']+[field]))
            else:
                fields=set(record)-{IDS[table],'schema_version'}
                unresolved={f for f in fields if record[f] is None or record[f]==dict(earliest=None,latest=None,precision='unknown',original_text=None)}
                review=dict(table=table,id=key,record_sha256=sha(record),previous_sha256=None,
                    accepted_fields=sorted(fields-unresolved),unresolved_fields=sorted(unresolved),publication='reviewed_metadata')
            reviews.append(review)
    events=[]
    for table,key in new_records:
        record=rows[table][key]
        evidence_claim=record if table=='claims' else rows['claims'][record['claim_ids'][0]] if table=='review_decisions' else rows['claims'][support]
        source=rows['source_documents'][evidence_claim['source_document_id']]
        events.append(dict(schema_version='1.0.0',event_id=str(uuid4()),action='allocate',table=table,inputs=[],outputs=[key],
            aliases=[dict(namespace='ballot-semantic-lineage-2026-11-06',source_id=key,record_sha256=sha(record))],assignments=[],
            reviewer='coordinator',reviewed_at=stamp,rationale='Explicit evidence-lineage correction; preserve old identities and immutable history.',
            evidence=[dict(url=source['url'],body_sha256=source['body_sha256'],locator='Scoped retained-source visual review and correction packet; no inferred legal force.')]))
    registry=Path('data/identities/expanded.jsonl')
    identity=dict(schema_version='1.0.0',expected_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),events=events)
    preview=scratch/'registry-preview.jsonl';preview.write_bytes(registry.read_bytes());apply_plan(preview,identity,True)
    plan=dict(schema_version='1.0.0',expected_sha256=Path('data/expanded').resolve().name,
        registry_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),snapshot_sha256=fingerprint(files),reviewer='coordinator',reviewed_at=stamp,
        rationale='Explicit mechanism claim support for four unchanged advisory classifications, plus an immutable Monterey Park successor recording city-total completion/scope. Retain every prior row, source version, vote and certification phase; no legal-force acceptance.',record_reviews=reviews)
    dump=lambda name,value:(packet/name).write_text(json.dumps(value,indent=2)+'\n')
    dump('identity-plan.json',identity);dump('publication-plan.json',plan);dump('visual-reviews.json',visuals+visual_new)
    changed=[dict(table=t,id=k,fields=sorted(f for f in rows[t][k] if rows[t][k].get(f)!=v.get(f)))
             for t in old for k,v in old[t].items() if rows[t][k]!=v]
    assert len(changed)==4 and all(r['table']=='measure_provisions' and r['fields']==['claim_ids'] for r in changed)
    dump('preservation-check.json',dict(baseline_snapshot=plan['expected_sha256'],candidate_snapshot=plan['snapshot_sha256'],
        retained_immutable_records_unchanged=all(rows[t][k]==v for t in old if t not in ['measure_provisions'] for k,v in old[t].items()),
        changed_existing_records=changed,mechanism_replacements=replacements,old_result_id=old_result_id,new_result_id=rid,
        unchanged_vote_and_certification_values=all(new_result[k]==v for k,v in old_result.items() if k not in ['result_observation_id','observed_at','supersedes_id','value_methods']),
        new_records_by_table={t:sum(table==t for table,_ in new_records) for t in IDS},new_claim_ids=[k for t,k in new_records if t=='claims']))
    dump('context.json',dict(prepared_at=stamp,baseline_snapshot=plan['expected_sha256'],scratch=str(scratch),candidate=str(candidate),new_result_id=rid))
    print(json.dumps(dict(candidate=str(candidate),snapshot=plan['snapshot_sha256'],new_records=len(new_records))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',type=Path,required=True);p.add_argument('--packet',type=Path,required=True)
    a=p.parse_args();prepare(a.scratch,a.packet)
