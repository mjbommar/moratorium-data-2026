import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_pilot_contracts import ROOT, audit, sha

MANIFEST=ROOT/'work/research/2026-11-06/pilot-contract-review/manifest.json'


class PilotContractReviewTests(unittest.TestCase):
    def edited(self, edit):
        original=json.loads(MANIFEST.read_text());edit(original)
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        path=Path(temp.name)/'manifest.json';path.write_text(json.dumps(original));return path

    def test_all_frozen_cases_and_unknowns_verify_without_rewriting_data(self):
        inputs=[ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv',MANIFEST]
        before={str(p):sha(p) for p in inputs};result=audit(MANIFEST)
        self.assertEqual(len(result['cases']),17)
        self.assertEqual(result['selected_canonical_measures'],12)
        self.assertEqual(result['selected_measure_months'],{'2026-11':11,'2026-03':1})
        self.assertEqual(result['case_kind_counts']['synthetic_schema_example'],5)
        self.assertEqual(before,{str(p):sha(p) for p in inputs})

    def test_omitted_named_case_cannot_silently_pass(self):
        path=self.edited(lambda d:d['cases'].pop())
        with self.assertRaisesRegex(ValueError,'Incomplete/duplicate'):audit(path)

    def test_factual_expectation_conflict_is_not_accepted_as_schema_success(self):
        def edit(data):
            case=next(c for c in data['cases'] if c['case_id']=='bloomington')
            case['assertions'][0]['equals']='binding'
        with self.assertRaisesRegex(ValueError,'Case expectation differs: bloomington'):
            audit(self.edited(edit))

    def test_source_review_receipt_drift_requires_reconciliation(self):
        def edit(data):
            case=next(c for c in data['cases'] if c['case_id']=='bloomington')
            case['evidence_files'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Review evidence drift'):
            audit(self.edited(edit))
