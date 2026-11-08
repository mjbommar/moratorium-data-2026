import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_policy_scope_exports as exports
import build_summary_stats as stats
import build_release_candidate as release
import export_reviewed_handoff as handoff
from policy_scope_reviews import INFRASTRUCTURE_SCOPE, partition_reviews


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.raw = self.root / 'raw.csv'
        self.registry = self.root / 'registry.jsonl'
        self.output = self.root / 'out'
        self.rows = [dict(policy_action_id=str(i), state_abbrev='MD', bill='HB, "1"\ncontinued', policy_instrument_type='bill', note='original') for i in range(4)]
        self.write_csv()
        self.event = dict(schema_version='1.0.0', decision_id='f59ba12f-5a11-4875-901a-6dd7b3c6c7a0', policy_action_id='0', decision='include', analytical_scope=INFRASTRUCTURE_SCOPE, record_identity_guard=dict(state_abbrev='MD', bill='HB, "1"\ncontinued', policy_instrument_type='bill'), reviewed_record_sha256='a'*64, reviewer='reviewer', reviewed_at='2026-11-07T12:00:00Z', rationale='reason', source_evidence=[dict(url='https://example.org', body_sha256='b'*64, locator='page')], supersedes=None)

    def write_csv(self):
        with self.raw.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(self.rows[0]))
            w.writeheader(); w.writerows(self.rows)

    def write_events(self, *events):
        self.registry.write_text(''.join(json.dumps(e) + '\n' for e in events), encoding='utf-8')

    def events(self):
        events = []
        for i, (decision, uid) in enumerate([('include', 'f59ba12f-5a11-4875-901a-6dd7b3c6c7a0'), ('exclude', '43541d2a-d1c7-4b45-ae0f-9cc0f7a14788'), ('unresolved', '853dff18-9352-44e0-83c0-7cdb97ba9ff2')]):
            events.append(dict(self.event, decision=decision, policy_action_id=str(i), decision_id=uid))
        return events

    def test_four_outcomes_order_escaping_and_input_immutability(self):
        self.write_events(*self.events())
        before = self.raw.read_bytes(), self.registry.read_bytes()
        result = exports.render(self.raw, self.registry)
        all_rows = list(csv.DictReader(io.StringIO(result[exports.ALL].decode(), newline='')))
        self.assertEqual([r['scope_review_status'] for r in all_rows], ['reviewed_include', 'reviewed_exclude', 'reviewed_unresolved', 'unreviewed'])
        self.assertEqual([{k:r[k] for k in self.rows[0]} for r in all_rows], self.rows)
        self.assertEqual([r['policy_action_id'] for r in csv.DictReader(io.StringIO(result[exports.CANDIDATES].decode()))], ['0', '2', '3'])
        self.assertEqual([r['policy_action_id'] for r in csv.DictReader(io.StringIO(result[exports.INCLUDED].decode()))], ['0'])
        self.assertEqual((self.raw.read_bytes(), self.registry.read_bytes()), before)
        self.assertEqual(result, exports.render(self.raw, self.registry))

    def test_missing_registry_header_only_and_invalid_ids(self):
        data = exports.render(self.raw, self.registry)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(data[exports.INCLUDED].decode())))), 0)
        self.assertIsNone(json.loads(data[exports.RECEIPT])['inputs']['registry_sha256'])
        self.assertEqual(len(list(csv.DictReader(io.StringIO(data[exports.CANDIDATES].decode())))), 4)
        for ident in ('', ' ', '0'):
            rows = copy.deepcopy(self.rows); rows[1]['policy_action_id'] = ident
            with self.subTest(ident=ident), self.assertRaises(ValueError):
                partition_reviews(rows, self.registry, scope=INFRASTRUCTURE_SCOPE)
        rows = copy.deepcopy(self.rows); del rows[1]['policy_action_id']
        with self.assertRaises(ValueError): partition_reviews(rows, self.registry, scope=INFRASTRUCTURE_SCOPE)

    def test_empty_header_validation_before_write(self):
        self.write_events()
        exports.sync(exports.render(self.raw, self.registry), self.output, boundary=self.root)
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.raw.write_text('wrong_header\n')
        with self.assertRaisesRegex(ValueError, 'policy_action_id'):
            exports.sync(exports.render(self.raw, self.registry), self.output, boundary=self.root)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        self.raw.write_text('policy_action_id,state\n')
        result = exports.render(self.raw, self.registry)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(result[exports.INCLUDED].decode())))), 0)

    def test_symlink_boundary_ancestors_and_entries(self):
        artifacts = exports.render(self.raw, self.registry)
        outside = self.root/'outside'; outside.mkdir()
        (self.root/'redirect').symlink_to(outside, target_is_directory=True)
        for check in (False, True):
            with self.assertRaises(ValueError):
                exports.sync(artifacts, self.root/'redirect'/'out', check=check, boundary=self.root)
        self.assertEqual(list(outside.iterdir()), [])
        self.output.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError): exports.sync(artifacts, self.output, boundary=self.root)
        self.output.unlink(); self.output.mkdir()
        (self.output/exports.ALL).symlink_to(outside/'victim')
        with self.assertRaises(ValueError): exports.sync(artifacts, self.output, boundary=self.root)
        self.assertFalse((outside/'victim').exists())
        (self.output/exports.ALL).unlink()
        alias = self.root.parent/(self.root.name + '-alias')
        alias.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(alias.unlink)
        exports.sync(artifacts, alias/'out', boundary=alias)
        self.assertTrue(exports.sync(artifacts, alias/'out', boundary=alias, check=True))

    def test_scope_guards_supersession_and_collisions(self):
        wrong = dict(self.event, analytical_scope='other')
        self.write_events(wrong)
        with self.assertRaisesRegex(ValueError, 'incompatible analytical_scope'): exports.render(self.raw, self.registry)
        stale = copy.deepcopy(self.event); stale['record_identity_guard']['bill'] = 'changed'
        self.write_events(stale)
        with self.assertRaisesRegex(ValueError, 'guard mismatch'): exports.render(self.raw, self.registry)
        self.registry.write_text('{bad}\n')
        with self.assertRaises(ValueError): exports.render(self.raw, self.registry)
        successor = dict(self.event, decision='exclude', decision_id='43541d2a-d1c7-4b45-ae0f-9cc0f7a14788', supersedes=self.event['decision_id'])
        self.write_events(self.event, successor)
        row = list(csv.DictReader(io.StringIO(exports.render(self.raw, self.registry)[exports.ALL].decode())))[0]
        self.assertEqual((row['scope_review_status'], row['scope_decision_id']), ('reviewed_exclude', successor['decision_id']))
        self.rows[0]['scope_decision_id'] = 'source'; self.write_csv()
        with self.assertRaisesRegex(ValueError, 'collision'): exports.render(self.raw, self.registry)

    def test_check_drift_missing_and_extra(self):
        artifacts = exports.render(self.raw, self.registry)
        self.assertFalse(exports.sync(artifacts, self.output, check=True, boundary=self.root))
        exports.sync(artifacts, self.output, boundary=self.root)
        self.assertTrue(exports.sync(artifacts, self.output, check=True, boundary=self.root))
        (self.output / exports.ALL).write_text('drift')
        self.assertFalse(exports.sync(artifacts, self.output, check=True, boundary=self.root))
        (self.output / exports.ALL).unlink()
        self.assertFalse(exports.sync(artifacts, self.output, check=True, boundary=self.root))
        (self.output / 'extra').write_text('do not remove')
        for check in (True, False):
            with self.assertRaisesRegex(ValueError, 'unexpected'): exports.sync(artifacts, self.output, check=check, boundary=self.root)
        self.assertEqual((self.output / 'extra').read_text(), 'do not remove')

    def test_summary_uses_registry_and_keeps_raw_count(self):
        policies = [dict(r, state='Maryland', activity_level='Low') for r in self.rows]
        with patch.object(stats, 'load', side_effect=lambda p: [] if p == stats.INV else policies), patch.object(stats, 'STATS', self.root/'stats.json'), patch.object(stats, 'SWEEP', self.root/'sweep.json'), patch.object(stats, 'STATES_DIR', self.root/'states'), patch.object(stats, 'SCOPE_REGISTRY', self.registry):
            empty = stats.build()
            self.write_events(*self.events())
            reviewed = stats.build()
        self.assertEqual(empty['total_state_policy_actions'], reviewed['total_state_policy_actions'])
        self.assertEqual(empty['policy_scope_review']['partition_counts']['unreviewed'], 4)
        self.assertEqual(reviewed['policy_scope_review']['partition_counts'], dict(reviewed_include=1, reviewed_exclude=1, reviewed_unresolved=1, unreviewed=1))

    def test_summary_check_detects_registry_change(self):
        policies = [dict(r, state='Maryland', activity_level='Low') for r in self.rows]
        with patch.object(stats, 'load', side_effect=lambda p: [] if p == stats.INV else policies), patch.object(stats, 'STATS', self.root/'stats.json'), patch.object(stats, 'SWEEP', self.root/'sweep.json'), patch.object(stats, 'STATES_DIR', self.root/'states'), patch.object(stats, 'SCOPE_REGISTRY', self.registry), patch.object(sys, 'argv', ['build_summary_stats.py', '--check']), patch('sys.stdout', new_callable=io.StringIO):
            stats.STATS.write_text(json.dumps(stats.build(), indent=2) + '\n')
            self.assertEqual(stats.main(), 0)
            self.write_events(self.event)
            self.assertEqual(stats.main(), 1)

    def test_release_and_handoff_selection(self):
        commit = release.git('rev-parse', 'HEAD^{commit}').decode().strip()
        names = release.git('ls-tree', '-r', '--name-only', commit).decode().splitlines()
        extra = ['scripts/build_policy_scope_exports.py', 'docs/policy-scope-exports.md'] + ['data/policy-scope/'+n for n in exports.NAMES]
        selected = release.select_files(commit, names + extra)
        self.assertTrue(set(extra) <= set(selected))
        with self.assertRaisesRegex(AssertionError, 'Unexpected policy-scope output set'): release.select_files(commit, names + extra + ['data/policy-scope/extra.csv'])
        with self.assertRaisesRegex(AssertionError, 'Incomplete policy-scope'): release.select_files(commit, names + [n for n in extra if not n.endswith('receipt.json')])
        source = self.root/'source'; source.mkdir()
        for d in ('data/expanded-snapshots/g', 'data/expanded-csv-snapshots/g', 'scripts'):
            (source/d).mkdir(parents=True)
        (source/'data/expanded').symlink_to('expanded-snapshots/g'); (source/'data/expanded-csv').symlink_to('expanded-csv-snapshots/g')
        (source/'scripts/build_policy_scope_exports.py').touch()
        with self.assertRaisesRegex(ValueError, 'Incomplete policy-scope'): handoff.alias_specs(source)
        for name in ['data/moratorium_inventory.csv', 'data/state_legislation.csv', 'data/summary_stats.json', 'data/state_policy_scope_reviews.jsonl', 'docs/policy-scope-exports.md', 'data/expanded-snapshots/g/publication.json'] + ['data/policy-scope/'+n for n in exports.NAMES]:
            p=source/name; p.parent.mkdir(parents=True, exist_ok=True); p.touch()
        aliases = {a['path'] for a in handoff.alias_specs(source)}
        self.assertTrue({'data/state_policy_scope_reviews.jsonl','docs/policy-scope-exports.md'} | {'data/policy-scope/'+n for n in exports.NAMES} <= aliases)


if __name__ == '__main__': unittest.main()
