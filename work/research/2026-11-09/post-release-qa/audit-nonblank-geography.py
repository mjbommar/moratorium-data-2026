#!/usr/bin/env python3
"""Screen existing map points against retained Census captures; never edits inputs."""
from pathlib import Path
import csv,io,json,hashlib,zipfile,math,datetime,argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--captures',type=Path,required=True);parser.add_argument('--inventory',type=Path,default=Path('data/moratorium_inventory.csv'));parser.add_argument('--output',type=Path,required=True);parser.add_argument('--details',type=Path,required=True);args=parser.parse_args();capture=args.captures;sha=lambda b:hashlib.sha256(b).hexdigest();tables={};sources=[]
for kind in ['counties','cousubs','place']:
 d=json.load(open(capture/(kind+'.private.json')));body=Path(d['artifact']).with_suffix('.body').read_bytes();assert sha(body)==d['body_sha256'];member='2026_Gaz_'+kind+'_national.txt';raw=zipfile.ZipFile(io.BytesIO(body)).read(member);tables[kind]=[{k.strip():v.strip() for k,v in r.items()} for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='|')];sources.append(dict(kind=kind,url=d['url'],body_sha256=sha(body),member=member,member_sha256=sha(raw),observed_at=d['body_observed_at']))
def distance(a,b):
 la,lo,lb,lob=map(math.radians,[*a,*b]);q=math.sin((lb-la)/2)**2+math.cos(la)*math.cos(lb)*math.sin((lob-lo)/2)**2;return 6371*2*math.asin(min(1,math.sqrt(q)))
index={kind:{} for kind in tables}
for kind,rows in tables.items():
 for r in rows:index[kind].setdefault((r['USPS'],r['NAME'].casefold()),[]).append(r)
records=[];flags=[]
for r in csv.DictReader(args.inventory.open()):
 if not r['latitude'].strip() or not r['longitude'].strip():continue
 typ=r['jurisdiction_type'];name=r['jurisdiction'];state=r['state_abbrev']
 if typ in ['County','Parish']:kind='counties'
 elif typ=='Township' or (typ=='Town' and state in ['CT','MA','ME','NH','NJ','NY','RI','VT','WI']):kind='cousubs'
 elif typ in ['City','Village','Town','Borough','Municipality']:kind='place'
 else:records.append(dict(id=r['moratorium_id'],decision='unsupported_type',type=typ));continue
 base=name
 for prefix in ['City of ','Town of ','Village of ','Township of ']:
  if base.startswith(prefix):base=base[len(prefix):]
 names={name.casefold(),base.casefold(),(base+' '+typ.lower()).casefold()}
 if typ=='Township':names.add(base.replace(' Township',' charter township').casefold())
 candidates={x['GEOID']:x for n in names for x in index[kind].get((state,n),[])}
 if len(candidates)!=1:records.append(dict(id=r['moratorium_id'],decision='ambiguous_or_unmatched',candidate_count=len(candidates),table=kind));continue
 x=next(iter(candidates.values()));old=(float(r['latitude']),float(r['longitude']));new=(float(x['INTPTLAT']),float(x['INTPTLONG']));km=distance(old,new);radius=math.sqrt((float(x['ALAND'])+float(x['AWATER']))/1e6/math.pi);threshold=max(25,3*radius);rec=dict(id=r['moratorium_id'],decision='large_displacement_candidate' if km>threshold else 'within_conservative_screen',table=kind,candidate_count=1,old_latitude=r['latitude'],old_longitude=r['longitude'],distance_km=round(km,3),threshold_km=round(threshold,3),census_record=x,current_row_sha256=sha(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()));records.append(rec)
 if km>threshold:flags.append(rec)
result=dict(reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),inventory_sha256=sha(args.inventory.read_bytes()),sources=sources,scope='New read-only screen of nonblank coordinates, distinct from earlier missing-point review. Strict state/name/type unique matches only. Threshold max25km or3 area-equivalent radii identifies candidates, not confirmed errors or boundary/applicability determinations. No network requests or canonical mutations.',nonblank_points=len(records),unique_comparisons=sum('distance_km' in r for r in records),unmatched_or_unsupported=sum('distance_km' not in r for r in records),flagged_candidates=flags)
args.details.write_text(json.dumps(records,indent=2)+'\n');args.output.write_text(json.dumps(result,indent=2)+'\n');print('Nonblank',len(records),'unique',result['unique_comparisons'],'flagged',len(flags))
for r in flags:print(r['id'],r['distance_km'],r['threshold_km'],r['census_record']['GEOID'],r['census_record']['NAME'])
