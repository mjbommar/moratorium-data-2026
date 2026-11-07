import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('headline_delta', ROOT/'scripts/build_refresh_headline_delta.py')
delta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delta)
sys.path.insert(0, str(ROOT/'scripts'))


class HeadlineDeltaTests(unittest.TestCase):
    def test_historical_projection_is_separate_from_current_lifecycle(self):
        scope = delta.ballot_scope(ROOT)
        self.assertEqual(scope['historical_projection']['summary']['total_canonical_measures'], 50)
        self.assertEqual(scope['current']['proposal_measure_records'],
                         sum(scope['current']['lifecycle_counts'].values()))
        self.assertEqual(scope['current']['frozen_groups_with_retained_canonical_ids'], 49)
        self.assertIn('litigated', scope['current']['lifecycle_counts'])

    def test_header_only_layout_change_is_reported(self):
        before = b'id,value\na,one\n'
        after = b'value,id\none,a\n'
        self.assertEqual(delta.indexed(before, 'id'), delta.indexed(after, 'id'))
        schema = delta.schema_difference(before, after)
        self.assertTrue(schema['column_layout_changed'])
        self.assertEqual(schema['added_columns'], [])
        self.assertEqual(schema['removed_columns'], [])

    def test_reject_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate canonical IDs'):
            delta.indexed(b'id,value\na,one\na,two\n', 'id')

    def test_reject_malformed_columns_and_empty_ids(self):
        for raw in (b'id,value,value\na,hidden,visible\n',
                    b'id,value\na,one,extra\n', b'id,value\na\n',
                    b'id,value\n,one\n', b'other,value\na,one\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                delta.indexed(raw, 'id')

    def test_missing_registry_cannot_hide_retirement(self):
        local_before = b'moratorium_id,enacted_status\na,active\nb,active\n'
        local_after = b'moratorium_id,enacted_status\na,active\n'
        policy = b'policy_action_id,bill_status_category,policy_instrument_type\np,unknown,bill\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'data').mkdir()
            (root/'data/moratorium_inventory.csv').write_bytes(local_after)
            (root/'data/state_legislation.csv').write_bytes(policy)
            def fake_git(root, *args):
                if args[0] == 'rev-parse':
                    return b'a' * 40 + b'\n'
                return local_before if args[1].endswith('moratorium_inventory.csv') else policy
            with patch.object(delta, 'git', fake_git), self.assertRaisesRegex(ValueError, 'Missing identity registry'):
                delta.build(root=root)

    def test_existing_report_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'history.json'
            original = b'{"historical":true}\n'
            path.write_bytes(original)
            result = subprocess.run([sys.executable, str(ROOT/'scripts/build_refresh_headline_delta.py'),
                                     '--output', str(path)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
