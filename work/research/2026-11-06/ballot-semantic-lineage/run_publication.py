"""Explicit preflight, identity apply, domain apply and exact replay for this packet."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path('scripts').resolve()))
from expanded_identity import apply_plan
from expanded_promotion import publish

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('phase',choices=['preflight','apply','replay'])
p.add_argument('--evidence-config',type=Path,required=True,help='Retained argv JSON supplying explicit evidence-directory roots')
a=p.parse_args();packet=Path(__file__).resolve().parent
context=json.loads((packet/'context.json').read_text());plan=json.loads((packet/'publication-plan.json').read_text())
command=json.loads(a.evidence_config.read_text());directories=[Path(command[i+1]) for i,s in enumerate(command) if s=='--evidence-directory']
assert directories,'Explicit evidence roots required'
visual={}
for path in json.loads((packet/'visual-reviews.json').read_text()):
    r=json.loads(Path(path).read_text());visual[r['claim_id']]=r
candidate=Path(context['candidate'])
if not candidate.exists():candidate=Path('data/expanded-snapshots')/plan['snapshot_sha256']
registry=Path(context['scratch'])/'registry-preview.jsonl' if a.phase=='preflight' else Path('data/identities/expanded.jsonl')
if a.phase=='apply':
    preflight=json.loads((packet/'preflight.json').read_text())
    assert preflight['state']=='ready' and preflight['sha256']==plan['snapshot_sha256']
    receipt=apply_plan(registry,json.loads((packet/'identity-plan.json').read_text()),True)
    (packet/'identity-apply.json').write_text(json.dumps(receipt,indent=2)+'\n')
result=publish(Path('data/expanded'),candidate,registry,plan,directories,a.phase!='preflight',visual,
    Path('data/moratorium_inventory.csv'),Path('data/state_legislation.csv'))
(packet/(a.phase+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(result['state'],result['sha256'])
