#!/usr/bin/env python3
"""Offline review worklist; due dates are operator rules, never legal deadlines."""
import argparse
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tasks(measures, elections, results, today, lead_days=30):
    superseded = {r['supersedes_id'] for r in results if r.get('supersedes_id')}
    current = [r for r in results if r['result_observation_id'] not in superseded]
    output = []
    for measure in measures:
        mid = measure['measure_id']
        election = elections[measure['election_id']]
        interval = election['election_date']
        # Only an exact source-supported day can drive a calendar rule.
        exact = interval.get('earliest') if interval.get('precision') == 'day' and interval.get('earliest') == interval.get('latest') else None
        day = date.fromisoformat(exact) if exact else None
        observations = [r for r in current if r['measure_id'] == mid]
        def add(kind, due, reason, observation=None):
            output.append(dict(measure_id=mid, election_id=measure['election_id'], kind=kind,
                due_on=due.isoformat() if due else None, due_now=due is None or due <= today,
                result_observation_id=observation, reason=reason))
        if day is None:
            add('election_date_review', None, 'Exact election day unresolved; no partial-date midpoint inferred.')
            continue
        if day > today:
            add('qualification_and_ballot', day-timedelta(days=lead_days), 'Review final qualification/ballot before election; operator lead time, not statutory deadline.')
            add('election_results', day+timedelta(days=1), 'Collect post-election results without assuming certification.')
            continue
        if not observations:
            add('election_results', day+timedelta(days=1), 'Election date has passed; no current result observation supplied.')
        for observation in observations:
            if observation.get('certification_status') != 'certified':
                add('certification_or_recount', day+timedelta(days=1), 'Current observation is not explicitly certified; check administering authority and corrections.', observation['result_observation_id'])
        if measure.get('bindingness') != 'advisory':
            add('implementation_review', day+timedelta(days=1), 'Review adoption, effectiveness, litigation and later events separately; vote is not operative-law proof.')
    return sorted(output, key=lambda r: (not r['due_now'], r['due_on'] or '', r['measure_id'], r['kind'], r['result_observation_id'] or ''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--today', type=date.fromisoformat, required=True)
    parser.add_argument('--destination', type=Path, default=ROOT/'data/expanded')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot = args.destination.resolve(strict=True)
    def read(name):
        return [json.loads(line) for line in (snapshot/(name+'.jsonl')).read_text().splitlines()]
    work = tasks(read('ballot_measures'), {r['election_id']:r for r in read('elections')}, read('measure_results'), args.today)
    report = dict(as_of=args.today.isoformat(), snapshot=snapshot.name,
        scope='Operator review priorities only; no legal deadlines, renewed factual acceptance or status mutation. Certification and implementation remain independent.',
        source_hashes={n:hashlib.sha256((snapshot/(n+'.jsonl')).read_bytes()).hexdigest() for n in ['ballot_measures','elections','measure_results']},
        task_counts=dict(Counter(r['kind'] for r in work)), tasks=work,
        additional_worklists={'qualification_gaps':'work/audit/ballot-release-dispositions-2026-11-06.json',
            'legacy_expiry':'Run scripts/build_worklist.py --today YYYY-MM-DD; review anchors before computing expiry.'})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'task_counts': report['task_counts'], 'tasks': len(work)}, indent=2))
