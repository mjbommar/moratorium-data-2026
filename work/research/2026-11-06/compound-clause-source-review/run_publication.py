"""Explicit preview, identity apply, domain apply or exact replay for this source-clause cohort."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path('scripts').resolve()))
from expanded_identity import apply_plan
from expanded_promotion import publish
p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['preflight','apply','replay']);a=p.parse_args()
packet=Path(__file__).resolve().parent;context=json.loads((packet/'context.private.json').read_text());plan=json.loads((packet/'publication-plan.json').read_text())
roots=[];visual={}
if a.phase!='replay':
 config=Path(context['evidence_config']);assert hashlib.sha256(config.read_bytes()).hexdigest()==json.loads((packet/'source-preflight.json').read_text())['evidence_config_sha256']
 roots=list(map(Path,json.loads(config.read_text())))
 for path in json.loads((packet/'visual-reviews.json').read_text()):
  r=json.loads(Path(path).read_text());visual[r['claim_id']]=r
candidate=Path(context['candidate'])
if a.phase=='replay' or not candidate.exists():
 applied=json.loads((packet/'apply.json').read_text());candidate=Path('data/expanded-snapshots')/applied['generation_id']
registry=Path(context['scratch'])/'registry-preview.jsonl' if a.phase=='preflight' else Path('data/identities/expanded.jsonl')
if a.phase=='apply':
 preview=json.loads((packet/'preflight.json').read_text());assert preview['state']=='ready' and preview['sha256']==plan['snapshot_sha256']
 receipt=apply_plan(registry,json.loads((packet/'identity-plan.json').read_text()),True)
 (packet/'identity-apply.json').write_text(json.dumps(receipt,indent=2)+'\n')
result=publish(Path('data/expanded'),candidate,registry,plan,roots,a.phase!='preflight',visual,Path('data/moratorium_inventory.csv'),Path('data/state_legislation.csv'))
(packet/(a.phase+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
