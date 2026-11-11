#!/usr/bin/env python3
"""Overlay pinned prior work on operator tasks without closing factual questions."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def row_digest(row):
    return digest(json.dumps(row, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False).encode())


def build(due_path, register_path, destination):
    due = json.loads(due_path.read_text())
    register = json.loads(register_path.read_text())
    snapshot = destination.resolve(strict=True)
    if snapshot.name != due['snapshot'] or register['snapshot'] != due['snapshot']:
        raise ValueError('Snapshot changed: refresh accounting and prior-work register')
    if digest(due_path.read_bytes()) != register['due_work_sha256']:
        raise ValueError('Due-work pin changed')
    for name, expected in due['source_hashes'].items():
        if digest((snapshot / (name + '.jsonl')).read_bytes()) != expected:
            raise ValueError('Native task input changed: ' + name)
    measures = {r['measure_id']: r for r in
                map(json.loads, (snapshot / 'ballot_measures.jsonl').read_text().splitlines())}
    results = list(map(json.loads, (snapshot / 'measure_results.jsonl').read_text().splitlines()))
    superseded = {r['supersedes_id'] for r in results if r.get('supersedes_id')}
    current = [r for r in results if r['result_observation_id'] not in superseded]
    reviews = {}
    for entry in register['records']:
        mid = entry['measure_id']
        if mid in reviews or mid not in measures:
            raise ValueError('Duplicate or unknown registered measure: ' + mid)
        ids = sorted(r['result_observation_id'] for r in current if r['measure_id'] == mid)
        if (row_digest(measures[mid]) != entry['measure_row_sha256']
                or ids != entry['current_result_observation_ids']):
            raise ValueError('Prior-work guard changed: ' + mid)
        pin = entry['prior_review']
        if digest((ROOT / pin['path']).read_bytes()) != pin['sha256']:
            raise ValueError('Prior review changed: ' + pin['path'])
        if entry['task_kinds'] != ['certification_or_recount']:
            raise ValueError('This register may gate certification lookup only')
        reviews[mid] = entry
    tasks = []
    for index, task in enumerate(due['tasks']):
        entry = reviews.get(task['measure_id'])
        applicable = entry and task['kind'] in entry['task_kinds']
        state = ('not_due' if not task['due_now'] else
                 'distinct_evidence_required' if applicable else 'prior_work_check_required')
        item = {'task_index': index, 'original_task': task, 'operator_state': state}
        if applicable:
            item.update(prior_review=entry['prior_review'],
                        resume_condition=entry['resume_condition'])
        tasks.append(item)
    assert [r['original_task'] for r in tasks] == due['tasks']
    return {'as_of': due['as_of'], 'snapshot': due['snapshot'],
            'due_work_sha256': digest(due_path.read_bytes()),
            'review_register_sha256': digest(register_path.read_bytes()),
            'task_count': len(tasks), 'registered_measures': len(reviews),
            'operator_state_counts': dict(Counter(r['operator_state'] for r in tasks)),
            'tasks': tasks,
            'scope': 'All original obligations retained. Prior bounded lookups are not '
                     'certification, closure, or evidence of absence. The register covers '
                     'only its named measures/task kind; other tasks still require a '
                     'prior-work check before collection. Dates are operator priorities, '
                     'not legal deadlines. No network or canonical mutation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--due-work', type=Path, required=True)
    parser.add_argument('--review-register', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=ROOT / 'data/expanded')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.due_work, args.review_register, args.destination)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'tasks'}, indent=2))
