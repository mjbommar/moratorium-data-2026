"""Read-only current-use inventory; flags are review work, not factual verdicts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def inspect(tables):
    measures={r['measure_id']:r for r in tables['ballot_measures']}
    claims={r['claim_id']:r for r in tables['claims']}
    decisions=tables['review_decisions']
    by_id={d['decision_id']:d for d in decisions}
    if len(by_id)!=len(decisions):raise ValueError('Duplicate decision ID')
    for decision in decisions:
        prior_id=decision.get('supersedes_id')
        if prior_id is None:continue
        prior=by_id.get(prior_id)
        if prior is None or prior['target']!=decision['target'] or prior['scope']!=decision['scope']:
            raise ValueError('Invalid decision supersession target or scope')
        visited={decision['decision_id']}
        while prior_id is not None:
            if prior_id in visited:raise ValueError('Decision supersession cycle')
            visited.add(prior_id);prior_id=by_id[prior_id].get('supersedes_id')
    superseded={d.get('supersedes_id') for d in decisions}

    def field_lineage(table, ident, field, value):
        current=[d for d in decisions if d['target']=={'table':table,'id':ident}
                 and d['scope']==field and d['decision_id'] not in superseded
                 and d['disposition']=='accepted']
        ids=sorted({cid for d in current for cid in d['claim_ids']})
        direct=[]
        for cid in ids:
            claim=claims[cid];cv=claim['value']
            if claim['subject']!={'table':table,'id':ident}:
                continue
            if (isinstance(cv,dict) and field in cv and cv[field]==value
                    or claim['predicate']==field and cv==value):
                direct.append(cid)
        return dict(current_accepted_decision_ids=sorted(d['decision_id'] for d in current),
                    accepted_decision_state='missing' if not current else 'single' if len(current)==1 else 'conflicting',
                    decision_details=[dict(decision_id=d['decision_id'],rationale=d['rationale'])
                                      for d in current if 'rationale' in d],
                    cited_claim_ids=ids,direct_named_value_claim_ids=direct,
                    direct_named_value_present=bool(direct))

    advisory=[]
    for provision in tables['measure_provisions']:
        mechanism=provision['mechanism']
        if mechanism not in ('advisory_support','advisory_opposition'):
            continue
        measure=measures[provision['measure_id']]
        expected={'advisory_support':'facilitates','advisory_opposition':'restricts'}[mechanism]
        flags=[]
        if provision['bindingness']!='advisory':flags.append('nonadvisory_provision')
        if measure['yes_direction']!=expected:flags.append('direction_requires_scope_review')
        lineage=field_lineage('measure_provisions',provision['provision_id'],'mechanism',mechanism)
        if lineage['accepted_decision_state']!='single':flags.append('mechanism_accepted_decision_'+lineage['accepted_decision_state'])
        if not lineage['direct_named_value_present']:flags.append('mechanism_claim_value_not_explicit')
        advisory.append(dict(provision_id=provision['provision_id'],measure_id=measure['measure_id'],
            mechanism=mechanism,yes_direction=measure['yes_direction'],
            expected_single_proposition_direction=expected,lineage=lineage,review_flags=flags))
    complete=[]
    superseded_results={r.get('supersedes_id') for r in tables['measure_results']}
    for result in tables['measure_results']:
        if result['reporting_status']!='complete':continue
        lineage=field_lineage('measure_results',result['result_observation_id'],'reporting_status','complete')
        flags=[]
        if not lineage['direct_named_value_present']:flags.append('reporting_status_claim_value_not_explicit')
        if lineage['accepted_decision_state']!='single':flags.append('reporting_status_accepted_decision_'+lineage['accepted_decision_state'])
        scope_lineage=field_lineage('measure_results',result['result_observation_id'],'reporting_scope',result.get('reporting_scope'))
        if result.get('reporting_scope') is None:flags.append('reporting_scope_not_recorded')
        elif scope_lineage['accepted_decision_state']!='single':flags.append('reporting_scope_accepted_decision_'+scope_lineage['accepted_decision_state'])
        complete.append(dict(result_observation_id=result['result_observation_id'],
            is_current=result['result_observation_id'] not in superseded_results,
            measure_id=result['measure_id'],source_document_id=result['source_document_id'],
            reporting_scope=result.get('reporting_scope'),certification_status=result['certification_status'],
            lineage=lineage,scope_lineage=scope_lineage,
            certification_lineage=field_lineage('measure_results',result['result_observation_id'],
                'certification_status',result['certification_status']),review_flags=flags))
    return dict(advisory_provisions=advisory,complete_result_observations=complete,
        mechanism_counts=dict(Counter(p['mechanism'] for p in tables['measure_provisions'])),
        reporting_status_counts=dict(Counter(r['reporting_status'] for r in tables['measure_results'])),
        current_reporting_status_counts=dict(Counter(r['reporting_status'] for r in tables['measure_results']
            if r['result_observation_id'] not in superseded_results)),
        scope='Structural current-use and explicit named-value lineage inventory. No source reacquisition, entailment judgment, automatic rejection or canonical writes.')


def audit(path):
    selected=path.resolve()
    names=['ballot_measures','measure_provisions','measure_results','claims','review_decisions']
    raw={n:(selected/f'{n}.jsonl').read_bytes() for n in names}
    result=inspect({n:[json.loads(line) for line in body.splitlines()] for n,body in raw.items()})
    return dict(schema_version='ballot-semantic-use-audit-1',snapshot=selected.name,
                table_sha256={n:hashlib.sha256(body).hexdigest() for n,body in raw.items()},**result)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,default=Path('data/expanded'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=audit(args.snapshot)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('snapshot','mechanism_counts','reporting_status_counts')},indent=2))
