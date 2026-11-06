"""Published summaries retain observation grain, nulls and supersession semantics."""
import copy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from expanded_data import validate
from build_ballot_summary import render

SNAPSHOT='7b960c58dd52c2f643647e306616966d4590a652c0b9caf11c108ea2edc3f421'

class BallotSummaryTests(unittest.TestCase):
    def setUp(self):
        errors,self.rows=validate(ROOT/'data/expanded-snapshots'/SNAPSHOT)
        self.assertFalse(errors)
        mid=next(k for k,m in self.rows['ballot_measures'].items() if m['designation']=='Data Center Moratorium')
        self.result=next(r for r in self.rows['measure_results'].values() if r['measure_id']==mid)

    def test_explicit_supersession_excludes_old_row_but_keeps_history_count(self):
        text=render(self.rows,SNAPSHOT)
        self.assertIn('2 current result observations',text)
        self.assertIn('3 result observations are retained',text)
        self.assertEqual(sum(line.startswith('| [Eliot') for line in text.splitlines()),1)
        self.assertIn('1565 | 791 | unknown | unknown',text)

    def test_zero_blank_votes_are_not_rendered_as_unknown(self):
        self.result['blank_votes']=0
        text=render(self.rows,SNAPSHOT)
        self.assertIn('1565 | 791 | 0 | unknown',text)

    def test_independent_live_observations_are_not_collapsed_or_summed(self):
        other=copy.deepcopy(self.result);other.update(result_observation_id='synthetic-independent',yes_votes=1564,no_votes=792,certification_status='unofficial',certification_date=None)
        self.rows['measure_results'][other['result_observation_id']]=other
        text=render(self.rows,SNAPSHOT)
        self.assertIn('3 current result observations',text)
        self.assertEqual(sum(line.startswith('| [Sabattus') for line in text.splitlines()),2)
        self.assertIn('1564 | 792',text)

    def test_source_categories_and_totals_do_not_fill_blank_or_ballot_columns(self):
        self.result['source_vote_categories']=[{'label':'VOIDS','count':24,'claim_ids':['review-stage']}]
        self.result['source_vote_totals']=[{'label':'circled total','count':2380,'scope':'question row','claim_ids':['review-stage']}]
        text=render(self.rows,SNAPSHOT)
        self.assertIn('VOIDS: 24 (unmapped category)',text)
        self.assertIn('circled total: 2380 (question row)',text)
        self.assertIn('1565 | 791 | unknown | unknown',text)

if __name__=='__main__':unittest.main()
