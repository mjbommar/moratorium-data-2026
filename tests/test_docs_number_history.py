"""Fixing newest-entry numbers must preserve the changelog title and older history."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('numbers',Path(__file__).resolve().parents[1]/'scripts/check_docs_numbers.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class HistoryTests(unittest.TestCase):
    def test_expanded_counts_separate_lifecycles_and_current_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            measures = [{'lifecycle': status} for status in ('voted', 'scheduled', 'litigated', 'unknown')]
            results = [{'result_observation_id':'old', 'supersedes_id':None, 'certification_status':'certified'},
                       {'result_observation_id':'new', 'supersedes_id':'old', 'certification_status':'amended_certification'},
                       {'result_observation_id':'part', 'supersedes_id':None, 'certification_status':'unofficial'}]
            for table, rows in [('ballot_measures', measures), ('measure_results', results)]:
                (root / (table + '.jsonl')).write_text(''.join(json.dumps(row) + '\n' for row in rows))
            facts = mod.expanded_facts(root)
            self.assertEqual(facts, {'expanded_records':4, 'expanded_voted':1, 'expanded_scheduled':1,
                                     'expanded_litigated':1, 'expanded_unknown':1,
                                     'expanded_current_results':2, 'expanded_certified_results':1})

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
