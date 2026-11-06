import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_search_cohort import audit
from normalize_search_provenance import normalize


class SearchCohortTests(unittest.TestCase):
    def ledger(self, root, name, ident, legacy=False):
        directory = root/name
        directory.mkdir()
        event = dict(attempt_id=ident, kind='exa', state='reserved', reserved_at='2026-11-06T00:00:00Z')
        if not legacy:
            event.update(client_sha256='client', config_sha256='config')
        path = directory/'attempts.private.jsonl'
        path.write_text(json.dumps(event)+'\n')
        return path

    def test_legacy_gaps_are_separate_from_verified_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [self.ledger(root, 'modern', 'a'), self.ledger(root, 'legacy', 'b', True)]
            result = audit(root, paths)
            self.assertEqual(result['summary']['verified_unique_search_attempts'], 1)
            self.assertEqual(result['summary']['requires_review_directories'], 1)
            self.assertEqual(result['summary']['review_reasons'], {'legacy_missing_client_hash': 1})
            self.assertEqual(result['summary']['verified_attempt_totals']['unpriced_attempts'], 1)
            self.assertEqual(result['summary']['verified_priced_subtotal_usd'], '0')

    def test_duplicate_attempts_cannot_inflate_aggregate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [self.ledger(root, 'one', 'a'), self.ledger(root, 'two', 'a')]
            with self.assertRaisesRegex(ValueError, 'multiple cohort ledgers'):
                audit(root, paths)
            with self.assertRaisesRegex(ValueError, 'Duplicate ledger'):
                audit(root, [paths[0], paths[0]])

    def test_paths_outside_explicit_root_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.ledger(root, 'one', 'a')
            with self.assertRaisesRegex(ValueError, 'outside cohort root'):
                audit(root/'other', [path])

    def test_source_change_during_verification_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.ledger(root, 'one', 'a')
            def changing(directory):
                result = normalize(directory)
                path.write_text(path.read_text()+'\n')
                return result
            with patch('audit_search_cohort.normalize', side_effect=changing):
                with self.assertRaisesRegex(ValueError, 'changed during cohort audit'):
                    audit(root, [path])
