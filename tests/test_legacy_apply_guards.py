"""A conflict anywhere must prevent partial writes; state decisions pin source rows."""
import contextlib
import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name+'.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


class ApplyGuards(unittest.TestCase):
    def run_case(self, name, stale=False, dry=False):
        m = module(name)
        is_policy = name == 'apply_legislation'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'data').mkdir()
            csv_path = root/'data'/('state_legislation.csv' if is_policy else 'moratorium_inventory.csv')
            # Use the real published schema/column set, but a local isolated row copy.
            with (ROOT/'data'/csv_path.name).open(newline='') as f:
                reader=csv.DictReader(f); fields=reader.fieldnames; row=next(reader)
            with csv_path.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
            baseline=root/'baseline.json'; baseline.write_text(json.dumps([row]))
            if is_policy:
                decisions=[{'bill_key':row['state_abbrev']+':'+row['bill'], 'outcome':'corrected',
                    'fields':{'key_provisions':'new reviewed value'},'evidence':[{'url':'https://example.invalid','source_type':'other','supports':'fixture'}]}]
                if not stale:
                    decisions.append({'bill_key':'ZZ:missing','outcome':'corrected','fields':{'key_provisions':'bad'},'evidence':[{'url':'https://example.invalid','source_type':'other','supports':'fixture'}]})
            else:
                decisions=[{'moratorium_id':row['moratorium_id'],'outcome':'corrected',
                    'changes':{'trigger':{'from':row['trigger'],'to':'valid proposed edit','reason':'fixture'},
                               'outcome':{'from':'stale expected value','to':'bad','reason':'fixture'}},'evidence':[{'url':'https://example.invalid','source_type':'other','supports':'fixture'}]}]
            answer=root/'answers.json';answer.write_text(json.dumps({'state_abbrev':row['state_abbrev'],'researched_as_of':'2026-11-05','decisions':decisions}))
            if stale:
                changed=dict(row); changed['sponsors']='concurrent edit'
                with csv_path.open('w',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(changed)
            before=csv_path.read_bytes()
            argv=[name,'--answers',str(answer)]
            if is_policy:argv+=['--baseline',str(baseline)]
            if dry:argv+=['--dry-run']
            with patch.object(m,'REPO',root),patch.object(m,'LEG' if is_policy else 'INV',csv_path),patch.object(m,'AUDIT_DIR',root/'audit'),patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()):
                code=m.main()
            self.assertEqual(code,1)
            self.assertEqual(csv_path.read_bytes(),before)
            self.assertFalse((root/'audit').exists())

    def test_inventory_conflict_prevents_partial_write(self):
        self.run_case('apply_research')

    def test_policy_invalid_key_prevents_partial_write(self):
        self.run_case('apply_legislation')

    def test_policy_stale_baseline_refused(self):
        self.run_case('apply_legislation',stale=True)

    def test_dry_run_reports_conflict_as_failure(self):
        self.run_case('apply_legislation',dry=True)


if __name__ == '__main__': unittest.main()
