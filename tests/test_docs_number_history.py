"""Fixing newest-entry numbers must preserve the changelog title and older history."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('numbers',Path(__file__).resolve().parents[1]/'scripts/check_docs_numbers.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class HistoryTests(unittest.TestCase):
    def test_fixed_percentage_passes_followup_check(self):
        facts={k:0 for k in ('rows','in_force','pending','past','states','verify_rows','geocoded','bills','bills_typed','bills_enacted')}
        facts['geocoded_percent']=99.8
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'README.md';path.write_text('Coverage: 99.6%\n')
            with patch.object(mod,'REPO',root),patch.object(mod,'CLAIMS',[('README.md',r'Coverage: ([\d.]+)%','geocoded_percent','coverage')]),patch.object(mod,'facts',return_value=facts),contextlib.redirect_stdout(io.StringIO()):
                with patch.object(sys,'argv',['check','--fix']):self.assertEqual(mod.main(),0)
                with patch.object(sys,'argv',['check']):self.assertEqual(mod.main(),0)
            self.assertEqual(path.read_text(),'Coverage: 99.8%\n')

    def test_only_newest_capture_changes(self):
        prefix='# Changelog\n\nIntroductory provenance.\n\n'
        newest='## New snapshot\n\nTotal: 5\n\n'
        historical='## Old snapshot\n\nTotal: 5\n\nHistorical explanation stays exact.\n'
        facts={k:0 for k in ('rows','in_force','pending','past','states','verify_rows','geocoded','bills','bills_typed','bills_enacted')}
        facts['rows']=6
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'CHANGELOG.md';path.write_text(prefix+newest+historical)
            with patch.object(mod,'REPO',root),patch.object(mod,'CLAIMS',[('CHANGELOG.md',r'Total: (\d+)','rows','newest total')]),patch.object(mod,'facts',return_value=facts),patch.object(sys,'argv',['check','--fix']),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mod.main(),0)
            self.assertEqual(path.read_text(),prefix+newest.replace('Total: 5','Total: 6')+historical)


if __name__=='__main__':unittest.main()
