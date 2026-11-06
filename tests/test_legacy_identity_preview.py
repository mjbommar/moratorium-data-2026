import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from preview_legacy_identity import preview, row_hash, sha


class LegacyIdentityPreviewTests(unittest.TestCase):
    def fixture(self):
        raw = b'moratorium_id,enacted_status,jurisdiction\na,active,Twin Town\nb,active,Twin Town\nc,pending,Twin Town\n'
        rows = {i: {'moratorium_id': i, 'enacted_status': 'pending' if i == 'c' else 'active',
                    'jurisdiction': 'Twin Town'} for i in 'abc'}
        def mapping(canonical, alias):
            return dict(canonical_id=canonical, alias_ids=[alias],
                        record_sha256={i: row_hash(rows[i]) for i in (canonical, alias)},
                        evidence=[dict(url='https://example.gov/act', body_sha256='0'*64, locator='Title')],
                        rationale='Explicit identity decision, not a same-name inference')
        plan = dict(schema_version='legacy-identity-preview-1', inventory_sha256=sha(raw),
                    reviewer='reviewer', reviewed_at='2026-11-06T00:00:00Z', merges=[mapping('a', 'b')])
        return raw, plan, mapping

    def test_only_explicit_mapping_affects_projected_counts(self):
        raw, plan, _ = self.fixture()
        result = preview(raw, plan)
        self.assertEqual(result['state'], 'preview_only_not_applied')
        self.assertEqual(result['raw_retained_records'], 3)
        self.assertEqual(result['projected_canonical_records'], 2)
        self.assertEqual(result['projected_aliases'], {'b': 'a'})
        self.assertEqual(result['projected_status_counts'], {'active': 1, 'pending': 1})

    def test_current_input_and_each_reviewed_member_are_pinned(self):
        raw, plan, _ = self.fixture()
        with self.assertRaisesRegex(ValueError, 'Inventory changed'):
            preview(raw.replace(b'Twin', b'Other'), plan)
        plan['merges'][0]['record_sha256']['a'] = '1'*64
        with self.assertRaisesRegex(ValueError, 'fingerprint changed'):
            preview(raw, plan)

    def test_unknown_self_and_duplicate_aliases_fail_closed(self):
        raw, plan, mapping = self.fixture()
        for invalid in ('self', 'unknown', 'duplicate'):
            p = copy.deepcopy(plan)
            if invalid == 'self': p['merges'][0]['alias_ids'] = ['a']
            elif invalid == 'unknown': p['merges'][0]['canonical_id'] = 'missing'
            else: p['merges'].append(mapping('c', 'b'))
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                preview(raw, p)

    def test_explicit_transitive_mapping_resolves_and_cycles_are_rejected(self):
        raw, plan, mapping = self.fixture()
        plan['merges'].append(mapping('b', 'c'))
        self.assertEqual(preview(raw, plan)['projected_aliases'], {'b': 'a', 'c': 'a'})
        plan['merges'] = [mapping('a', 'b'), mapping('b', 'a')]
        with self.assertRaisesRegex(ValueError, 'cycle'):
            preview(raw, plan)
