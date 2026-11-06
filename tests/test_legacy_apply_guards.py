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
    def test_same_second_receipts_are_preserved_under_concurrent_writes(self):
        from concurrent.futures import ThreadPoolExecutor
        m = module('apply_research')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stamp = '20261105T195550'
            original = root / f'apply-{stamp}.json'
            original.write_text('preserved original receipt\n')
            def write(number):
                return m.write_audit_receipt(root, stamp, {'changes': [number]})
            with ThreadPoolExecutor(max_workers=4) as pool:
                paths = list(pool.map(write, range(8)))
            self.assertEqual(original.read_text(), 'preserved original receipt\n')
            self.assertEqual(len(set(paths)), 8)
            self.assertEqual(len(list(root.glob('apply-*.json'))), 9)
            self.assertEqual({json.loads(p.read_text())['changes'][0] for p in paths},
                             set(range(8)))

    def test_distinct_successor_keeps_endpoint_and_replay_does_not_duplicate(self):
        m=module('apply_research')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();path=root/'data/moratorium_inventory.csv'
            with (ROOT/'data/moratorium_inventory.csv').open(newline='') as f:
                reader=csv.DictReader(f);fields=reader.fieldnames;row=next(reader)
            row.update(jurisdiction='Synthetic County',moratorium_id='zz-synthetic-2026',
                       legal_basis='Resolution 2026-1',enacted_status='replaced')
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerow(row)
            answer=root/'answer.json';answer.write_text(json.dumps({
                'state_abbrev':row['state_abbrev'],'researched_as_of':'2026-11-05','decisions':[],
                'new_candidates':[{'state':row['state'],'jurisdiction':row['jurisdiction'],
                    'jurisdiction_type':'County','legal_basis':'Resolution 2026-2',
                    'date_enacted_iso':'2026-07-06','duration_kind':'until_date',
                    'current_end_date_iso':'2027-05-26','enacted_status':'active','confidence':.9,
                    'evidence':[{'url':'https://example.invalid','source_type':'resolution','supports':'synthetic fixture'}]}]}))
            with patch.object(m,'REPO',root),patch.object(m,'INV',path),patch.object(m,'AUDIT_DIR',root/'audit'),patch.object(sys,'argv',['apply_research','--answers',str(answer)]),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(),0)
                first=path.read_bytes()
                self.assertEqual(m.main(),0)
                self.assertEqual(path.read_bytes(),first)
            with path.open(newline='') as f:result=list(csv.DictReader(f))
            self.assertEqual(len(result),2)
            successor=next(r for r in result if r['legal_basis']=='Resolution 2026-2')
            self.assertEqual(successor['current_end_date_iso'],'2027-05-26')
            self.assertEqual(result[0]['moratorium_id'],row['moratorium_id'])

    def run_case(self, name, stale=False, dry=False, candidate=False):
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
            payload={'state_abbrev':row['state_abbrev'],'researched_as_of':'2026-11-05','decisions':decisions}
            if candidate:
                payload['decisions']=[]
                payload['new_candidates']=[{'state':row['state'],'jurisdiction':'Synthetic Missing Status',
                    'jurisdiction_type':'City','confidence':0.9,'sectors':['data_center'],
                    'evidence':[{'url':'https://example.invalid','source_type':'other','supports':'fixture'}]}]
            answer=root/'answers.json';answer.write_text(json.dumps(payload))
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

    def test_candidate_without_reviewed_status_cannot_default_active(self):
        self.run_case('apply_research',candidate=True)

    def test_policy_invalid_key_prevents_partial_write(self):
        self.run_case('apply_legislation')

    def test_policy_stale_baseline_refused(self):
        self.run_case('apply_legislation',stale=True)

    def test_dry_run_reports_conflict_as_failure(self):
        self.run_case('apply_legislation',dry=True)


if __name__ == '__main__': unittest.main()
