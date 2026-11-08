import csv
import json
from pathlib import Path
import shutil
import subprocess
import contextlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_policy_scope_exports as exports
import build_summary_stats as stats
import verify_release_candidate as verifier
import build_release_candidate as release


class RestoredScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'data').mkdir()
        for name in ('build_policy_scope_exports.py', 'policy_scope_reviews.py', 'build_summary_stats.py'):
            shutil.copyfile(ROOT / 'scripts' / name, self.root / 'scripts' / name)
        self.raw = self.root / 'data/state_legislation.csv'
        self.raw.write_text('policy_action_id,state,state_abbrev,activity_level,policy_instrument_type,bill\na,Maryland,MD,Low,bill,HB1\n')
        (self.root / 'data/moratorium_inventory.csv').write_text('state,activity_level,state_abbrev,enacted_status\n')
        self.registry = self.root / 'data/state_policy_scope_reviews.jsonl'
        self.registry.write_text('')
        self.output = self.root / 'data/policy-scope'
        self.refresh()

    def refresh(self):
        exports.sync(exports.render(self.raw, self.registry), self.output, boundary=self.root)
        with patch.multiple(stats, INV=self.root/'data/moratorium_inventory.csv', LEG=self.raw,
                            STATS=self.root/'data/summary_stats.json', SCOPE_REGISTRY=self.registry,
                            SWEEP=self.root/'data/sweep_coverage.json', STATES_DIR=self.root/'states'):
            (self.root/'data/summary_stats.json').write_text(json.dumps(stats.build()))

    def test_real_restored_check_and_drift(self):
        self.assertEqual(verifier.verify_policy_scope(self.root)['status'], 'verified')
        for path, replacement in [(self.raw, self.raw.read_text().replace('HB1', 'HB2')),
                                  (self.registry, '\n'),
                                  (self.output/exports.ALL, 'changed'),
                                  (self.output/exports.RECEIPT, '{}')]:
            before = path.read_bytes()
            path.write_text(replacement)
            with self.subTest(path=path), self.assertRaises(ValueError):
                verifier.verify_policy_scope(self.root)
            path.write_bytes(before)
        summary = self.root/'data/summary_stats.json'
        data = json.loads(summary.read_text())
        data['policy_scope_review']['raw_observation_count'] = 9
        summary.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'summary is stale'):
            verifier.verify_policy_scope(self.root)

    def test_registry_change_with_fresh_exports_but_stale_summary(self):
        event = dict(schema_version='1.0.0', decision_id='f59ba12f-5a11-4875-901a-6dd7b3c6c7a0',
                     policy_action_id='a', decision='exclude',
                     analytical_scope='data-center infrastructure policy analytical census',
                     record_identity_guard=dict(state_abbrev='MD', bill='HB1', policy_instrument_type='bill'),
                     reviewed_record_sha256='a'*64, reviewer='reviewer', reviewed_at='2026-11-07T12:00:00Z',
                     rationale='reason', source_evidence=[dict(url='https://example.org', body_sha256='b'*64, locator='page')], supersedes=None)
        self.registry.write_text(json.dumps(event) + '\n')
        exports.sync(exports.render(self.raw, self.registry), self.output, boundary=self.root)
        with self.assertRaisesRegex(ValueError, 'summary is stale'):
            verifier.verify_policy_scope(self.root)
        self.refresh()
        self.assertEqual(verifier.verify_policy_scope(self.root)['status'], 'verified')

    def test_candidate_checks_selected_bytes_before_writing(self):
        shutil.copyfile(ROOT/'scripts/verify_release_candidate.py', self.root/'scripts/verify_release_candidate.py')
        names = [str(p.relative_to(self.root)) for p in self.root.rglob('*') if p.is_file()]
        committed = {name: (self.root/name).read_bytes() for name in names}
        committed['paper/moratorium-nation-2026-04-30.pdf'] = b'paper'
        def git(*args):
            if args[0] == 'rev-parse': return b'abc\n'
            if args[0] == 'ls-tree': return ('\n'.join(names) + '\n').encode()
            if args[0] == 'show': return committed[args[1].split(':', 1)[1]]
            raise AssertionError(args)
        destination = self.root/'candidate'
        # Dirty restored inputs are irrelevant; build consumes only simulated committed bytes.
        self.raw.write_text('dirty worktree')
        with patch.object(release, 'git', side_effect=git), patch.object(release, 'select_files', return_value=names), contextlib.redirect_stdout(io.StringIO()):
            release.build(destination, 'HEAD')
            for name in ('data/state_legislation.csv', 'data/state_policy_scope_reviews.jsonl',
                         'data/policy-scope/all-annotated.csv', 'data/policy-scope/receipt.json',
                         'data/summary_stats.json'):
                original = committed[name]
                committed[name] = original + b'\n'
                # Whitespace after JSON is semantically harmless, so make summary stale explicitly.
                if name.endswith('summary_stats.json'):
                    summary = json.loads(original); summary['policy_scope_review'] = {}
                    committed[name] = json.dumps(summary).encode()
                target = self.root/('bad-' + Path(name).name)
                with self.subTest(name=name), self.assertRaises(subprocess.CalledProcessError): release.build(target, 'HEAD')
                self.assertFalse(target.exists())
                committed[name] = original

    def test_missing_and_extra_outputs(self):
        path = self.output/exports.INCLUDED
        old = path.read_bytes(); path.unlink()
        with self.assertRaises(ValueError): verifier.verify_policy_scope(self.root)
        path.write_bytes(old)
        (self.output/'extra').write_text('x')
        with self.assertRaises(ValueError): verifier.verify_policy_scope(self.root)

    def test_historical_and_cached_module_isolation(self):
        self.assertEqual(verifier.verify_policy_scope(self.root)['status'], 'verified')
        # A deliberately poisoned cached exporter must not be used.
        with patch.dict(sys.modules, {'build_policy_scope_exports': object()}):
            self.assertEqual(verifier.verify_policy_scope(self.root)['status'], 'verified')
        (self.root/'scripts/build_policy_scope_exports.py').unlink()
        self.assertEqual(verifier.verify_policy_scope(self.root)['status'], 'not_present')


if __name__ == '__main__': unittest.main()
