"""Check scoped source hashes/quotes and the exact twelve-cell canonical delta."""
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[4];PACKET=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
base_raw=subprocess.check_output(['git','show','d9c09ebfe9b6585f82e3c7d841aa2316376ec914:data/state_legislation.csv'],cwd=ROOT);after_raw=(ROOT/'data/state_legislation.csv').read_bytes()
read=lambda b:{r['policy_action_id']:r for r in csv.DictReader(io.StringIO(b.decode()))}
before,after=read(base_raw),read(after_raw);assert set(before)==set(after) and len(after)==442
expected={}
for st in ['ny','tx','tx-sb6']:
 row=json.loads((PACKET/('answers-'+st+'.json')).read_text())['decisions'][0]
 baseline=next(r for r in json.loads((PACKET/'baseline.json').read_text()) if 'TX:'+r['bill']==row['bill_key'] or 'NY:'+r['bill']==row['bill_key'])
 for field,value in row['fields'].items():expected[baseline['policy_action_id'],field]=value
changes=[]
for k,r in before.items():
 for field,value in r.items():
  if value!=after[k][field]:
   assert expected.pop((k,field))==after[k][field]
   changes.append({'policy_action_id':k,'field':field,'before':value,'after':after[k][field]})
assert not expected and len(changes)==12
versions=json.loads((PACKET/'source-versions.json').read_text())
for source in versions:
 d=a.evidence_root/source.get('evidence_subdirectory',source['state'].lower());i=source['attempt_id'];assert source['ok'] is True
 for ext,key in [('body','body_sha256'),('txt','text_sha256')]:assert sha((d/(i+'.private.'+ext)).read_bytes())==source[key]
for quote in json.loads((PACKET/'quote-proofs.json').read_text()):
 source=next(s for s in versions if s['attempt_id']==quote['attempt_id']);folder=source.get('evidence_subdirectory',source['state'].lower());ext='body' if quote.get('representation')=='original_utf8_html_body' else 'txt';text=(a.evidence_root/folder/(quote['attempt_id']+'.private.'+ext)).read_bytes().decode();_,start,end=quote['span'].split(':');assert text[int(start):int(end)]==quote['quote'];assert sha(quote['quote'].encode())==quote['quote_sha256']
visual=json.loads((PACKET/'visual-review.json').read_text())
for page in visual['pages']:assert sha((a.evidence_root/'tx'/('letter-'+str(page['physical_page'])+'.png')).read_bytes())==page['render_sha256']
report={'baseline_commit':'d9c09ebfe9b6585f82e3c7d841aa2316376ec914','before_csv_sha256':sha(base_raw),'after_csv_sha256':sha(after_raw),'all_442_ids_preserved':True,'all_unlisted_cells_unchanged':True,'changes':changes,'source_versions_verified':len(versions),'quote_spans_verified':len(json.loads((PACKET/'quote-proofs.json').read_text())),'visual_page_hashes_verified':2,'legal_effect_before':dict(Counter(r['legal_effect_status'] for r in before.values())),'legal_effect_after':dict(Counter(r['legal_effect_status'] for r in after.values())),'scope':'Exact data delta and source-integrity checks only; no independent legal conclusion or all-field/current-force acceptance.'}
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='changes'},indent=2))
