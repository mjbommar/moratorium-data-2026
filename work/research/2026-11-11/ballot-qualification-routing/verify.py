"""Replay qualification routing; preserve every factual obligation and native byte."""
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def row_digest(row):
    return digest(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())

def build(register):
    pointer=register['base_plan'];path=ROOT/pointer['path']
    if digest(path.read_bytes())!=pointer['sha256']:
        raise ValueError('Prior certification plan changed')
    base=json.loads(path.read_text());snapshot=ROOT/'data/expanded'
    if snapshot.resolve().name!=register['snapshot'] or base['snapshot']!=register['snapshot']:
        raise ValueError('Native snapshot changed')
    for name,pin in register['native_pins'].items():
        if digest((snapshot/(name+'.jsonl')).read_bytes())!=pin:
            raise ValueError('Native input changed: '+name)
    measures={r['measure_id']:r for r in map(json.loads,(snapshot/'ballot_measures.jsonl').read_text().splitlines())}
    docs={r['source_document_id']:r for r in map(json.loads,(snapshot/'source_documents.jsonl').read_text().splitlines())}
    records=register['records']
    if len(records)!=4 or [r['task_index']for r in records]!=[0,1,2,3]:
        raise ValueError('Qualification scope changed')
    plan=copy.deepcopy(base)
    for entry in records:
        i=entry['task_index'];task=plan['tasks'][i];original=task['original_task'];mid=entry['measure_id']
        if (entry['task_kind']!='qualification_history_review' or original['kind']!=entry['task_kind']
            or original['measure_id']!=mid or row_digest(original)!=entry['original_task_sha256']
            or row_digest(measures[mid])!=entry['measure_row_sha256']
            or task['operator_state']!='prior_work_check_required'):
            raise ValueError('Task or measure guard changed')
        for pin in entry['prior_reviews']:
            if digest((ROOT/pin['path']).read_bytes())!=pin['sha256']:
                raise ValueError('Prior review changed')
        for document in entry['current_source_documents']:
            if docs.get(document['source_document_id'])!=document:
                raise ValueError('Current source version changed')
        task.update(operator_state='distinct_evidence_required',qualification_prior_work=entry)
    if [r['original_task']for r in plan['tasks']]!=[r['original_task']for r in base['tasks']]:
        raise ValueError('Factual obligations changed')
    if plan['tasks'][4:]!=base['tasks'][4:]:
        raise ValueError('Unrelated routing changed')
    counts=dict(Counter(r['operator_state']for r in plan['tasks']))
    if counts!={'distinct_evidence_required':10,'prior_work_check_required':85,'not_due':2}:
        raise ValueError('Task accounting changed')
    plan.update(operator_state_counts=counts,qualification_register_sha256=digest((HERE/'qualification-prior-work-register.json').read_bytes()),qualification_prior_work_records=4,scope='All97original obligations preserved. Four qualificationpriorwork checks supplement the prior certificationrouting; only repeatedcollection is gated. No new evidenceacceptance, result, certification, legalforce or closure. Operatorprioritydates are not legaldeadlines.')
    return plan

if __name__=='__main__':
    register=json.loads((HERE/'qualification-prior-work-register.json').read_text())
    plan=build(register)
    assert plan==json.loads((HERE/'plan.json').read_text())
    rejected=[]
    for name,mutate in [
        ('stale_base_plan',lambda r:r['base_plan'].update(sha256='0'*64)),
        ('stale_native',lambda r:r['native_pins'].update(ballot_measures='0'*64)),
        ('stale_measure',lambda r:r['records'][0].update(measure_row_sha256='0'*64)),
        ('wrong_task_kind',lambda r:r['records'][0].update(task_kind='implementation_review')),
        ('stale_review',lambda r:r['records'][0]['prior_reviews'][0].update(sha256='0'*64)),
        ('changed_source',lambda r:r['records'][0]['current_source_documents'][0].update(body_sha256='0'*64)),
        ('omitted_task',lambda r:r['records'].pop()),
    ]:
        value=copy.deepcopy(register);mutate(value)
        try:build(value)
        except ValueError:rejected.append(name)
        else:raise AssertionError('Stale/overbroad routing accepted: '+name)
    print(json.dumps({'tasks_preserved':97,'qualification_tasks_routed':4,'other_93_tasks_identical':True,'operator_state_counts':plan['operator_state_counts'],'negative_pin_checks':rejected},indent=2))
