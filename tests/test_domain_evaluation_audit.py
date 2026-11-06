import copy
import hashlib
import tempfile
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_domain_evaluation import agreement, matches_gold, verify_frozen_code, verify_support_locations


class DomainEvaluationAuditTests(unittest.TestCase):
    def test_support_audit_rejects_fabricated_or_omitted_locations(self):
        candidate=dict(supporting_passages=[dict(quote='term',role='definition')],
                       supporting_passage_locations=[dict(quote='term',role='definition',exact_quote_spans=[[0,4]])])
        self.assertTrue(verify_support_locations(candidate,'term'))
        with self.assertRaisesRegex(ValueError,'incomplete or changed'):
            verify_support_locations(candidate,'term term')
        candidate['supporting_passage_locations'][0]['exact_quote_spans']=[]
        self.assertFalse(verify_support_locations(candidate,'absent'))
        candidate['supporting_passage_locations']=[]
        with self.assertRaisesRegex(ValueError,'inventory mismatch'):
            verify_support_locations(candidate,'absent')

    def test_historical_audit_uses_exact_executed_bytes_not_changed_live_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); live=root/'extract.py';live.write_text('later development')
            old=b'frozen implementation';expected=hashlib.sha256(old).hexdigest()
            archive=root/'executed-code';archive.mkdir()
            retained=archive/f'{expected}-extract.py';retained.write_bytes(old)
            verify_frozen_code(root,{str(live):expected})
            retained.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'missing or changed'):
                verify_frozen_code(root,{str(live):expected})
            retained.unlink()
            with self.assertRaisesRegex(ValueError,'missing or changed'):
                verify_frozen_code(root,{str(live):expected})

    def candidate(self,field,value,table='measure_results'):
        return dict(target_table=table,target_field=field,value=value,field_schema_errors=[])

    def test_adjacent_contest_count_cannot_satisfy_target_gold(self):
        slot=dict(table='measure_results',field='yes_votes',required=105)
        self.assertTrue(matches_gold(self.candidate('yes_votes',105),slot))
        self.assertFalse(matches_gold(self.candidate('yes_votes',168),slot))
        self.assertFalse(matches_gold(self.candidate('no_votes',105),slot))

    def test_inferred_boolean_is_not_a_numeric_vote(self):
        self.assertFalse(matches_gold(self.candidate('precincts_total',True),
                                      dict(table='measure_results',field='precincts_total',required=1)))

    def test_duration_must_preserve_applicability_anchor_and_date(self):
        slot=dict(table='measure_provisions',field='duration',required=dict(value=180,unit='days',anchor='applicability_date',anchor_date={'earliest':'2026-06-16'}))
        value=copy.deepcopy(slot['required'])
        self.assertTrue(matches_gold(self.candidate('duration',value,'measure_provisions'),slot))
        value['anchor_date']['earliest']='2026-11-03'
        self.assertFalse(matches_gold(self.candidate('duration',value,'measure_provisions'),slot))

    def test_area_number_alone_cannot_hide_missing_basis_or_changed_units(self):
        slot=dict(table='measure_provisions',field='thresholds',required=dict(value=100000,operator='ge',unit='square feet',aggregation_rule='aggregate',measurement_basis_contains='impervious'))
        item=dict(value=100000,operator='ge',unit='sq ft',aggregation_rule='aggregate',measurement_basis='aggregate Data Center Area')
        self.assertFalse(matches_gold(self.candidate('thresholds',[item],'measure_provisions'),slot))
        item['measurement_basis']='Aggregate area including associated impervious surfaces'
        self.assertTrue(matches_gold(self.candidate('thresholds',[item],'measure_provisions'),slot))
        item['unit']='acres'
        self.assertFalse(matches_gold(self.candidate('thresholds',[item],'measure_provisions'),slot))

    def test_omitted_candidates_cannot_inflate_reviewer_agreement(self):
        with self.assertRaisesRegex(ValueError,'populations differ'):
            agreement({'one':'supported','two':'ambiguous'},{'one':'supported'})

    def test_reviewer_agreement_does_not_relabel_ambiguity_as_accuracy(self):
        result=agreement({'a':'supported','b':'ambiguous'},{'a':'supported','b':'unsupported'})
        self.assertEqual(result['observed_agreement'],.5)
        self.assertAlmostEqual(result['cohens_kappa'],1/3)
        self.assertIn('not accuracy',result['scope'])
