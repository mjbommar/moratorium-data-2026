import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_builder', ROOT / 'scripts/build_release_candidate.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ReleaseSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = builder.git('rev-parse', 'HEAD^{commit}').decode().strip()
        cls.tracked = builder.git('ls-tree', '-r', '--name-only', cls.commit).decode().splitlines()
        cls.selected = set(builder.select_files(cls.commit, cls.tracked))

    def test_current_public_metadata_and_validation_closure(self):
        expected = {
            'work/audit/refresh-field-accounting-2026-11-07.md',
            'work/audit/refresh-field-accounting-2026-11-07.json',
            'work/research/2026-11-07/wilmington-initiative-history/publication-plan.json',
            'work/research/2026-11-07/wilmington-initiative-history/replay.json',
            'work/research/2026-11-07/executive-force-review/source-versions.json',
            'work/research/2026-11-07/state-policy-forms/source-review.json',
            'scripts/validate_dataset.py', 'scripts/build_summary_stats.py',
            'scripts/legacy_moratorium_identity.py', 'scripts/preview_legacy_identity.py',
            'data/sweep_coverage.json', 'states/alabama.md',
            'data/state_policy_scope_reviews.jsonl', 'scripts/policy_scope_reviews.py',
        }
        self.assertTrue(expected <= self.selected, expected - self.selected)
        self.assertTrue(set(builder.PUBLIC_NOV7_METADATA) <= self.selected)
        self.assertTrue(any(p.startswith('data/expanded-snapshots/') for p in self.selected))
        self.assertTrue(any(p.startswith('data/expanded-csv-snapshots/') for p in self.selected))

    def test_private_and_untracked_paths_are_not_selected(self):
        excluded = {
            'work/research/2026-11-07/executive-force-review/quote-proofs.json',
            'work/research/2026-11-07/wilmington-initiative-history/prepare.py',
            'work/research/2026-11-07/state-policy-forms/answers-ak.json',
            'work/research/2026-11-07/state-policy-forms/private-source.json',
        }
        self.assertFalse(excluded & set(builder.select_files(self.commit, self.tracked + list(excluded))))
        # Even an allowlisted name is excluded if absent from the committed tree.
        missing = builder.PUBLIC_NOV7_METADATA[0]
        self.assertNotIn(missing, builder.select_files(self.commit, [n for n in self.tracked if n != missing]))
        self.assertTrue(self.selected <= set(self.tracked))


if __name__ == '__main__':
    unittest.main()
