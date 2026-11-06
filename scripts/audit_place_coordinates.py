#!/usr/bin/env python3
"""Flag exact-name municipal point discrepancies; never infer legal applicability."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def distance_km(lat1,lon1,lat2,lon2):
    a,b=map(math.radians,[lat1,lat2]);delta_lat=b-a;delta_lon=math.radians(lon2-lon1)
    h=math.sin(delta_lat/2)**2+math.cos(a)*math.cos(b)*math.sin(delta_lon/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(h)))


def compare(inventory, places, threshold=25):
    index={}
    for place in places:
        index.setdefault((place['USPS'],place['NAME'].casefold()),[]).append(place)
    output=[]
    for row in inventory:
        kind=row['jurisdiction_type'].casefold()
        if kind not in {'city','village'}:
            continue  # Township/county geography is not a Census place-name join.
        name=row['jurisdiction'].strip()
        prefix=kind+' of '
        if name.casefold().startswith(prefix):name=name[len(prefix):]
        # A place name itself may end in City (e.g. Grove City city).
        # Prefer the name plus legal type, then an already typed exact name.
        typed=name+' '+kind
        if (row['state_abbrev'],typed.casefold()) in index:
            name=typed
        elif (row['state_abbrev'],name.casefold()) not in index:
            name=typed
        matches=index.get((row['state_abbrev'],name.casefold()),[])
        report={'moratorium_id':row['moratorium_id'],'state':row['state_abbrev'],
                'lookup_name':name,'match_count':len(matches)}
        if len(matches)!=1:
            report['disposition']='ambiguous' if matches else 'unmatched'
        elif not row['latitude'] or not row['longitude']:
            report['disposition']='inventory_coordinates_missing'
        else:
            match=matches[0]
            km=distance_km(float(row['latitude']),float(row['longitude']),float(match['INTPTLAT']),float(match['INTPTLONG']))
            report.update(disposition='distance_review_required' if km>threshold else 'within_distance_screen',
                distance_km=round(km,3),census_geoid=match['GEOID'],
                inventory_point=[float(row['longitude']),float(row['latitude'])],
                census_internal_point=[float(match['INTPTLONG']),float(match['INTPTLAT'])])
        output.append(report)
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gazetteer',type=Path,required=True)
    p.add_argument('--inventory',type=Path,default=ROOT/'data/moratorium_inventory.csv')
    p.add_argument('--threshold-km',type=float,default=25)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.threshold_km<=0:p.error('threshold must be positive')
    raw=args.gazetteer.read_bytes();text=raw.decode('utf-8-sig');delimiter='|' if '|' in text.splitlines()[0] else '\t'
    places=list(csv.DictReader(text.splitlines(),delimiter=delimiter));states={r['USPS'] for r in places}
    with args.inventory.open(newline='') as stream:inventory=[r for r in csv.DictReader(stream) if r['state_abbrev'] in states]
    rows=compare(inventory,places,args.threshold_km)
    from collections import Counter
    report={'gazetteer_sha256':hashlib.sha256(raw).hexdigest(),'inventory_sha256':hashlib.sha256(args.inventory.read_bytes()).hexdigest(),
            'states':sorted(states),'screen_threshold_km':args.threshold_km,'counts':dict(Counter(r['disposition'] for r in rows)),
            'scope':'Exact-name city/village candidate comparison only. No automatic correction, equivalence, boundary, complete geography audit or project/legal applicability finding. Within threshold is not proof of correct jurisdiction.',
            'records':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['counts'],indent=2))
