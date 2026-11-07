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
sys.path.insert(0, str(ROOT / 'scripts'))
import atomic_csv


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name+'.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


class ApplyGuards(unittest.TestCase):
    def test_valid_writes_are_atomic_and_recoverable(self):
        for name in ('apply_research', 'apply_legislation'):
            expected = None
            for failure in ('success', 'dry', 'write', 'file_fsync', 'replace', 'directory_fsync', 'receipt'):
                with self.subTest(writer=name, failure=failure), tempfile.TemporaryDirectory() as tmp:
                    m = module(name)
                    policy = name == 'apply_legislation'
                    root = Path(tmp)
                    (root / 'data').mkdir()
                    path = root / 'data' / ('state_legislation.csv' if policy else 'moratorium_inventory.csv')
                    with (ROOT / 'data' / path.name).open(newline='') as f:
                        reader = csv.DictReader(f)
                        fields, row = reader.fieldnames, next(reader)
                    with path.open('w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=fields)
                        writer.writeheader(); writer.writerow(row)
                    path.chmod(0o640)
                    before = path.read_bytes()
                    baseline = root / 'baseline.json'
                    baseline.write_text(json.dumps([row]))
                    if policy:
                        decision = {'bill_key': row['state_abbrev'] + ':' + row['bill'],
                                    'outcome': 'corrected', 'fields': {'key_provisions': 'reviewed change'},
                                    'evidence': [{'url': 'https://example.invalid', 'source_type': 'other', 'supports': 'fixture'}]}
                    else:
                        decision = {'moratorium_id': row['moratorium_id'], 'outcome': 'corrected',
                                    'changes': {'trigger': {'from': row['trigger'], 'to': 'reviewed change', 'reason': 'fixture'}},
                                    'evidence': [{'url': 'https://example.invalid', 'source_type': 'other', 'supports': 'fixture'}]}
                    answer = root / 'answers.json'
                    answer.write_text(json.dumps({'state_abbrev': row['state_abbrev'],
                        'researched_as_of': '2026-11-05', 'decisions': [decision]}))
                    audit = root / 'audit'; audit.mkdir()
                    old_receipt = audit / 'existing.json'; old_receipt.write_bytes(b'existing receipt\n')
                    argv = [name, '--answers', str(answer)] + (['--baseline', str(baseline)] if policy else [])
                    if failure == 'dry': argv.append('--dry-run')
                    real_fdopen = atomic_csv.os.fdopen
                    real_fsync = atomic_csv.os.fsync
                    class FailingWriter:
                        def __init__(self, wrapped): self.wrapped = wrapped
                        def __enter__(self): self.wrapped.__enter__(); return self
                        def __exit__(self, *args): return self.wrapped.__exit__(*args)
                        def write(self, text):
                            self.wrapped.write(text[:20]); self.wrapped.flush()
                            raise OSError('injected staged write failure')
                    calls = []
                    def fsync(fd):
                        calls.append(fd)
                        if failure == 'file_fsync' and len(calls) == 1:
                            raise OSError('injected file fsync failure')
                        if failure == 'directory_fsync' and len(calls) == 2:
                            raise OSError('injected directory fsync failure')
                        return real_fsync(fd)
                    with contextlib.ExitStack() as stack:
                        stack.enter_context(patch.object(m, 'REPO', root))
                        stack.enter_context(patch.object(m, 'LEG' if policy else 'INV', path))
                        stack.enter_context(patch.object(m, 'AUDIT_DIR', audit))
                        stack.enter_context(patch.object(sys, 'argv', argv))
                        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                        if failure == 'write':
                            stack.enter_context(patch.object(atomic_csv.os, 'fdopen', side_effect=lambda *a, **k: FailingWriter(real_fdopen(*a, **k))))
                        if failure == 'replace':
                            stack.enter_context(patch.object(atomic_csv.os, 'replace', side_effect=OSError('injected replace failure')))
                        if failure in ('file_fsync', 'directory_fsync'):
                            stack.enter_context(patch.object(atomic_csv.os, 'fsync', side_effect=fsync))
                        if failure == 'receipt':
                            def fail_receipt(*args, **kwargs):
                                (audit / 'partial.json').write_bytes(b'{"partial":')
                                raise OSError('injected receipt failure')
                            if policy:
                                stack.enter_context(patch.object(Path, 'write_text', side_effect=fail_receipt))
                            else:
                                stack.enter_context(patch.object(m, 'write_audit_receipt', side_effect=fail_receipt))
                        if failure in ('write', 'file_fsync', 'replace', 'directory_fsync', 'receipt'):
                            with self.assertRaises(OSError): m.main()
                        else:
                            self.assertEqual(m.main(), 0)
                    after = path.read_bytes()
                    self.assertEqual(path.stat().st_mode & 0o777, 0o640)
                    self.assertEqual(list(path.parent.glob(f'.{path.name}.*.tmp')), [])
                    self.assertEqual(old_receipt.read_bytes(), b'existing receipt\n')
                    if failure in ('dry', 'write', 'file_fsync', 'replace'):
                        self.assertEqual(after, before)
                    else:
                        self.assertNotEqual(after, before)
                        if failure == 'success': expected = after
                        else: self.assertEqual(after, expected)
                        with path.open(newline='') as f:
                            result = list(csv.DictReader(f))
                        self.assertEqual(len(result), 1)
                        self.assertEqual(result[0]['key_provisions' if policy else 'trigger'], 'reviewed change')
                    receipts = list(audit.iterdir())
                    self.assertEqual(len(receipts), 2 if failure in ('success', 'receipt') else 1)
                    if failure == 'receipt':
                        self.assertEqual((audit / 'partial.json').read_bytes(), b'{"partial":')
                    if failure in ('receipt', 'success'):
                        with patch.object(m, 'REPO', root), patch.object(m, 'LEG' if policy else 'INV', path), \
                                patch.object(m, 'AUDIT_DIR', audit), patch.object(sys, 'argv', argv), \
                                contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(m.main(), 0)
                        self.assertEqual(path.read_bytes(), after)
                        self.assertEqual(len(list(audit.iterdir())), len(receipts))

    def test_prefixed_resolutions_remain_distinct_and_replay_is_stable(self):
        m = module('apply_research')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            path = root / 'data/moratorium_inventory.csv'
            with (ROOT / 'data/moratorium_inventory.csv').open(newline='') as f:
                reader = csv.DictReader(f)
                fields, row = reader.fieldnames, next(reader)
            row.update(jurisdiction='Synthetic County',
                       moratorium_id='zz-prefixed-original',
                       legal_basis='Resolution R-2026-26',
                       date_enacted_iso='2026-04-16', enacted_status='active',
                       sectors=json.dumps(['data_center']))
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
            answer = root / 'answer.json'
            answer.write_text(json.dumps({
                'state_abbrev': row['state_abbrev'],
                'researched_as_of': '2026-11-05', 'decisions': [],
                'new_candidates': [{
                    'state': row['state'], 'jurisdiction': row['jurisdiction'],
                    'jurisdiction_type': 'County', 'legal_basis': 'Resolution R-2026-27',
                    'date_enacted_iso': '2026-04-16', 'enacted_status': 'active',
                    'sectors': ['data_center'], 'confidence': .9,
                    'evidence': [{'url': 'https://example.invalid',
                                  'source_type': 'resolution', 'supports': 'synthetic fixture'}],
                }],
            }))
            with patch.object(m, 'REPO', root), patch.object(m, 'INV', path), \
                    patch.object(m, 'AUDIT_DIR', root / 'audit'), \
                    patch.object(sys, 'argv', ['apply_research', '--answers', str(answer)]), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(m.main(), 0)
                first = path.read_bytes()
                self.assertEqual(m.main(), 0)
                self.assertEqual(path.read_bytes(), first)
            with path.open(newline='') as f:
                result = list(csv.DictReader(f))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], row)
            self.assertEqual({r['legal_basis'] for r in result},
                             {'Resolution R-2026-26', 'Resolution R-2026-27'})

    def test_instrument_number_requires_number_not_adoption_prose(self):
        m = module('apply_research')
        for text in ['Resolution adopted April 16, 2026',
                     'Resolution pending review', 'Ordinance under consideration']:
            with self.subTest(text=text):
                self.assertEqual(m.instrument_key(text), '')

    def test_prefixed_number_is_not_consumed_as_optional_number_label(self):
        m = module('apply_research')
        cases = {
            'Ordinance OR-2026-0035': 'ordinance-or-2026-0035',
            'Ordinance ORD-26-00002': 'ordinance-ord-26-00002',
            'Ordinance No. O-26-03': 'ordinance-o-26-03',
            'Ordinance O2026-02': 'ordinance-o2026-02',
            'Ordinance No. O1689': 'ordinance-o1689',
            'Ord. No. 3063': 'ord-3063',
            'Resolution #21 FYR 25/26': 'resolution-21',
            'Resolution R-11-19-2025; Ordinance No. 1-2026':
                'resolution-r-11-19-2025',
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(m.instrument_key(text), expected)

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
