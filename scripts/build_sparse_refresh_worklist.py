#!/usr/bin/env python3
"""Freeze every inventory object and sparse census coordinates; preview, never execute.

Search coordinates are not new domain identities. Exact legacy locality tuples stay
separate from canonical expanded jurisdictions until an explicit identity review.
Unreviewed host candidates never become official domain filters.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from apply_research import STATE_ABBREV
from search_refresh_batch import preview

ROOT = Path(__file__).resolve().parents[1]
SECTOR_MAP = {'data_center':'data_center', 'battery_storage':'battery_storage',
              'solar':'solar', 'wind':'wind', 'cryptocurrency_mining':'cryptocurrency',
              'cryptocurrency':'cryptocurrency'}
SECTOR_WORDS = {'data_center':'data center', 'battery_storage':'battery energy storage',
                'solar':'solar energy', 'wind':'wind energy', 'cryptocurrency':'cryptocurrency'}


def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def coordinate(kind, value): return kind+':'+digest(canonical(value))[:24]
def require(ok, message):
    if not ok: raise ValueError(message)


def build(root, cutoff, *, seed=20261106, per_lane=None, bindings=None):
    from datetime import date
    date.fromisoformat(cutoff)
    require(per_lane is None or (type(per_lane) is int and per_lane > 0), 'Positive per-lane sample required')
    inputs = {};loaded_paths={}
    expanded_root=(root/'data/expanded').resolve()
    def load(rel, fmt):
        path = expanded_root/Path(rel).name if rel.startswith('data/expanded/') else root/rel
        raw = path.read_bytes();loaded_paths[rel]=path
        inputs[rel] = digest(raw)
        if fmt == 'csv':
            import io
            return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        return [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    local = load('data/moratorium_inventory.csv','csv')
    state = load('data/state_legislation.csv','csv')
    jurisdictions = load('data/expanded/jurisdictions.jsonl','jsonl')
    measures = load('data/expanded/ballot_measures.jsonl','jsonl')
    elections = load('data/expanded/elections.jsonl','jsonl')
    source_rows = load('data/expanded/source_documents.jsonl','jsonl')
    for rows, field in [(local,'moratorium_id'),(state,'policy_action_id'),
                        (jurisdictions,'jurisdiction_id'),(measures,'measure_id'),(elections,'election_id')]:
        require(all(r[field] for r in rows) and len({r[field] for r in rows}) == len(rows), 'Duplicate or blank input identity: '+field)
    registry = {}
    def register(key, label, aliases, state, government_type, county=None):
        require(state in STATE_ABBREV.values(), 'Unknown state coordinate')
        entry = {'id':key,'label':label,'aliases':sorted(set(aliases)), 'state':state,
                 'government_type':government_type,'county':county,'official_hosts':[],
                 'host_discovery_status':'not_reviewed','portal_candidates':[]}
        if key in registry: require(registry[key] == entry,'Conflicting registry coordinate')
        registry[key] = entry
        return key
    states = {abbr:register('state:'+abbr,name,[name,abbr],abbr,'state')
              for name,abbr in sorted(STATE_ABBREV.items()) if abbr!='DC'}
    local_j = {}
    for r in local:
        tup = [r['state_abbrev'],r['jurisdiction_type'],r['jurisdiction']]
        key = coordinate('legacy-locality',tup)
        local_j[r['moratorium_id']] = register(key, r['jurisdiction']+', '+r['state'],
                                             [r['jurisdiction']],r['state_abbrev'],r['jurisdiction_type'])
    for r in jurisdictions:
        register('expanded:'+r['jurisdiction_id'],r['name']+', '+r['state'],
                 [r['name'],*r['aliases']],r['state'],r['government_type'],r['county'])
    # Canonical result URLs are discovery candidates, not reviewed host authority.
    for e in elections:
        key = 'expanded:'+e['jurisdiction_id']; require(key in registry,'Unknown election jurisdiction')
        for url in e['official_result_urls']:
            registry[key]['portal_candidates'].append({'url':url,'host':urlsplit(url).hostname,
                                                       'election_id':e['election_id'],'status':'requires_host_review'})
    bindings = bindings or {'schema_version':'refresh-host-bindings-1','bindings':[]}
    require(set(bindings)=={'schema_version','bindings'} and bindings['schema_version']=='refresh-host-bindings-1','Invalid host bindings')
    manifest_cache = {}
    for b in bindings['bindings']:
        require(set(b)=={'jurisdiction_id','host','source_url','body_sha256','locator','role','reviewer','manifest','authority_review','authority_review_sha256'}, 'Wrong binding fields')
        require(b['jurisdiction_id'] in registry,'Unknown binding jurisdiction')
        require(b['role'] in ('government','election','records') and b['reviewer'] and b['locator'], 'Explicit host role/reviewer required')
        host = urlsplit(b['source_url']).hostname
        require(host == b['host'] and urlsplit(b['source_url']).scheme in ('https','http'), 'Host does not match source URL')
        rel = b['manifest']; require(not Path(rel).is_absolute() and '..' not in Path(rel).parts and rel.startswith('work/sources/'), 'Invalid manifest path')
        if rel not in manifest_cache: manifest_cache[rel] = load(rel,'jsonl')
        matches = [r for r in manifest_cache[rel] if r.get('sha256')==b['body_sha256'] and r.get('url')==b['source_url'] and r.get('ok')]
        require(matches,'Host binding has no successful retained source version')
        files = [root/f for r in matches for f in r.get('files',[]) if Path(f).suffix.lower()!='.txt']
        require(any(f.is_file() and digest(f.read_bytes())==b['body_sha256'] for f in files),'Host evidence body unavailable or drifted')
        review_path=Path(b['authority_review'])
        require(not review_path.is_absolute() and '..' not in review_path.parts and str(review_path).startswith('work/research/'),'Invalid authority review path')
        review_raw=(root/review_path).read_bytes();require(digest(review_raw)==b['authority_review_sha256'],'Authority review hash drift')
        review=json.loads(review_raw)
        require(not ({'path','sha256'} & set(review)),'Reserved authority review fields')
        for field in ('jurisdiction_id','host','role','source_url','body_sha256','reviewer'):
            require(review.get(field)==b[field],'Authority review scope mismatch: '+field)
        require(review.get('authority_basis') and review.get('reviewed_at'),'Authority basis and review date required')
        from datetime import datetime
        require(datetime.fromisoformat(review['reviewed_at']).tzinfo is not None,'Timezone required in authority review')
        entry=registry[b['jurisdiction_id']]
        require(not any(h['host']==b['host'] and h['role']==b['role'] for h in entry['official_hosts']),'Duplicate host binding')
        entry['official_hosts'].append({**{k:b[k] for k in ('host','source_url','body_sha256','locator','role','reviewer')},
                                        'authority_review':{**review,'path':str(review_path),'sha256':b['authority_review_sha256']}})
        entry['host_discovery_status']='reviewed_hosts_available_not_exhaustive'
    items=[]; cells=[]
    def item(kind, known_id, jurisdiction, raw_sectors, intent, context, lane='inventory_refresh'):
        sectors=sorted({SECTOR_MAP[s] for s in raw_sectors if s in SECTOR_MAP})
        unresolved=sorted(set(raw_sectors)-set(SECTOR_MAP))
        task={'id':kind+':'+known_id,'kind':kind,'known_id':known_id,'jurisdiction_id':jurisdiction,
              'lane':lane,'sectors':sectors,'unresolved_sector_terms':unresolved,'intent':intent,
              'sector_coordinate_translations':[{'source_term':term,'search_coordinate':SECTOR_MAP[term], 'semantics':'query vocabulary translation, not canonical equivalence'} for term in sorted(set(raw_sectors)) if term in SECTOR_MAP],
              'context':context,'freshness_disposition':'not_attempted_by_this_worklist',
              'planning_status':'partial_sector_review' if unresolved else ('ready_for_search_preview' if sectors else 'sector_neutral_search_sector_review_open')}
        items.append(task)
        for sector in sectors+(['sector_unresolved'] if unresolved or not sectors else []):
            label=registry[jurisdiction]['label']; words=SECTOR_WORDS.get(sector,'land use energy infrastructure development')
            designation=context.get('designation') or context.get('title') or ''
            aliases=' OR '.join(json.dumps(a,ensure_ascii=False) for a in registry[jurisdiction]['aliases'])
            exact_place=(('('+aliases+')') if aliases else json.dumps(label))+' '+registry[jurisdiction]['state']
            if kind=='state_action': words=''  # Legislative designation recovery does not require sector inference.
            # No publication window: preserve undated primary-record recovery.
            if lane=='election_census':
                semantic=f'{label} {designation} {words} ballot referendum initiative town meeting qualification wording results canvass certification implementation allow prohibit development {cutoff}'
                exact=f'{exact_place} {designation} {words} (ballot OR referendum OR initiative OR "town meeting") (allow OR prohibit OR results OR certification)'
            else:
                semantic=f'{label} {designation} {words} moratorium adoption extension expiration repeal replacement injunction official records through {cutoff}'
                exact=f'{exact_place} {designation} {words} (moratorium OR extension OR repeal OR replacement OR injunction)'
            if kind=='state_action':
                semantic=f'{label} {designation} official legislative status enacted veto amendment effective date utility executive litigation {cutoff}'
                exact=f'{exact_place} {json.dumps(designation)} (legislature OR enacted OR veto OR amendment OR status)'
            hosts=sorted({h['host'] for h in registry[jurisdiction]['official_hosts']})
            # Official-host recovery is separate from unrestricted discovery.
            variants=[{'name':'exa-discovery','backend':'exa','query':semantic,'max_results':5},
                      {'name':'google-exact','backend':'serpapi','query':exact,'max_results':5}]
            if hosts: variants.append({'name':'exa-primary-host','backend':'exa','query':semantic,'max_results':5,'include_domains':hosts})
            cells.append({'id':task['id']+':'+sector,'lane':lane,'jurisdiction_id':jurisdiction,
                          'sector':sector,'period':'through-'+cutoff,'intent':intent,'known_id':task['id'],'variants':variants})
    for r in sorted(local,key=lambda r:r['moratorium_id']):
        item('moratorium',r['moratorium_id'],local_j[r['moratorium_id']],json.loads(r['sectors']),
             'original-and-later-legal-history',{'classification':r['enacted_status'],'legacy_legal_basis':r['legal_basis'],
             'legacy_date':r['date_enacted_iso'],'current_endpoint':r['current_end_date_iso']})
    for r in sorted(state,key=lambda r:r['policy_action_id']):
        require(r['state_abbrev'] in states,'State policy outside fifty-state scope')
        item('state_action',r['policy_action_id'],states[r['state_abbrev']],[],
             'legislative-executive-utility-and-litigation-history',{'designation':r['bill'],
             'classification':r['bill_status_category'],'sector_gap':'Legacy state table has no reviewed sector column; no sector inferred from prose.'})
    election_by_id={e['election_id']:e for e in elections}
    for r in sorted(measures,key=lambda r:r['measure_id']):
        e=election_by_id[r['election_id']]
        item('measure',r['measure_id'],'expanded:'+r['jurisdiction_id'],r['sectors'],
             'wording-qualification-result-certification-and-implementation',
             {'designation':r['designation'],'title':r['title'],'election_id':r['election_id'],
              'election_date':e['election_date'],'lifecycle':r['lifecycle'],'bindingness':r['bindingness']},'election_census')
    for abbr,key in sorted(states.items()):
        for sector in sorted(SECTOR_WORDS):
            for lane in ['gap_discovery','election_census']:
                item('state_sector_'+lane,abbr+':'+sector,key,[sector],
                     'new-local-and-state-actions' if lane=='gap_discovery' else 'independent-election-discovery',
                     {'coverage_unit':'state-sector search, not municipal census'},lane)
    # Sparse coordinates are explicit. No local-government Cartesian product.
    limit=sum(len(c['variants']) for c in cells)
    sampling={'strategy':'full','seed':seed} if per_lane is None else {'strategy':'stratified','dimension':'lane','per':per_lane,'seed':seed}
    plan={'schema_version':'refresh-search-plan-2','registry':[{'id':r['id'],'label':r['label'],'aliases':r['aliases'],
          'official_hosts':[{k:h[k] for k in ('host','source_url','body_sha256','locator','authority_review')} for h in r['official_hosts']]}
          for r in sorted(registry.values(),key=lambda r:r['id'])], 'cells':cells,
          'sample':sampling,
          'caps':{'exa':limit,'serpapi':limit,'googlenews':0,'gdelt':0,'search_total':limit},'allow_unpriced':False}
    prepared=preview(plan)
    counts=prepared['provider_calls'];plan['caps']={k:counts.get(k,0) for k in ['exa','serpapi','googlenews','gdelt']};plan['caps']['search_total']=sum(counts.values())
    prepared=preview(plan)
    selected={c['id'] for c in prepared['selected_cells']}
    coverage={}
    for c in cells:
        key=registry[c['jurisdiction_id']]['state']+':'+c['lane']+':'+c['sector']
        bucket=coverage.setdefault(key,{'planned':0,'selected':0,'excluded':0});bucket['planned']+=1;bucket['selected' if c['id'] in selected else 'excluded']+=1
    require((root/'data/expanded').resolve()==expanded_root,'Expanded pointer changed during planning')
    require(all(digest(loaded_paths[rel].read_bytes())==value for rel,value in inputs.items()),'Input changed during planning')
    summary={'schema_version':'refresh-scope-1','expanded_generation':expanded_root.name,'cutoff':cutoff,'input_sha256':inputs,'bindings_sha256':digest(canonical(bindings)),
             'object_counts':{'moratorium':len(local),'state_action':len(state),'measure':len(measures)},
             'registry_coordinates':len(registry),'planning_status_counts':dict(Counter(t['planning_status'] for t in items)),
             'work_items':len(items),'explicit_search_cells':len(cells),'selected_search_cells':len(prepared['selected_cells']),
             'reviewed_host_coordinates':sum(bool(r['official_hosts']) for r in registry.values()),
             'source_document_rows':len(source_rows),'selection_mode':'full_frame' if per_lane is None else 'lane_preview_only_not_campaign_coverage','selection_by_state_lane_sector':coverage,'limitations':['Planning does not update or reset any research freshness. All statuses are scoped to this newly generated worklist.',
             'Legacy locality tuples and expanded jurisdictions remain separate until reviewed crosswalk; coordinates are not new canonical IDs.',
             'State-sector sweeps are not a local-government census. Missing official hosts and unresolved sectors remain visible.',
             'Unresolved sector terms do not disappear when another sector is searchable. No completeness or negative-finding inference.',
             'No provider calls. Prices and whole-run budgets remain unresolved; execution is disabled by unpriced policy.']}
    return {'registry':{'schema_version':'refresh-jurisdiction-registry-1','jurisdictions':sorted(registry.values(),key=lambda r:r['id'])},
            'worklist':{'schema_version':'refresh-worklist-1','items':items},'plan':plan,'preview':prepared,'summary':summary}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cutoff',required=True);p.add_argument('--bindings',type=Path)
    p.add_argument('--seed',type=int,default=20261106);p.add_argument('--per-lane',type=int,help='Optional tiny lane-stratified preview; default includes full explicit frame.')
    p.add_argument('--output',type=Path)
    a=p.parse_args();result=build(ROOT,a.cutoff,seed=a.seed,per_lane=a.per_lane,
                                  bindings=json.loads(a.bindings.read_text()) if a.bindings else None)
    if a.output:
        a.output.mkdir(parents=True,exist_ok=False)
        for key,value in result.items(): (a.output/(key+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':main()
