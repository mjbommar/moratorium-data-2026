import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_ballot_semantics import inspect


class SemanticAuditTests(unittest.TestCase):
    def fixture(self):
        return dict(ballot_measures=[dict(measure_id='m',yes_direction='restricts')],
            measure_provisions=[dict(provision_id='p',measure_id='m',mechanism='advisory_opposition',bindingness='advisory')],
            measure_results=[],claims=[dict(claim_id='c',subject=dict(table='measure_provisions',id='p'),
                predicate='mechanism',value='advisory_opposition')],
            review_decisions=[dict(decision_id='d',target=dict(table='measure_provisions',id='p'),
                scope='mechanism',disposition='accepted',supersedes_id=None,claim_ids=['c'])])

    def test_proposition_axis_not_winning_side(self):
        tables=self.fixture();tables['ballot_measures'][0]['reported_outcome']='defeated'
        self.assertEqual(inspect(tables)['advisory_provisions'][0]['review_flags'],[])
        tables['ballot_measures'][0]['yes_direction']='facilitates'
        self.assertIn('direction_requires_scope_review',inspect(tables)['advisory_provisions'][0]['review_flags'])

    def test_bindingness_claim_is_not_direct_mechanism_support(self):
        tables=self.fixture();tables['claims'][0].update(predicate='classification',value={'bindingness':'advisory'})
        row=inspect(tables)['advisory_provisions'][0]
        self.assertIn('mechanism_claim_value_not_explicit',row['review_flags'])
        self.assertEqual(row['lineage']['cited_claim_ids'],['c'])

    def test_superseded_acceptance_cannot_hide_withheld_field(self):
        tables=self.fixture();later=copy.deepcopy(tables['review_decisions'][0])
        later.update(decision_id='later',supersedes_id='d',disposition='withheld')
        tables['review_decisions'].append(later)
        self.assertFalse(inspect(tables)['advisory_provisions'][0]['lineage']['direct_named_value_present'])

    def test_wrong_subject_claim_cannot_supply_field_value(self):
        tables=self.fixture();tables['claims'][0]['subject']['id']='other'
        self.assertFalse(inspect(tables)['advisory_provisions'][0]['lineage']['direct_named_value_present'])

    def test_supersession_cannot_suppress_another_fields_decision(self):
        tables=self.fixture();later=copy.deepcopy(tables['review_decisions'][0])
        later.update(decision_id='later',scope='bindingness',supersedes_id='d')
        tables['review_decisions'].append(later)
        with self.assertRaisesRegex(ValueError,'target or scope'):inspect(tables)

    def test_conflicting_current_acceptances_are_visible(self):
        tables=self.fixture();later=copy.deepcopy(tables['review_decisions'][0]);later['decision_id']='other'
        tables['review_decisions'].append(later)
        self.assertIn('mechanism_accepted_decision_conflicting',inspect(tables)['advisory_provisions'][0]['review_flags'])
