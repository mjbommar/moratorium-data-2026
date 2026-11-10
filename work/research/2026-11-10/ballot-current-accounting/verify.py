"""Pin current ballot accounting without renewing substantive reviews."""
import collections,datetime,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[4];out=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads((root/p).read_text())
rows=lambda f:[json.loads(x) for x in (root/'data/expanded'/f).read_text().splitlines()]
measures=rows('ballot_measures.jsonl');results=rows('measure_results.jsonl');superseded={r['supersedes_id'] for r in results if r['supersedes_id']};current=[r for r in results if r['result_observation_id'] not in superseded]
prior=load('work/research/2026-11-08/ballot-current-accounting/measure-dispositions.json')['measures'];byid={r['measure_id']:r for r in measures};assert len(prior)==len(byid)==57
changes=[]
for r in prior:
 ident=r['measure_id'];assert sha(json.dumps(byid[ident],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==r['canonical_row_sha256']
 now=sorted(x['result_observation_id'] for x in current if x['measure_id']==ident)
 if now!=sorted(r['current_result_observation_ids']):changes.append({'measure_id':ident,'prior_current_result_ids':r['current_result_observation_ids'],'current_result_ids':now})
assert len(changes)==1
j={r['jurisdiction_id']:r for r in rows('jurisdictions.jsonl')};assert 'Canterbury' in str(j[byid[changes[0]['measure_id']]['jurisdiction_id']])
counts={'measures':len(measures),'retained_result_versions':len(results),'current_result_observations':len(current),'measures_with_current_results':len({r['measure_id'] for r in current}),'measures_without_current_results':len(byid.keys()-{r['measure_id'] for r in current}),'current_certification_status_counts':dict(collections.Counter(r['certification_status'] for r in current)),'lifecycle_counts':dict(collections.Counter(r['lifecycle'] for r in measures))};assert (len(results),len(current),counts['measures_with_current_results'])==(65,53,52) and counts['current_certification_status_counts']['certified']==5
pins=['data/expanded/ballot_measures.jsonl','data/expanded/measure_results.jsonl','data/expanded/publication.json','work/research/2026-11-08/ballot-current-accounting/measure-dispositions.json','work/research/2026-11-10/canterbury-minutes-result-review/coordinator-adjudication.json','work/research/2026-11-10/post-release-qa/bethel-official-minutes-review.json']
r={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':counts,'all57_prior_measure_row_guards_matched':True,'changed_current_result_id_sets':changes,'input_pins':{f:sha((root/f).read_bytes()) for f in pins},'scope':'Current accounting; all prior measure identities retained. Canterbury replacement observation already published; Bethel later board research action adds no result, certification or operative-law acceptance. No new source freshness or census claim.'};(out/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(counts,indent=2))
