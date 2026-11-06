"""Explicit unapplied-candidate refinements after the two source-image reviews."""
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

packet=Path(__file__).resolve().parent
assert not (packet/'refinement.json').exists(), 'Refined once; do not silently regenerate identities'
context=json.loads((packet/'context.json').read_text());candidate=Path(context['candidate'])
rows={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(candidate).items()}
old={t:{r[IDS[t]]:r for r in map(json.loads,raw.decode().splitlines())} for t,raw in read_snapshot(Path('data/expanded')).items()}
plan=json.loads((packet/'publication-plan.json').read_text());identity=json.loads((packet/'identity-plan.json').read_text())
original_candidate_hash=plan['snapshot_sha256'];stamp=dt.datetime.now(dt.timezone.utc).isoformat()
sha=lambda record:hashlib.sha256(encode(record).encode()).hexdigest()
visual_sha=lambda record:hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
visuals=json.loads((packet/'visual-reviews.json').read_text())
check=json.loads((packet/'preservation-check.json').read_text())
wright=next(r for r in check['mechanism_replacements'] if r['name']=='wrightstown')
wclaim=rows['claims'][wright['new_claim_id']]
wclaim['span']='pdf-pages:1-2'
wclaim['extraction_provenance']+=' The continued question also covers public-facing video, telecommunications and Internet-access facility operations; the classification does not erase those service qualifications.'
image=Path('/tmp/moratorium-lineage-9887e14807de-2.png')
for path in visuals:
    path=Path(path)
    if path.parent!=packet and path.parent.resolve()!=packet.resolve():continue
    receipt=json.loads(path.read_text());claim=rows['claims'][receipt['claim_id']]
    receipt['claim_sha256']=visual_sha(claim)
    if claim['claim_id']==wclaim['claim_id']:
        receipt['additional_pdf_pages']=[dict(page=2,dpi=150,render_sha256=hashlib.sha256(image.read_bytes()).hexdigest())]
    path.write_text(json.dumps(receipt,indent=2)+'\n')

added=[]
def add(table,record):
    key=record[IDS[table]];assert key not in rows[table];rows[table][key]=record;added.append((table,key));return key

def current(table,key,field):
    ds=old['review_decisions'].values();sup={d['supersedes_id'] for d in ds if d['supersedes_id']}
    found=[d for d in ds if d['target']==dict(table=table,id=key) and d['scope']==field and d['decision_id'] not in sup]
    assert len(found)==1;return found[0]['decision_id']

def decision(target,scope,cid,reason,disposition='accepted',supersedes=None):
    return add('review_decisions',dict(schema_version='1.0.0',decision_id=str(uuid4()),target=target,
        scope=scope,claim_ids=[cid],disposition=disposition,reviewer='coordinator',method='direct retained source-role and PDF-page review',
        rationale=reason,decided_at=stamp,supersedes_id=supersedes))

wp=rows['measure_provisions'][wright['provision_id']]
wp['geography']='Proposed municipal infrastructure/services associated with development within or affecting the Village of Wrightstown; final ballot and operative restriction territory unverified.'
cid=str(uuid4());claim=dict(schema_version='1.0.0',claim_id=cid,subject=dict(table='measure_provisions',id=wp['provision_id']),
    predicate='geography',value=wp['geography'],source_document_id=wclaim['source_document_id'],quote=None,span='pdf-pages:1-2',
    temporal_support=dict(earliest=None,latest=None,precision='unknown',original_text=None),
    extraction_provenance='Coordinator direct physical pages1–2 review of reproduced referral: development within or affecting village; proposed public infrastructure/service question only. Final printed ballot, actual restriction territory and legal force remain unverified.')
add('claims',claim);wp['claim_ids'].append(cid)
decision(dict(table='claims',id=cid),'geography',cid,'Source-role qualification of reproduced proposal; no final ballot or enacted territory inference.')
decision(claim['subject'],'geography',cid,'Replace overly narrow village-only geography with proposed service/development scope, preserving final-wording and legal-force gaps.',supersedes=current('measure_provisions',wp['provision_id'],'geography'))
receipt=json.loads((packet/(wclaim['claim_id']+'-visual-review.json')).read_text());receipt.update(claim_id=cid,claim_sha256=visual_sha(claim),values=claim['value'],reviewed_at=stamp)
path=packet/(cid+'-visual-review.json');path.write_text(json.dumps(receipt,indent=2)+'\n');visuals.append(str(path))
bloom=next(r for r in check['mechanism_replacements'] if r['name']=='bloomington');bp=rows['measure_provisions'][bloom['provision_id']]
bp['geography']=None
decision(dict(table='measure_provisions',id=bp['provision_id']),'geography',bloom['new_claim_id'],
    'Specimen establishes an advisory request to the City of Bloomington; it does not establish the territory of a resulting restriction. Separate township electorate is not restriction territory. Withhold geography until source-qualified territorial support is reviewed.',
    disposition='unresolved',supersedes=current('measure_provisions',bp['provision_id'],'geography'))

for table,key in added:
    record=rows[table][key]
    source=rows['source_documents'][record['source_document_id']] if table=='claims' else rows['source_documents'][rows['claims'][record['claim_ids'][0]]['source_document_id']]
    identity['events'].append(dict(schema_version='1.0.0',event_id=str(uuid4()),action='allocate',table=table,inputs=[],outputs=[key],
        aliases=[dict(namespace='ballot-semantic-lineage-2026-11-06',source_id=key,record_sha256=sha(record))],assignments=[],reviewer='coordinator',reviewed_at=stamp,
        rationale='Source-review refinement before application: explicit proposed geography or withheld restriction territory.',evidence=[dict(url=source['url'],body_sha256=source['body_sha256'],locator='Scoped PDF review; all prior identities and history retained.')]))
for event in identity['events']:
    for alias in event['aliases']:alias['record_sha256']=sha(rows[event['table']][event['outputs'][0]])
preview=Path(context['scratch'])/'registry-preview.jsonl';preview.write_bytes(Path('data/identities/expanded.jsonl').read_bytes());apply_plan(preview,identity,True)
files=serialized(rows)
for table,raw in files.items():(candidate/(table+'.jsonl')).write_bytes(raw)
reviews={(r['table'],r['id']):r for r in plan['record_reviews']}
for table,key in added:
    record=rows[table][key];fields=set(record)-{IDS[table],'schema_version'}
    unresolved={f for f in fields if record[f] is None or record[f]==dict(earliest=None,latest=None,precision='unknown',original_text=None)}
    reviews[table,key]=dict(table=table,id=key,record_sha256=sha(record),previous_sha256=None,accepted_fields=sorted(fields-unresolved),unresolved_fields=sorted(unresolved),publication='reviewed_metadata')
for (table,key),review in reviews.items():review['record_sha256']=sha(rows[table][key])
review=reviews['measure_provisions',bp['provision_id']];review['accepted_fields']=[f for f in review['accepted_fields'] if f!='geography'];review['unresolved_fields']=sorted(set(review['unresolved_fields']+['geography']))
plan.update(snapshot_sha256=fingerprint(files),registry_sha256=hashlib.sha256(preview.read_bytes()).hexdigest(),record_reviews=list(reviews.values()),reviewed_at=stamp)
check.update(candidate_snapshot=plan['snapshot_sha256'],changed_existing_records=[dict(table=t,id=k,fields=sorted(f for f in rows[t][k] if rows[t][k].get(f)!=v.get(f))) for t in old for k,v in old[t].items() if rows[t][k]!=v],
    new_records_by_table={t:len(rows[t])-len(old[t]) for t in IDS},new_claim_ids=sorted(set(rows['claims'])-set(old['claims'])))
for name,value in [('publication-plan.json',plan),('identity-plan.json',identity),('visual-reviews.json',visuals),('preservation-check.json',check),
                   ('refinement.json',dict(initial_candidate_snapshot=original_candidate_hash,refined_candidate_snapshot=plan['snapshot_sha256'],refined_at=stamp,
                    reason='Source-image reviews: preserve full Wrightstown continuation/services and within-or-affecting scope; withhold Bloomington restriction territory; repair receipt-only encoding mismatch.',new_record_ids=added))]:
    (packet/name).write_text(json.dumps(value,indent=2)+'\n')
print(plan['snapshot_sha256'])
