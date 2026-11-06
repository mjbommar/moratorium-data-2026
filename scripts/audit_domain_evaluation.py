#!/usr/bin/env python3
"""Audit frozen domain-extraction artifacts and adjudicated metrics, without calls.

Source entailment comes from explicit review files, never from this arithmetic.
Public output contains metadata, field names and IDs, not source/model payloads.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from extract_document_resumable import digest

LABELS={'supported','unsupported','ambiguous','off_target'}

def require(ok,message):
    if not ok: raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())


def verify_frozen_code(run, hashes):
    """Verify retained executed bytes, independent of subsequent source edits."""
    for original, expected in hashes.items():
        retained = run / 'executed-code' / f'{expected}-{Path(original).name}'
        require(retained.is_file() and sha(retained) == expected,
                f'Frozen executed-code missing or changed: {Path(original).name}')


def verify_support_locations(candidate, text):
    passages=candidate.get('supporting_passages', [])
    locations=candidate.get('supporting_passage_locations', [])
    require(len(passages)==len(locations), 'Supporting passage location inventory mismatch')
    for passage, located in zip(passages, locations):
        require(all(located.get(k)==v for k,v in passage.items()), 'Supporting passage changed')
        expected=[];offset=0
        require(bool(passage['quote']), 'Empty supporting quote')
        while (found:=text.find(passage['quote'],offset))>=0:
            expected.append([found,found+len(passage['quote'])]);offset=found+1
        require(located['exact_quote_spans']==expected, 'Supporting quote spans incomplete or changed')
    return all(len(p['exact_quote_spans'])==1 for p in locations)


def matches_gold(candidate,slot):
    if candidate['target_table']!=slot['table'] or candidate['target_field']!=slot['field']:
        return False
    if candidate.get('field_schema_errors'):return False
    value=candidate['value']
    def match(actual,expected):
        if isinstance(expected,dict):
            return isinstance(actual,dict) and all(k in actual and match(actual[k],v) for k,v in expected.items())
        if isinstance(expected,(int,float)) and not isinstance(expected,bool):
            return type(actual) in (int,float) and actual==expected
        return actual==expected
    if 'required_terms' in slot:
        return isinstance(value,str) and all(t.casefold() in ' '.join(value.casefold().split()) for t in slot['required_terms'])
    required=slot['required']
    if slot['field']=='thresholds':
        units={'square feet','square foot','sq ft','sqft','ft2','ft²'}
        unit=lambda value: 'square feet' if value.casefold() in units else value.casefold()
        for item in value:
            if (item['value']==required['value'] and item['operator']==required['operator']
                    and unit(item.get('unit') or '')==unit(required['unit'])
                    and required['aggregation_rule'] in (item.get('aggregation_rule') or '').casefold()
                    and required['measurement_basis_contains'] in (item.get('measurement_basis') or '').casefold()):
                return True
        return False
    return match(value,required)


def agreement(first,second):
    require(first.keys()==second.keys() and first,'Review populations differ or are empty')
    n=len(first);same=sum(first[k]==second[k] for k in first)
    a,b=Counter(first.values()),Counter(second.values())
    expected=sum(a[k]*b[k] for k in set(a)|set(b))/n**2
    observed=same/n
    return {'candidate_count':n,'matching_labels':same,'observed_agreement':observed,
            'cohens_kappa':(observed-expected)/(1-expected) if expected<1 else None,
            'scope':'Agreement of two source-informed AI review runs, not accuracy or independent truth.'}


def audit(run,protocol_path,gold_path,coordinator_path,reviewer_paths):
    protocol=load(protocol_path);private=load(run/'protocol.private.json');gold=load(gold_path)
    require(sha(protocol_path)==private['public_protocol_sha256'] and sha(gold_path)==private['gold_sha256'],'Frozen protocol/gold drift')
    transport=load(protocol_path.parent/'sdk-retry-audit.json')
    verify_frozen_code(run, transport['files_sha256'])
    require(transport['provider_http_attempt_count'] is not None or not transport['strict_provider_cap_verified'],'Missing HTTP-attempt evidence cannot verify a provider cap')
    require(len(reviewer_paths)==2,'Exactly two independent CLI reviews required')
    verify_frozen_code(run, protocol['code_sha256'])
    require(all(sha(Path(p))==h for p,h in protocol['canonical_inputs_sha256'].items()),'Canonical input changed during evaluation')
    require(Path('data/expanded').resolve().name==protocol['canonical_snapshot'],'Canonical snapshot changed during evaluation')
    require(load(run/'terminal.private.json')['state']=='batch_terminal','Batch not terminal')
    candidates={};case_reports=[];source_texts={};artifacts={};calls=0;charged=0;success_cost=0
    for case in private['cases']:
        name=case['case_id'];directory=run/name;state=load(directory/'state.private.json');result=load(directory/'domain-candidates.private.json');status=load(directory/'evaluation-status.private.json')
        require(sha(Path(case['body_path']))==case['source']['body_sha256'] and sha(Path(case['text_path']))==case['source']['text_sha256'],'Source body/text drift')
        text=Path(case['text_path']).read_text();source_texts[name]=text
        require(status['state']=='finished' and status['replay_without_calls'] and sha(directory/'domain-candidates.private.json')==status['result_sha256'],'Unfinished or drifted candidate/replay result')
        require(digest(state['context'])==state['context_sha256']==result['context_sha256'],'Extraction context drift')
        require(state['context']['document']['text']==text and state['context']['document']['body_sha256']==case['source']['body_sha256'],'Extraction document differs from freeze')
        require(state['context']['question'].startswith(protocol['question']+'\n'),'Extraction question differs from freeze')
        require(all(state['context']['model_identity'][k]==v for k,v in protocol['model_identity'].items()),'Model settings differ from freeze')
        require(state['context']['max_calls']==case['max_calls'] and state['context']['budget_policy']['max_usd']==case['max_usd'],'Budget context mismatch')
        require(all(a['reserved_usd']==case['reservation_usd'] for a in state['attempts']),'Per-request reservation mismatch')
        require(len(state['attempts'])<=case['max_calls'],'Call cap exceeded')
        for success in state['successes'].values():require(digest(success['output'])==success['output_sha256'],'Model cache output drift')
        cost=sum(a.get('charged_usd',a['reserved_usd']) for a in state['attempts'])
        require(math.isfinite(cost) and cost<=case['max_usd']+1e-9,'Dollar allocation cap exceeded')
        require(all(a['status']=='succeeded' and a['accounting']['priced'] for a in state['attempts']),'Unreconciled/failed/unpriced extraction attempt')
        require(all(a['accounting']['model']==protocol['model_identity']['model'] for a in state['attempts']),'Returned model differs from freeze')
        ledger=[json.loads(s) for s in (directory/'calls.private.jsonl').read_text().splitlines()]
        require(len(ledger)==len(state['attempts']) and all(r['attempts']==1 for r in ledger),'Provider/backend call accounting differs')
        require(abs(sum(r['cost_usd'] for r in ledger)-cost)<1e-9,'Backend/adapter cost mismatch')
        calls+=len(state['attempts']);charged+=cost;success_cost+=sum(a['accounting']['cost_usd'] for a in state['attempts'])
        require(result['canonical_records_written']==0 and all(not c['accepted'] for c in result['candidates']),'Candidate automatically promoted')
        for candidate in result['candidates']:
            key=name,candidate['candidate_id'];require(key not in candidates,'Duplicate candidate ID');candidates[key]=candidate
            require(candidate['body_sha256']==case['source']['body_sha256'] and candidate['text_sha256']==case['source']['text_sha256'],'Candidate source identity mismatch')
            for a,b in candidate['exact_quote_spans']:require(text[a:b]==candidate['quote'],'Candidate quote/span mismatch')
            verify_support_locations(candidate,text)
        case_reports.append({'case_id':name,'candidates':len(result['candidates']),'model_requests':len(state['attempts']),'estimated_charged_usd':cost,
                             'full_supplied_text_chunk_coverage':result['full_text_chunk_coverage'],'chunks':len(state['chunks']),
                             'successful_chunks':sum(c['status']=='succeeded' for c in state['chunks']),'replay_without_calls':True})
        for filename in ['state.private.json','domain-candidates.private.json','calls.private.jsonl','evaluation-status.private.json']:
            artifacts[str(directory/filename)]=sha(directory/filename)
    require(calls<=protocol['max_calls'] and charged<=protocol['max_allocations_usd']+1e-9,'Aggregate extraction cap exceeded')
    expected_slots={(case,s['slot']):s for case,slots in gold.items() for s in slots}
    reviews=[];public_hash=sha(protocol_path);private_hash=sha(run/'protocol.private.json')
    for path in [coordinator_path,*reviewer_paths]:
        review=load(path);require(review['protocol_sha256'] in (public_hash,private_hash),'Review protocol reference drift')
        labels={};entries={}
        for row in review['candidates']:
            key=row['case_id'],row['candidate_id'];require(key in candidates and key not in labels and row['disposition'] in LABELS,'Review coverage/label mismatch')
            require(type(row['high_impact']) is bool and row['rationale'].strip(),'Incomplete review rationale/severity')
            for span in row['source_spans']:
                require(len(span)==2 and all(type(n) is int for n in span) and 0<=span[0]<span[1]<=len(source_texts[key[0]]),'Review span outside original text')
            require(row['disposition']!='supported' or row['source_spans'],'Supported label lacks source localization')
            labels[key]=row['disposition'];entries[key]=row
        require(labels.keys()==candidates.keys(),'Reviewer omitted/added candidates')
        slot_labels={}
        for row in review['slots']:
            key=row['case_id'],row['slot'];require(key in expected_slots and key not in slot_labels,'Review slot coverage mismatch')
            gold_slot=expected_slots[key]
            for ident in row['matched_candidate_ids']:
                ckey=row['case_id'],ident;require(ckey in labels and labels[ckey]=='supported','Gold match uses unaccepted candidate')
                candidate=candidates[ckey];require(candidate['target_table']==gold_slot['table'] and candidate['target_field']==gold_slot['field'],'Gold match field mismatch')
                require(matches_gold(candidate,gold_slot),'Claimed gold match does not satisfy frozen value/basis requirements')
            slot_labels[key]=bool(row['matched_candidate_ids'])
        require(slot_labels.keys()==expected_slots.keys(),'Reviewer omitted gold slots')
        reviews.append({'reviewer_id':review['reviewer_id'],'labels':labels,'entries':entries,'slots':slot_labels,'file_sha256':sha(path),'protocol_reference_sha256':review['protocol_sha256']})
    require(len({r['reviewer_id'] for r in reviews})==3,'Distinct reviewer labels required')
    final=reviews[0];n=len(candidates);supported=sum(v=='supported' for v in final['labels'].values());matched=sum(final['slots'].values())
    located=sum(bool(c['exact_quote_spans']) for c in candidates.values());valid=sum(not c['field_schema_errors'] for c in candidates.values())
    ambiguous_quotes=sum(len(c['exact_quote_spans'])>1 for c in candidates.values());high_errors=sum(r['high_impact'] and r['disposition'] in ('unsupported','off_target') for r in final['entries'].values())
    high_ambiguities=sum(r['high_impact'] and r['disposition']=='ambiguous' for r in final['entries'].values())
    thresholds=protocol['thresholds'];criteria={'located_quotes':located/n>=thresholds['located_quote_fraction'],'field_schema':valid/n>=thresholds['field_schema_valid_fraction'],
        'supported_relevant_candidates':supported/n>=thresholds['source_supported_relevant_candidate_fraction'],'required_slots':matched/len(expected_slots)>=thresholds['required_slot_recall'],
        'confirmed_high_impact_errors':high_errors==0,'full_text_coverage':all(c['full_supplied_text_chunk_coverage'] for c in case_reports),'no_canonical_writes':True,
        'strict_provider_request_cap_verified':transport['strict_provider_cap_verified']}
    for case in case_reports:
        name=case['case_id'];keys=[k for k in candidates if k[0]==name];case['supported']=sum(final['labels'][k]=='supported' for k in keys);case['unresolved']=sum(final['labels'][k]=='ambiguous' for k in keys)
        case['support_fraction']=case['supported']/len(keys);case['required_slots']=sum(k[0]==name for k in expected_slots);case['matched_slots']=sum(v for k,v in final['slots'].items() if k[0]==name)
        case['review_ready']=(case['full_supplied_text_chunk_coverage']
            and case['support_fraction']>=thresholds['source_supported_relevant_candidate_fraction']
            and case['matched_slots']/case['required_slots']>=thresholds['required_slot_recall']
            and all(not candidates[k]['field_schema_errors'] and candidates[k]['exact_quote_spans']
                    and verify_support_locations(candidates[k],source_texts[name]) for k in keys)
            and not any(final['entries'][k]['high_impact'] and final['labels'][k]!='supported' for k in keys))
    ready=sum(c['review_ready'] for c in case_reports)
    return {'schema_version':'domain-evaluation-audit-1','protocol_sha256':public_hash,'private_protocol_sha256':private_hash,'gold_sha256':sha(gold_path),'cases':case_reports,
        'metrics':{'candidate_count':n,'supported_candidates':supported,'ambiguous_candidates':sum(v=='ambiguous' for v in final['labels'].values()),'confirmed_unsupported_candidates':sum(v=='unsupported' for v in final['labels'].values()),
        'supported_relevant_fraction':supported/n,'schema_valid_candidates':valid,'located_quote_candidates':located,'multiple_location_quotes':ambiguous_quotes,'required_slots':len(expected_slots),'matched_slots':matched,'required_slot_recall':matched/len(expected_slots),
        'confirmed_high_impact_errors':high_errors,'high_impact_ambiguities':high_ambiguities,'review_ready_documents':ready,'estimated_usd_per_review_ready_document':charged/ready if ready else None,
        'discovery_recall':None,'false_exclusion_rate':None,'primary_recovery_rate':None,'unmeasured_scope':'Sources were preselected/recovered; no discovery or relevance-exclusion experiment.'},
        'frozen_gate_criteria':criteria,'frozen_gate_passed':all(criteria.values()),
        'reviewer_metrics':[{'reviewer_id':r['reviewer_id'],'labels':dict(Counter(r['labels'].values())),'matched_slots':sum(r['slots'].values()),'review_file_sha256':r['file_sha256'],'protocol_reference_sha256':r['protocol_reference_sha256']} for r in reviews],
        'cli_reviewer_agreement':agreement(reviews[1]['labels'],reviews[2]['labels']),
        'issues':[{'case_id':k[0],'candidate_id':k[1],'table':candidates[k]['target_table'],'field':candidates[k]['target_field'],'disposition':row['disposition'],'high_impact_if_accepted':row['high_impact'],'rationale':row['rationale']} for k,row in final['entries'].items() if row['disposition']!='supported'],
        'spend':{'accounted_backend_calls':calls,'provider_http_attempts':None,'observed_default_sdk_max_retries':transport['sdk_max_retries'],
                 'strict_provider_request_cap_verified':False,'estimated_success_cost_usd':success_cost,'backend_allocation_charged_usd':charged,
                 'backend_call_cap':protocol['max_calls'],'intended_provider_request_cap':protocol['max_calls'],'max_backend_allocations_usd':protocol['max_allocations_usd'],
                 'cli_review_jobs':2,'cli_spend_usd':None,'basis':'Installed bc-llm successful-call estimates and backend reservation ledger. Provider HTTP retries/failed-attempt charges are unobserved; no invoice or campaign-wide total.'},
        'artifact_sha256':artifacts,'canonical_records_written':0,'scope':'Frozen prospective extraction evaluation of previously reviewed sources, followed by AI/source adjudication. Not historically unseen independent data, global discovery quality, source reacquisition, canonical acceptance or completed P4.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--gold',type=Path,required=True);p.add_argument('--coordinator',type=Path,required=True);p.add_argument('--reviewer',type=Path,action='append',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=audit(args.run,args.protocol,args.gold,args.coordinator,args.reviewer);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('metrics','spend','frozen_gate_passed')},indent=2))
