import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from policy_scope_reviews import load_reviews
import validate_dataset


class PolicyScopeReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'reviews.jsonl'
        self.rows = [dict(policy_action_id='md-example-2026', state_abbrev='MD',
                          bill='HB 1 / SB 2', policy_instrument_type='bill', note='current')]
        self.event = dict(schema_version='1.0.0', decision_id='f59ba12f-5a11-4875-901a-6dd7b3c6c7a0',
                          policy_action_id='md-example-2026', decision='exclude',
                          analytical_scope='infrastructure policy',
                          record_identity_guard=dict(state_abbrev='MD', bill='HB 1 / SB 2', policy_instrument_type='bill'),
                          reviewed_record_sha256='a'*64, reviewer='Example reviewer',
                          reviewed_at='2026-11-07T12:00:00-05:00', rationale='Illustrative decision.',
                          source_evidence=[dict(url='https://example.org/source', body_sha256='b'*64, locator='Section 1')],
                          supersedes=None)

    def write(self, *events):
        self.path.write_text(''.join(json.dumps(e) + '\n' for e in events), encoding='utf-8')

    def test_missing_registry_and_historical_row_hash(self):
        self.assertEqual(load_reviews(self.path, self.rows), {})
        self.write(self.event)
        self.rows[0]['note'] = 'later unrelated change'
        self.assertEqual(load_reviews(self.path, self.rows)['md-example-2026'], self.event)

    def test_stale_guard_or_unknown_id_fails(self):
        self.write(self.event)
        for field in ('state_abbrev', 'bill', 'policy_instrument_type'):
            rows = copy.deepcopy(self.rows)
            rows[0][field] += ' changed'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'guard mismatch'):
                load_reviews(self.path, rows)
        with self.assertRaisesRegex(ValueError, 'exactly one dataset row'):
            load_reviews(self.path, [])
        with self.assertRaisesRegex(ValueError, 'exactly one dataset row'):
            load_reviews(self.path, self.rows * 2)

    def test_supersession_and_ambiguous_history(self):
        second = copy.deepcopy(self.event)
        second.update(decision_id='43541d2a-d1c7-4b45-ae0f-9cc0f7a14788', decision='unresolved', supersedes=self.event['decision_id'])
        self.write(self.event, second)
        self.assertEqual(load_reviews(self.path, self.rows)['md-example-2026'], second)
        third = copy.deepcopy(second)
        third['decision_id'] = '853dff18-9352-44e0-83c0-7cdb97ba9ff2'
        for supersedes in (None, self.event['decision_id'], 'b6c42c59-5839-437d-99d6-9d54db4b824c'):
            third['supersedes'] = supersedes
            self.write(self.event, second, third)
            with self.subTest(supersedes=supersedes), self.assertRaises(ValueError):
                load_reviews(self.path, self.rows)
        second['analytical_scope'] = 'another scope'
        self.write(self.event, second)
        with self.assertRaisesRegex(ValueError, 'analytical_scope'):
            load_reviews(self.path, self.rows)
        self.write(self.event, self.event)
        with self.assertRaisesRegex(ValueError, 'duplicate decision_id'):
            load_reviews(self.path, self.rows)

    def test_cross_identity_supersession_rejected(self):
        other = copy.deepcopy(self.event)
        other.update(decision_id='43541d2a-d1c7-4b45-ae0f-9cc0f7a14788', policy_action_id='md-other', supersedes=self.event['decision_id'])
        self.rows.append(dict(self.rows[0], policy_action_id='md-other'))
        self.write(self.event, other)
        with self.assertRaisesRegex(ValueError, 'cross-identity'):
            load_reviews(self.path, self.rows)

    def test_reviewed_title_correction_can_supersede_historical_guard(self):
        second = copy.deepcopy(self.event)
        second.update(decision_id='43541d2a-d1c7-4b45-ae0f-9cc0f7a14788',
                      supersedes=self.event['decision_id'])
        second['record_identity_guard']['bill'] = 'HB 1 (corrected title)'
        self.rows[0]['bill'] = second['record_identity_guard']['bill']
        self.write(self.event, second)
        original = self.path.read_bytes()
        self.assertEqual(load_reviews(self.path, self.rows)['md-example-2026'], second)
        self.assertEqual(self.path.read_bytes(), original)

    def test_evidence_and_required_metadata(self):
        mutations = [({'source_evidence': []}), ({'source_evidence': [{'url': 'https://example.org'}]}),
                     ({'source_evidence': [dict(url=' ', body_sha256='b'*64, locator='x')]}),
                     ({'source_evidence': [dict(url='https://example.org', body_sha256='bad', locator='x')]}),
                     ({'source_evidence': [dict(url='https://example.org', body_sha256='b'*64, locator=' ')]}),
                     ({'reviewer': ' '}), ({'rationale': ''}), ({'analytical_scope': ''}),
                     ({'reviewed_at': '2026-11-07T12:00:00'}), ({'reviewed_record_sha256': 'z'*64}),
                     ({'decision_id': 'not-a-uuid'}), ({'extra': 'unknown'})]
        for mutation in mutations:
            event = dict(self.event, **mutation)
            self.write(event)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                load_reviews(self.path, self.rows)

    def test_jsonl_integrity(self):
        for raw in (b'{bad}\n', b'{}', b'{"x":1,"x":2}\n', b'\xff\n', b'\n'):
            self.path.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_reviews(self.path, self.rows)

    def test_main_reports_registry_errors(self):
        (self.path.parent / 'state_policy_scope_reviews.jsonl').write_text('{bad}\n')
        inv = self.path.parent / 'inv.csv'
        leg = self.path.parent / 'leg.csv'
        stats = self.path.parent / 'stats.json'
        inv.write_text('moratorium_id\n')
        leg.write_text('policy_action_id\n')
        stats.write_text('{}')
        with patch.object(validate_dataset, 'INV', inv), patch.object(validate_dataset, 'LEG', leg), \
             patch.object(validate_dataset, 'STATS', stats), patch.object(validate_dataset, 'check_inventory'), \
             patch.object(validate_dataset, 'check_legislation'), patch.object(validate_dataset, 'check_summary_stats'), \
             patch('legacy_moratorium_identity.load_aliases'), patch.object(sys, 'argv', ['validate_dataset', '--json']):
            import contextlib
            import io
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(validate_dataset.main(), 1)
            self.assertEqual(json.loads(output.getvalue())['errors'][0]['check'], 'policy.scope_registry')


if __name__ == '__main__':
    unittest.main()
