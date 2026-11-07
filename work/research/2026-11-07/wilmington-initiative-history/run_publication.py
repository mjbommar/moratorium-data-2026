"""Run preflight, apply, or replay; apply/replay require explicit future authorization."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];packet=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'scripts'))
from expanded_identity import apply_plan
from expanded_promotion import publish
p=argparse.ArgumentParser();p.add_argument('phase',choices=['preflight','apply','replay']);a=p.parse_args()
context=json.loads((packet/'context.private.json').read_text());plan=json.loads((packet/'publication-plan.json').read_text());roots=[];visual={}
if a.phase!='replay':
 config=Path(context['evidence_config']);assert hashlib.sha256(config.read_bytes()).hexdigest()==json.loads((packet/'source-preflight.json').read_text())['evidence_config_sha256']
 roots=list(map(Path,json.loads(config.read_text())))+[Path(context['extra_evidence'])]
 for name in json.loads((packet/'visual-reviews.json').read_text()):
  path=Path(name);path=path if path.is_absolute() else ROOT/path
  r=json.loads(path.read_text());visual[r['claim_id']]=r
candidate=Path(context['candidate'])
if a.phase=='replay':candidate=ROOT/'data/expanded-snapshots'/json.loads((packet/'apply.json').read_text())['generation_id']
registry=Path(context['scratch'])/'registry-preview.jsonl' if a.phase=='preflight' else ROOT/'data/identities/expanded.jsonl'
if a.phase=='apply':
 pre=json.loads((packet/'preflight.json').read_text());assert pre['state']=='ready' and pre['sha256']==plan['snapshot_sha256']
 receipt=apply_plan(registry,json.loads((packet/'identity-plan.json').read_text()),True);(packet/'identity-apply.json').write_text(json.dumps(receipt,indent=2)+'\n')
result=publish(ROOT/'data/expanded',candidate,registry,plan,roots,a.phase!='preflight',visual,ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv')
(packet/(a.phase+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
