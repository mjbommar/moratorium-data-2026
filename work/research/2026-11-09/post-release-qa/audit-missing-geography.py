#!/usr/bin/env python3
"""Prepare candidates only: Census internal points do not prove legal coverage."""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('captures',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
tables={};sources=[]
for kind in ('counties','cousubs','place'):
 receipt=json.loads((a.captures/f'{kind}.private.json').read_text());assert receipt['ok']
 body=Path(receipt['artifact']).with_suffix('.body').read_bytes();assert sha(body)==receipt['body_sha256']
 z=zipfile.ZipFile(io.BytesIO(body));member=f'2026_Gaz_{kind}_national.txt';raw=z.read(member)
 tables[kind]=[{k.strip():v.strip() for k,v in r.items()} for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='|')]
 sources.append({'kind':kind,'url':receipt['url'],'body_sha256':sha(body),'member':member,'member_sha256':sha(raw),'observed_at':receipt['body_observed_at']})
inv=Path('data/moratorium_inventory.csv');rows=list(csv.DictReader(inv.open()));out=[]
for r in rows:
 if r['latitude'].strip() and r['longitude'].strip():continue
 name=r['jurisdiction'];typ=r['jurisdiction_type'];state=r['state_abbrev'];kind='place'
 if 'Aggregate' in typ: candidates=[];kind=None
 else:
  if typ in ('County','Parish'):kind='counties';names={name}
  elif typ=='Township' or (typ=='Town' and state in ('ME','NY','NJ')):
   kind='cousubs';names={name,name+' town',name+' township',name.replace(' Township',' charter township')}
  else:
   base=re.sub(r'^Town of ','',name);names={base,base+' '+typ.lower()}
   if state=='MA':names.add(base+' Town city')
  candidates=[x for x in tables[kind] if x['USPS']==state and x['NAME'].casefold() in {n.casefold() for n in names}]
 out.append({'id':r['moratorium_id'],'jurisdiction':name,'type':typ,'state':state,'row_sha256':sha(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),'table':kind,'candidate_count':len(candidates),'candidates':candidates,'decision':'candidate_only_requires_identity_review' if candidates else 'unmatched_or_aggregate'})
result={'schema':'missing-geography-candidates-v1','inventory_sha256':sha(inv.read_bytes()),'scope':'Missing coordinates only. Exact state/name/type candidates; no canonical edits or QA closures. Internal points are neither boundaries nor project locations. Unique matches still require identity review.','sources':sources,'records':out,'counts':{'missing':len(out),'unique_candidates':sum(x['candidate_count']==1 for x in out),'ambiguous_candidates':sum(x['candidate_count']>1 for x in out),'unmatched':sum(x['candidate_count']==0 for x in out)}}
a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result['counts']))
for x in out:
 if x['candidate_count']!=1:print(x['id'],x['candidate_count'],[c['NAME'] for c in x['candidates']])
