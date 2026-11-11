"""Offline replay and fail-closed pin checks; never collects sources."""
import importlib.util
import json
from pathlib import Path
import tempfile
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('followup', ROOT / 'scripts/build_ballot_followup_plan.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
due = HERE.parent / 'ballot-current-accounting/due-work.json'
register = HERE / 'prior-review-register.json'
snapshot = ROOT / 'data/expanded'
plan = module.build(due, register, snapshot)
assert plan == json.loads((HERE / 'plan.json').read_text())
assert plan['task_count'] == 97
assert plan['operator_state_counts'] == {'prior_work_check_required': 89, 'distinct_evidence_required': 6, 'not_due': 2}
assert [r['original_task'] for r in plan['tasks']] == json.loads(due.read_text())['tasks']
checks = []
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'register.json'
    for name, mutate in [
        ('stale_due_work', lambda r: r.update(due_work_sha256='0' * 64)),
        ('stale_measure', lambda r: r['records'][0].update(measure_row_sha256='0' * 64)),
        ('stale_result', lambda r: r['records'][0].update(current_result_observation_ids=[])),
        ('broadened_task_scope', lambda r: r['records'][0].update(task_kinds=['implementation_followup'])),
        ('stale_prior_review', lambda r: r['records'][0]['prior_review'].update(sha256='0' * 64)),
    ]:
        candidate = json.loads(register.read_text())
        mutate(candidate)
        path.write_text(json.dumps(candidate))
        try:
            module.build(due, path, snapshot)
        except ValueError:
            checks.append(name)
        else:
            raise AssertionError('Accepted invalid guard: ' + name)
print(json.dumps({'exact_replay': True, 'all_97_original_tasks_preserved': True,
                  'fail_closed_checks': checks, 'canonical_writes': 0}, indent=2))
