#!/usr/bin/env python3
"""Validate candidate expanded JSONL ledgers; never writes or promotes records."""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path(__file__).resolve().parents[1] / 'work/schemas/expanded/1.0.0.json'
IDS = {'jurisdictions':'jurisdiction_id', 'elections':'election_id', 'ballot_measures':'measure_id', 'measure_provisions':'provision_id', 'measure_results':'result_observation_id', 'local_restrictions':'restriction_id', 'instrument_events':'event_id', 'measure_instrument_links':'link_id', 'source_documents':'source_document_id', 'claims':'claim_id', 'review_decisions':'decision_id', 'search_runs':'run_id', 'search_attempts':'attempt_id', 'search_sightings':'sighting_id', 'coverage_observations':'coverage_id'}


def validate(directory, moratoria=None, state_actions=None):
    directory = directory.resolve()  # Pin one immutable publication generation.
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    errors, rows = [], {name: {} for name in IDS}
    def err(where, message): errors.append(f'{where}: {message}')
    for path in sorted(directory.glob('*.jsonl')):
        name = path.stem
        if name not in IDS:
            err(path.name, 'unknown table'); continue
        validator = Draft202012Validator({'$ref': '#/$defs/' + name, '$defs': schema['$defs']}, format_checker=FormatChecker())
        for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip(): continue
            where = f'{path.name}:{line_no}'
            try: record = json.loads(line)
            except json.JSONDecodeError as exc:
                err(where, f'invalid JSON: {exc.msg}'); continue
            issues = list(validator.iter_errors(record))
            if issues:
                for issue in issues: err(where, f"{'/'.join(map(str, issue.absolute_path)) or '<record>'}: {issue.message}")
                continue
            key = record[IDS[name]]
            if key in rows[name]: err(where, f'duplicate {IDS[name]} {key}'); continue
            rows[name][key] = record
    def exists(table, key, where):
        if key is not None and key not in rows[table]: err(where, f'unknown {table} reference {key}')
    def ext_ids(path, field):
        if path is None: return None
        try:
            with path.open(newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                if field not in (reader.fieldnames or []): raise ValueError(f'missing column {field}')
                return {r[field] for r in reader if r[field]}
        except (OSError, ValueError) as exc:
            err(str(path), str(exc)); return set()
    external = {'moratorium': ext_ids(moratoria, 'moratorium_id'), 'state_action': ext_ids(state_actions, 'policy_action_id')}
    def instrument(ref, where):
        kind, key = ref['kind'], ref['id']
        if kind == 'restriction': exists('local_restrictions', key, where)
        elif external[kind] is None: err(where, f'{kind} reference requires corresponding legacy CSV')
        elif key not in external[kind]: err(where, f'unknown {kind} reference {key}')
    def bounded(value, where):
        if isinstance(value, dict):
            if {'earliest','latest','precision','original_text'} <= value.keys():
                a,b=value['earliest'],value['latest']
                if a and b and a > b: err(where, 'date bounds earliest after latest')
                if value['precision'] == 'unknown' and (a or b): err(where, 'unknown precision with known date bounds')
                if value['precision'] == 'day' and (not a or a != b): err(where, 'day precision requires equal bounds')
            for k,v in value.items(): bounded(v, where + '/' + k)
        elif isinstance(value, list):
            for i,v in enumerate(value): bounded(v, where + '/' + str(i))
    for table, records in rows.items():
        for key, r in records.items():
            w=f'{table}/{key}'
            bounded(r,w)
            for field, target in [('jurisdiction_id','jurisdictions'),('election_id','elections'),('measure_id','ballot_measures'),('source_document_id','source_documents'),('run_id','search_runs'),('attempt_id','search_attempts')]:
                if field in r and IDS[table] != field: exists(target,r[field],w)
            for field,target in [('claim_ids','claims'),('provision_ids','measure_provisions')]:
                for x in r.get(field,[]): exists(target,x,w)
            if 'instrument' in r: instrument(r['instrument'],w)
            for field in ('subject','target'):
                if field in r: exists(r[field]['table'],r[field]['id'],w)
            if table=='ballot_measures' and r['election_id'] in rows['elections'] and rows['elections'][r['election_id']]['jurisdiction_id'] != r['jurisdiction_id']:
                err(w,'measure and election jurisdiction IDs differ; model overlapping electoral jurisdictions explicitly')
            if table=='measure_instrument_links':
                for p in r['provision_ids']:
                    if p in rows['measure_provisions'] and rows['measure_provisions'][p]['measure_id'] != r['measure_id']: err(w,'provision belongs to another measure')
            if table in ('measure_results','review_decisions') and r.get('supersedes_id'):
                exists(table,r['supersedes_id'],w)
                old=rows[table].get(r['supersedes_id'])
                if old:
                    field='measure_id' if table=='measure_results' else 'target'
                    if old[field] != r[field]: err(w,'supersession changes target')
                    if table == 'review_decisions' and old['scope'] != r['scope']: err(w,'supersession changes review scope')
                    time='observed_at' if table=='measure_results' else 'decided_at'
                    if datetime.fromisoformat(old[time].replace('Z','+00:00')) >= datetime.fromisoformat(r[time].replace('Z','+00:00')): err(w,'superseded observation is not earlier')
            if table=='search_attempts' and r['retry_of']:
                exists(table,r['retry_of'],w)
                old=rows[table].get(r['retry_of'])
                if old and (old['run_id'] != r['run_id'] or old['started_at'] >= r['started_at']): err(w,'retry must follow an attempt in the same run')
            if table=='jurisdictions' and r['valid_from'] and r['valid_until'] and r['valid_from'] >= r['valid_until']: err(w,'invalid half-open jurisdiction validity interval')
            if table=='coverage_observations' and r['period_start'] and r['period_end'] and r['period_start'] >= r['period_end']: err(w,'invalid half-open coverage interval')
            if table=='search_attempts' and r['window_start'] and r['window_end'] and r['window_start'] > r['window_end']: err(w,'search window start after end')
            if table=='local_restrictions':
                a=r['applicability_start']['latest']; e=r['effective']['earliest']
                if a and e and a < e and not r['retroactivity_explanation']: err(w,'retroactive applicability requires explanation and evidence')
                if a and e and a < e and not r['claim_ids']: err(w,'retroactive applicability requires evidence claims')
                if a and e and a < e and r['claim_ids'] and not any(
                    rows['claims'].get(cid, {}).get('subject') == {'table':'local_restrictions','id':key}
                    and rows['claims'][cid]['predicate'] == 'applicability_start' for cid in r['claim_ids']
                ): err(w,'retroactivity requires a claim scoped to applicability_start')
            if table=='measure_results':
                for field, method in r.get('value_methods', {}).items():
                    if field not in r: err(w, f'value method references absent field {field}')
                    for cid in method['claim_ids']: exists('claims',cid,w)
                check_result(r,w,rows,err)
    # Accepted evidence is scoped to a specific claim predicate; link acceptance additionally
    # needs a decision for that exact relation and claim subjects matching the link.
    decisions=list(rows['review_decisions'].values())
    for table in ('measure_results', 'review_decisions'):
        successors = {}
        for record in rows[table].values():
            previous = record.get('supersedes_id')
            if previous:
                successors.setdefault(previous, []).append(record[IDS[table]])
        for previous, children in successors.items():
            if len(children) > 1:
                err(table+'/'+previous, 'conflicting supersession branches: '+', '.join(children))
    def accepted(table,key,scope):
        ds=[d for d in decisions if d['target']=={'table':table,'id':key} and d['scope']==scope]
        superseded={d['supersedes_id'] for d in decisions if d['supersedes_id']}
        live=[d for d in ds if d['decision_id'] not in superseded]
        return len(live)==1 and live[0]['disposition']=='accepted'
    for d in decisions:
        w='review_decisions/'+d['decision_id']
        if d['disposition']=='accepted' and not d['claim_ids']: err(w,'accepted decision requires supporting claims')
        for cid in d['claim_ids']:
            c=rows['claims'].get(cid)
            if c and (c['subject'] != d['target'] and not (d['target']['table']=='claims' and d['target']['id']==cid)):
                err(w,'supporting claim subject does not match decision target')
            if c and d['disposition']=='accepted' and d['target']['table'] != 'claims' and not accepted('claims',cid,c['predicate']):
                err(w, f'supporting claim {cid} lacks current scoped acceptance')
        if d['target']['table']=='claims':
            c=rows['claims'].get(d['target']['id'])
            if c and d['scope'] != c['predicate']: err(w,'claim decision scope must equal predicate')
    for link in rows['measure_instrument_links'].values():
        if link['review_status'] != 'accepted': continue
        w='measure_instrument_links/'+link['link_id']
        if not accepted('measure_instrument_links',link['link_id'],link['relation']): err(w,'accepted link lacks a current scoped accepted decision')
        if not link['claim_ids']: err(w,'accepted link requires supporting claims')
        for cid in link['claim_ids']:
            c=rows['claims'].get(cid)
            if c and (c['subject'] != {'table':'measure_instrument_links','id':link['link_id']} or not accepted('claims',cid,c['predicate'])): err(w,f'claim {cid} lacks scoped acceptance for this link')
        measure=rows['ballot_measures'].get(link['measure_id'])
        if measure and measure['bindingness']=='advisory' and link['relation'] in ('enacts','upholds'): err(w,'advisory measure cannot itself enact or uphold an instrument')
    return errors, rows


def certified_result_count(rows):
    """Count only current explicitly certified observations, never precinct completion."""
    results = list(rows['measure_results'].values())
    superseded = {r['supersedes_id'] for r in results if r['supersedes_id']}
    return sum(r['result_observation_id'] not in superseded and
               r['certification_status'] in ('certified', 'amended_certification')
               for r in results)


def check_result(r,w,rows,err):
    y,n,o,v=r['yes_votes'],r['no_votes'],r['other_votes'],r['valid_votes']
    if None not in (y,n,o,v) and y+n+o != v: err(w,'vote components do not equal valid votes')
    if r.get('yes_no_votes') is not None and (y is None or n is None or r['yes_no_votes'] != y+n):
        err(w,'yes_no_votes must equal supported yes plus no counts')
    if r.get('blank_votes') is not None and r['ballots_cast'] is not None and v is not None and v+r['blank_votes'] > r['ballots_cast']:
        err(w,'valid plus blank votes exceed ballots cast')
    if v is not None and y is not None and n is not None and y+n > v: err(w,'yes and no exceed valid votes')
    b,reg=r['ballots_cast'],r['registered_voters']
    if v is not None and b is not None and v > b: err(w,'valid votes exceed ballots cast')
    if b is not None and reg is not None and b > reg: err(w,'ballots exceed registered voters')
    if None not in (v,r['undervotes'],r['overvotes'],b) and v+r['undervotes']+r['overvotes'] != b: err(w,'question votes and undervotes/overvotes do not equal ballots cast')
    if None not in (r['precincts_reporting'],r['precincts_total']) and r['precincts_reporting'] > r['precincts_total']: err(w,'reporting precincts exceed total')
    denom={'valid_votes':v,'ballots_cast':b,'registered_voters':reg}.get(r['percentage_denominator'])
    if y is not None and denom and r['source_yes_percent'] is not None and abs(100*y/denom-r['source_yes_percent']) > 0.11: err(w,'source yes percentage contradicts stated denominator')
    cert=r['certification_status']
    if cert in ('certified','amended_certification') and not r['certification_date']: err(w,'certified status requires certification date')
    if cert in ('unofficial','unknown') and r['certification_date']: err(w,'uncertified status cannot claim certification date')
    if r['certification_date'] and r['certification_date'] > r['observed_at'][:10]: err(w,'certification date after observation')
    expected='unknown'
    if y is not None and denom and r['passage_threshold'] is not None and r['threshold_comparison'] != 'unknown':
        if y == n and r['passage_threshold']==0.5 and r['percentage_denominator']=='valid_votes': expected='tied'
        else:
            ratio=y/denom; t=r['passage_threshold']
            expected='approved' if (ratio>t if r['threshold_comparison']=='greater_than' else ratio>=t) else 'defeated'
    if r['calculated_outcome'] != 'unknown' and r['calculated_outcome'] != expected: err(w,'calculated outcome contradicts votes or lacks a specified passage rule')
    if r['reported_outcome'] in ('approved','defeated','tied') and expected != 'unknown' and r['reported_outcome'] != expected: err(w,'reported outcome contradicts calculated passage rule')
    m=rows['ballot_measures'].get(r['measure_id'])
    direction='unresolved'
    basis=r.get('outcome_direction_basis','calculated')
    outcome=r['calculated_outcome'] if basis=='calculated' else r['reported_outcome'] if basis=='reported' else 'unknown'
    if basis=='reported':
        method=r.get('value_methods',{}).get('reported_outcome',{})
        target={'table':'measure_results','id':r['result_observation_id']}
        supporting=[rows['claims'].get(cid,{}) for cid in method.get('claim_ids',[])]
        if (method.get('method')!='source_reported' or not any(
            c.get('subject')==target and c.get('predicate')=='reported_outcome'
            and c.get('value')==outcome for c in supporting)):
            err(w,'reported direction basis requires an outcome claim scoped to this result observation')
    if m and outcome in ('approved','defeated'):
        direction=m['yes_direction']
        if outcome=='defeated': direction={'restricts':'facilitates','facilitates':'restricts'}.get(direction,direction)
    if r['outcome_direction'] != 'unresolved' and r['outcome_direction'] != direction: err(w,'outcome direction contradicts its outcome basis and yes polarity')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path); p.add_argument('--moratoria',type=Path); p.add_argument('--state-actions',type=Path)
    a=p.parse_args()
    if not a.directory.is_dir(): p.error('directory does not exist')
    errors,rows=validate(a.directory,a.moratoria,a.state_actions)
    for e in errors: print(e,file=sys.stderr)
    if errors: print(f'Invalid: {len(errors)} error(s)',file=sys.stderr); return 1
    print('Valid candidate ledgers: '+', '.join(f'{k}={len(v)}' for k,v in rows.items()))
    print(f'Current explicitly certified result observations: {certified_result_count(rows)}')
    return 0

if __name__=='__main__': sys.exit(main())
