import csv,io,json,hashlib,subprocess,collections
from pathlib import Path
baseline='dbaab04d84f8d679ba5a3d57bf45f32186109222'
report={'baseline_commit':baseline,'current_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'scope':'Working inventory comparison, not a public-release comparison or complete legal-force verification. Ballot measures have a separate denominator.','tables':{}}
for name,filename,key,status in [('local','moratorium_inventory.csv','moratorium_id','enacted_status'),('state_policy','state_legislation.csv','policy_action_id','bill_status_category')]:
 p=Path('data')/filename
 before=subprocess.check_output(['git','show',baseline+':'+str(p)])
 after=p.read_bytes()
 def parse(b):
  rows=list(csv.DictReader(io.StringIO(b.decode())))
  indexed={r[key]:r for r in rows}
  assert len(indexed)==len(rows)
  return indexed
 a,b=parse(before),parse(after)
 changed=[{'record_id':i,'fields':{f:{'before':a[i][f],'after':b[i][f]} for f in a[i] if a[i][f]!=b[i][f]}} for i in sorted(a.keys()&b.keys()) if a[i]!=b[i]]
 report['tables'][name]={'path':str(p),'baseline_sha256':hashlib.sha256(before).hexdigest(),'current_sha256':hashlib.sha256(after).hexdigest(),'before_total':len(a),'after_total':len(b),'before_status_counts':dict(collections.Counter(r[status] for r in a.values())),'after_status_counts':dict(collections.Counter(r[status] for r in b.values())),'added_ids':sorted(b.keys()-a.keys()),'removed_ids':sorted(a.keys()-b.keys()),'changed_existing_records':changed}
registry=Path('data/identities/legacy-moratoria.jsonl')
if registry.exists():
 from legacy_moratorium_identity import load_aliases
 current_ids={r['moratorium_id'] for r in csv.DictReader(Path('data/moratorium_inventory.csv').open())}
 aliases=load_aliases(Path('data/moratorium_inventory.csv'),current_ids)
 removed=report['tables']['local']['removed_ids']
 assert all(i in aliases for i in removed), 'Unexplained baseline ID removal'
 report['legacy_identity_retirements']={'path':str(registry),'sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),'aliases':aliases,'removed_baseline_ids':removed,'scope':'Explicit duplicate retirements; original IDs and full row observations retained. Historical baseline count is not backcast.'}
projection=Path('work/research/2026-11-05/ballot-census-review/canonical-projection-status.json')
p=json.loads(projection.read_text());snap=Path('data/expanded').resolve()
assert p['canonical_snapshot']==snap.name
report['ballot_scope']={'snapshot':snap.name,'projection_path':str(projection),'projection_sha256':hashlib.sha256(projection.read_bytes()).hexdigest(),**p['summary'],'canonical_table_counts':{f.stem:len(f.read_text().splitlines()) for f in sorted(snap.glob('*.jsonl'))}}
out=Path('work/audit/refresh-baseline-delta-2026-11-06.json');out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:{f:v[f] for f in ['before_total','after_total','before_status_counts','after_status_counts','added_ids','removed_ids']} for k,v in report['tables'].items()},indent=2))
