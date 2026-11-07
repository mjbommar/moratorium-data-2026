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
    def test_proposal_link_keeps_unknown_force_and_dates_separate(self):
        unknown={'earliest':None,'latest':None,'precision':'unknown','original_text':None}
        self.rows['local_restrictions']['r']={'restriction_id':'r','title':'Proposed prohibition',
            'status':'unknown','adoption':unknown,'effective':unknown}
        self.rows['measure_instrument_links']['l']={'link_id':'l','measure_id':self.result['measure_id'],
            'instrument':{'kind':'restriction','id':'r'},'relation':'proposes',
            'review_status':'accepted','claim_ids':[]}
        text=render(self.rows,SNAPSHOT)
        self.assertIn('## Linked restriction records',text)
        self.assertIn('proposes | accepted | Proposed prohibition | unknown | unknown | unknown',text)
        self.assertIn('2 reviewed measure records',text)
        self.assertIn('does not establish enactment or current force',text)

    def test_scheduled_measure_is_listed_without_creating_a_result(self):
        measure=copy.deepcopy(self.rows['ballot_measures'][self.result['measure_id']])
        measure.update(measure_id='future-measure',election_id='future-election',
                       designation='Future ordinance',lifecycle='scheduled')
        election=copy.deepcopy(self.rows['elections'][self.rows['ballot_measures'][self.result['measure_id']]['election_id']])
        election.update(election_id='future-election',election_date=dict(
            earliest='2026-12-15',latest='2026-12-15',precision='day',original_text='December15'))
        self.rows['ballot_measures']['future-measure']=measure
        self.rows['elections']['future-election']=election
        text=render(self.rows,SNAPSHOT)
        self.assertIn('3 reviewed measure records · 2 current result observations',text)
        self.assertIn('1 reviewed measure has no current result observation',text)
        self.assertIn('Future ordinance | 2026-12-15 | scheduled |',text)
        self.assertNotIn('2026-12-15 | scheduled | 0',text)
        self.assertEqual(len(self.rows['measure_results']),3)

    def test_refused_placement_is_visible_without_inventing_a_vote(self):
        measure = copy.deepcopy(self.rows['ballot_measures'][self.result['measure_id']])
        measure.update(measure_id='refused-placement', designation='Separate proposed initiative',
                       lifecycle='disqualified')
        self.rows['ballot_measures'][measure['measure_id']] = measure
        before = copy.deepcopy(self.rows['measure_results'])
        text = render(self.rows, SNAPSHOT)
        self.assertIn('1 disqualified; 2 voted', text)
        self.assertIn('3 reviewed measure records · 2 current result observations', text)
        self.assertIn('Election date (held or intended)', text)
        self.assertIn('Separate proposed initiative', text)
        self.assertIn('disqualified |', text)
        self.assertEqual(self.rows['measure_results'], before)

    def test_named_county_parts_remain_visible_and_are_never_summed(self):
        self.result.update(yes_votes=106, no_votes=899,
                           reporting_scope={'kind':'jurisdiction_part','description':'Brown County portion'})
        other=copy.deepcopy(self.result)
        other.update(result_observation_id='outagamie-part', yes_votes=45, no_votes=134,
                     reporting_scope={'kind':'jurisdiction_part','description':'Outagamie County portion'})
        self.rows['measure_results'][other['result_observation_id']]=other
        text=render(self.rows,SNAPSHOT)
        self.assertIn('Partial jurisdiction: Brown County portion',text)
        self.assertIn('Partial jurisdiction: Outagamie County portion',text)
        self.assertIn('106 | 899',text)
        self.assertIn('45 | 134',text)
        self.assertNotIn('151 | 1033',text)
        self.assertIn('scope not recorded',text)
        self.assertIn('3 current result observations',text)

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

    def test_advisory_permission_direction_is_visible_next_to_counts(self):
        measure=self.rows['ballot_measures'][self.result['measure_id']]
        measure.update(bindingness='advisory',yes_direction='facilitates')
        text=render(self.rows,SNAPSHOT)
        self.assertIn('| Bindingness | Yes-vote direction |',text)
        self.assertIn('| advisory | facilitates | 1565 | 791 |',text)
        self.assertIn('do not by themselves enact a restriction or authorize a project',text)

    def test_certification_does_not_resolve_measure_bindingness(self):
        self.rows['ballot_measures'][self.result['measure_id']]['bindingness']='unresolved'
        self.result.update(certification_status='certified',certification_date='2026-11-04')
        text=render(self.rows,SNAPSHOT)
        row=next(line for line in text.splitlines() if line.startswith('| [Sabattus'))
        self.assertIn('| unresolved |',row)
        self.assertIn('| certified 2026-11-04 |',row)

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

    def test_durable_citation_is_displayed_without_replacing_acquisition_url(self):
        source=self.rows['source_documents'][self.result['source_document_id']]
        original=source['url'];source['citation_url']='https://example.gov/durable-post'
        self.assertIn('](<https://example.gov/durable-post>)',render(self.rows,SNAPSHOT))
        self.assertEqual(source['url'],original)

    def accounting_claim(self,result_id):
        source=copy.deepcopy(self.rows['source_documents'][self.result['source_document_id']])
        source.update(source_document_id='accounting-source',url='https://example.gov/accounting-review')
        self.rows['source_documents'][source['source_document_id']]=source
        self.rows['claims']['accounting-review']=dict(claim_id='accounting-review',
            subject={'table':'measure_results','id':result_id},predicate='derived_accounting_discrepancy',
            source_document_id=source['source_document_id'],value={'unreconciled_ballots':5,
            'formula':'18601 - (3800 + 14207 + 32 + 557) = 5',
            'classification':'Not assigned to blank or other votes'})

    def test_reviewed_accounting_note_uses_claim_source_without_changing_counts(self):
        before=copy.deepcopy(self.result)
        self.accounting_claim(self.result['result_observation_id'])
        text=render(self.rows,SNAPSHOT)
        self.assertIn('](<https://example.gov/accounting-review>): source accounting difference 5',text)
        self.assertIn('18601 - (3800 + 14207 + 32 + 557) = 5',text)
        self.assertIn('Not assigned to blank or other votes',text)
        self.assertEqual(self.result,before)

    def test_superseded_result_accounting_note_is_not_presented_as_current(self):
        retired=next(r for r in self.rows['measure_results'].values()
                     if r['result_observation_id'] in {v['supersedes_id'] for v in self.rows['measure_results'].values()})
        self.accounting_claim(retired['result_observation_id'])
        self.assertNotIn('source accounting difference',render(self.rows,SNAPSHOT))

    def test_ballot_difference_without_reviewed_claim_does_not_generate_a_note(self):
        self.result['ballots_cast']=9999
        self.assertNotIn('source accounting difference',render(self.rows,SNAPSHOT))

if __name__=='__main__':unittest.main()
