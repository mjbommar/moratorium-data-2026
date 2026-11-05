#!/usr/bin/env python3
"""Combine terminal ballot returns for review; never promotes or edits inputs."""
import argparse
import copy
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from expanded_data import IDS, validate

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'work/research/2026-11-05/ballot-discovery'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def record_hash(row):return digest(json.dumps(row,sort_keys=True,separators=(',',':')).encode())
def lines(path):return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def namespace(table,row,prefix):
    """Remap declared references, retaining free-form source values verbatim."""
    row=copy.deepcopy(row)
    ref=lambda value:prefix+'::'+value if value is not None else None
    for field in IDS.values():
        if field in row:row[field]=ref(row[field])
    for field in ('claim_ids','provision_ids'):
        if field in row:row[field]=[ref(v) for v in row[field]]
    for field in ('subject','target'):
        if field in row:row[field]['id']=ref(row[field]['id'])
    if 'instrument' in row and row['instrument']['kind']=='restriction':
        row['instrument']['id']=ref(row['instrument']['id'])
    for field in ('supersedes_id','retry_of'):
        if field in row:row[field]=ref(row[field])
    for method in row.get('value_methods',{}).values():
        method['claim_ids']=[ref(v) for v in method['claim_ids']]
    return row


def build(queue_path,runs,output,registry=REGISTRY):
    if output.exists():raise ValueError('Refusing to overwrite a census snapshot')
    queue=json.loads(queue_path.read_text());overrides=json.loads((registry/'reviewed-inputs.json').read_text())
    aliases=json.loads((registry/'identity-decisions.json').read_text())
    receipts=[];tables=defaultdict(list);candidates=[];original_measures={};hashes={}
    for job in queue['jobs']:
        if not job['id'].startswith(('ballot-','recovery-ballot-')):continue
        jid=job['id'];status_path=runs/jid/'status.json'
        status=json.loads(status_path.read_text()) if status_path.exists() else {'state':'not_started'}
        receipt={'job_id':jid,'state':status['state'],'assigned_seeds':job['records']};receipts.append(receipt)
        if status['state'] not in ('finished','failed'):continue
        spec=json.loads(Path(job['spec']).read_text());owned=Path(spec['owned_paths'][0]);directory=owned/'expanded'
        if jid in overrides:
            override=overrides[jid];directory=ROOT/override['directory']
            review_path=ROOT/override['receipt'];review=json.loads(review_path.read_text())
            expected=review['output_hashes']
            actual={p.name:digest(p.read_bytes()) for p in directory.glob('*.jsonl')}
            if actual!=expected:raise ValueError('Reviewed overlay drift: '+jid)
            hashes[str(review_path.relative_to(ROOT))]=digest(review_path.read_bytes())
            receipt['reviewed_overlay']=override['directory']
        if not directory.exists() or not (owned/'candidates.json').exists():
            receipt['error']='missing expanded ledgers or candidate dispositions';continue
        receipt['source_directory']=str(directory)
        job_tables={p.stem:lines(p) for p in sorted(directory.glob('*.jsonl'))}
        for table,rows in job_tables.items():
            if table not in IDS:raise ValueError('Unknown table: '+table)
            path=directory/(table+'.jsonl');hashes[str(path)]=digest(path.read_bytes())
            for row in rows:
                if table=='ballot_measures':original_measures[(jid,row['measure_id'])]=row
                tables[table].append(namespace(table,row,jid))
        candidate_path=owned/'candidates.json';hashes[str(candidate_path)]=digest(candidate_path.read_bytes())
        returned=json.loads(candidate_path.read_text());receipt['returned_candidates']=len(returned)
        for candidate in returned:candidates.append({'job_id':jid,'id_namespace':jid,'source_candidate':candidate})
    representative={}
    for alias in aliases:
        if alias['disposition']!='same_electoral_question':continue
        record_ids={r['measure_id'] for r in alias['records']}
        if not {alias['alias_id'],alias['representative_seed_id']} <= record_ids:
            raise ValueError('Identity decision must pin both electoral-question records')
        if alias['alias_id'] in representative:
            raise ValueError('Competing identity decisions for '+alias['alias_id'])
        for record in alias['records']:
            row=original_measures.get((record['job_id'],record['measure_id']))
            if row is None or record_hash(row)!=record['record_sha256']:
                raise ValueError('Identity decision record missing or drifted: '+record['measure_id'])
        representative[alias['alias_id']]=alias['representative_seed_id']
    if set(representative) & set(representative.values()):
        raise ValueError('Resolve identity chains explicitly before staging')
    groups=defaultdict(list)
    for (jid,mid),row in original_measures.items():
        groups[representative.get(mid,mid)].append({'job_id':jid,'original_measure_id':mid,'staged_measure_id':jid+'::'+mid})
    output.mkdir(parents=True)
    ledger=output/'expanded';ledger.mkdir()
    for table,rows in sorted(tables.items()):
        rows.sort(key=lambda r:r[IDS[table]])
        (ledger/(table+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
    errors,_=validate(ledger,ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv')
    for name in ('identity-decisions.json','reviewed-inputs.json'):
        hashes[str(registry/name)]=digest((registry/name).read_bytes())
    manifest={'queue_sha256':digest(queue_path.read_bytes()),'input_hashes':hashes,'jobs':receipts,
        'table_counts':{t:len(r) for t,r in sorted(tables.items())},
        'logical_seed_groups':len(groups),'measure_observation_records':len(original_measures),
        'job_states':dict(Counter(r['state'] for r in receipts)),'structural_errors':errors,
        'scope':'Candidate review snapshot only. Namespaces prevent ID collisions. Explicit identity decisions group duplicate electoral questions; physical observations remain separate. No legal-effect, source-quality, certification or canonical promotion acceptance. Logical groups are not a complete or independently verified census.'}
    manifest['expanded_output_hashes']={p.name:digest(p.read_bytes()) for p in sorted(ledger.glob('*.jsonl'))}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (output/'measure-groups.json').write_text(json.dumps(dict(sorted(groups.items())),indent=2)+'\n')
    (output/'candidate-dispositions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in candidates))
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue',type=Path,required=True);p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();m=build(a.queue,a.runs,a.output)
    print(json.dumps({k:m[k] for k in ('job_states','logical_seed_groups','measure_observation_records','structural_errors')},indent=2))
