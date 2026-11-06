import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('expanded_data', ROOT / 'scripts/expanded_data.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
FIXTURE = ROOT / 'work/schemas/expanded/fixtures/synthetic'

def date(s=None): return {'earliest':s,'latest':s,'precision':'day' if s else 'unknown','original_text':s}

class ExpandedContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.tables = {p.stem: [json.loads(s) for s in p.read_text().splitlines()] for p in FIXTURE.glob('*.jsonl')}
    def validate(self):
        for name, records in self.tables.items():
            (self.path / (name + '.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in records))
        return mod.validate(self.path)[0]
    def restriction(self):
        return {'schema_version':'1.0.0','restriction_id':'r','jurisdiction_id':'synthetic-town','title':None,'status':'proposed','provisions':[],'adoption':date(),'effective':date(),'applicability_start':date(),'retroactivity_explanation':None,'end':date(),'duration_original':None,'claim_ids':[]}
    def claim(self,subject,predicate):
        return {'schema_version':'1.0.0','claim_id':'c','subject':subject,'predicate':predicate,'value':'synthetic','source_document_id':'synthetic-source','quote':'Synthetic quote','span':None,'temporal_support':date(),'extraction_provenance':'synthetic'}
    def test_enactment_term_preserves_unknown_date(self):
        # A six-month enactment term must not acquire an election/retroactivity date.
        provision = {'schema_version': '1.0.0', 'provision_id': 'p',
            'measure_id': 'synthetic-question', 'mechanism': 'temporary_permitting_pause',
            'bindingness': 'unresolved', 'covered_uses': [], 'thresholds': [],
            'exemptions': [], 'geography': None, 'implementation_requirements': None,
            'claim_ids': []}
        self.tables['measure_provisions'] = [provision]
        provision['duration'] = {'value': 6, 'unit': 'calendar_months',
            'anchor': 'enactment', 'anchor_date': None,
            'original_text': 'six (6) months following its enactment'}
        self.assertEqual(self.validate(), [])
        self.assertIsNone(provision['duration']['anchor_date'])

    def source_categories(self):
        r=self.tables['measure_results'][0]
        r.update(valid_votes=None,ballots_cast=None,source_yes_percent=None,
                 percentage_denominator='unknown',calculated_outcome='unknown',
                 reported_outcome='unknown',outcome_direction='unresolved')
        self.tables['claims']=[]
        for field,predicate,value in [
            ('source_vote_categories','source_vote_category',{'label':'VOIDS','count':24}),
            ('source_vote_totals','source_vote_total',{'label':'circled total','count':124,'scope':'question row'})]:
            c=self.claim({'table':'measure_results','id':r['result_observation_id']},predicate)
            c.update(claim_id=predicate,value=value)
            self.tables['claims'].append(c)
            r[field]=[{**value,'claim_ids':[c['claim_id']]}]
        return r

    def test_unmapped_categories_do_not_infer_denominators(self):
        r=self.source_categories()
        self.assertEqual(self.validate(),[])
        self.assertIsNone(r['ballots_cast'])
        self.assertIsNone(r.get('blank_votes'))
        self.assertIsNone(r['valid_votes'])

    def test_source_category_claim_must_match_value_target_and_source(self):
        self.source_categories();c=self.tables['claims'][0]
        for field,bad in [('value',{'label':'VOIDS','count':25}),
                          ('subject',{'table':'ballot_measures','id':'synthetic-question'}),
                          ('source_document_id','different-source')]:
            original=c[field];c[field]=bad
            self.assertTrue(any('must match exact result' in e for e in self.validate()))
            c[field]=original
        c['predicate']='blank_votes'
        self.assertTrue(any('must match exact result' in e for e in self.validate()))

    def test_source_category_requires_existing_claim(self):
        r=self.source_categories();r['source_vote_categories'][0]['claim_ids']=['absent']
        self.assertTrue(any('unknown claims reference' in e for e in self.validate()))

    def test_duplicate_source_label_and_forced_mapping_rejected(self):
        r=self.source_categories()
        r['source_vote_categories'].append({**r['source_vote_categories'][0],'count':25})
        self.assertTrue(any('duplicate source_vote_categories' in e for e in self.validate()))
        r['source_vote_categories'].pop()
        r['source_vote_categories'][0]['mapped_as']='blank_votes'
        self.assertTrue(self.validate())

    def test_negative_source_count_and_blank_scope_rejected(self):
        r=self.source_categories();r['source_vote_categories'][0]['count']=-1
        self.assertTrue(self.validate())
        r['source_vote_categories'][0]['count']=24
        r['source_vote_totals'][0]['scope']=' '
        self.assertTrue(any('nonblank' in e for e in self.validate()))

    def test_fixture_and_reverse_polarity(self):
        self.assertEqual(self.validate(), [])
        self.tables['measure_results'][0]['outcome_direction'] = 'facilitates'
        self.assertTrue(any('direction' in e for e in self.validate()))
    def test_reported_direction_requires_scoped_outcome_evidence(self):
        r=self.tables['measure_results'][0]
        r.update(yes_votes=None,calculated_outcome='unknown',reported_outcome='defeated',
                 source_yes_percent=None,outcome_direction='restricts',outcome_direction_basis='reported')
        self.assertTrue(any('outcome claim' in e for e in self.validate()))
        c=self.claim({'table':'measure_results','id':r['result_observation_id']},'reported_outcome')
        c['value']='defeated';self.tables['claims']=[c]
        r['value_methods']={'reported_outcome':{'method':'source_reported','claim_ids':['c'],'note':None}}
        self.assertEqual(self.validate(),[])
        r['outcome_direction']='facilitates'
        self.assertTrue(any('direction' in e for e in self.validate()))
        r['outcome_direction']='restricts';c['value']='approved'
        self.assertTrue(any('outcome claim' in e for e in self.validate()))
        r.update(yes_votes=40,reported_outcome='approved',outcome_direction='facilitates')
        self.assertTrue(any('reported outcome contradicts' in e for e in self.validate()))
    def test_uncertified_complete_count_is_not_certification(self):
        r=self.tables['measure_results'][0]
        self.assertEqual(r['certification_status'], 'unofficial'); self.assertEqual(self.validate(), [])
        _, rows = mod.validate(self.path)
        self.assertEqual(mod.certified_result_count(rows), 0)
        r['certification_status']='certified'
        self.assertTrue(any('certification date' in e for e in self.validate()))
        r['certification_date']='2026-11-04'; self.assertEqual(self.validate(), [])
        _, rows = mod.validate(self.path)
        self.assertEqual(mod.certified_result_count(rows), 1)
    def test_inconsistent_totals_and_stale_revision(self):
        r=self.tables['measure_results'][0]; r['valid_votes']=99
        self.assertTrue(any('vote components' in e for e in self.validate()))
        r['valid_votes']=100
        newer=copy.deepcopy(r); newer.update(result_observation_id='new', observed_at='2026-11-03T12:00:00Z', supersedes_id=r['result_observation_id'])
        self.tables['measure_results'].append(newer)
        self.assertTrue(any('not earlier' in e for e in self.validate()))
    def test_same_name_different_governments_are_not_merged(self):
        j=copy.deepcopy(self.tables['jurisdictions'][0]); j.update(jurisdiction_id='synthetic-city',government_type='city')
        self.tables['jurisdictions'].append(j); self.assertEqual(self.validate(), [])
        self.tables['ballot_measures'][0]['jurisdiction_id']='synthetic-city'
        self.assertTrue(any('jurisdiction IDs differ' in e for e in self.validate()))
    def test_retroactivity_requires_explanation_and_claim(self):
        r=self.restriction(); r.update(adoption=date('2026-11-03'),effective=date('2026-11-03'),applicability_start=date('2026-06-16'),duration_original='180 days from applicability')
        self.tables['local_restrictions']=[r]
        self.assertTrue(any('retroactive' in e for e in self.validate()))
        r.update(retroactivity_explanation='Express retroactivity in synthetic text',claim_ids=['c'])
        self.tables['claims']=[self.claim({'table':'local_restrictions','id':'r'},'applicability_start')]
        self.assertEqual(self.validate(), [])
    def test_advisory_cannot_enact_even_with_scoped_review(self):
        self.tables['local_restrictions']=[self.restriction()]
        self.tables['measure_instrument_links']=[{'schema_version':'1.0.0','link_id':'l','measure_id':'synthetic-question','instrument':{'kind':'restriction','id':'r'},'relation':'enacts','provision_ids':[],'claim_ids':['c'],'review_status':'accepted'}]
        self.tables['claims']=[self.claim({'table':'measure_instrument_links','id':'l'},'relation')]
        base={'schema_version':'1.0.0','disposition':'accepted','claim_ids':['c'],'reviewer':'synthetic','method':'manual','rationale':'synthetic','decided_at':'2026-11-04T13:00:00Z','supersedes_id':None}
        self.tables['review_decisions']=[dict(base,decision_id='d1',target={'table':'claims','id':'c'},scope='relation'),dict(base,decision_id='d2',target={'table':'measure_instrument_links','id':'l'},scope='enacts')]
        self.assertTrue(any('advisory measure' in e for e in self.validate()))
        self.tables['ballot_measures'][0]['bindingness']='binding'; self.assertEqual(self.validate(), [])
        self.tables['review_decisions'][0]['scope']='wrong'
        self.assertTrue(any('scope' in e or 'scoped acceptance' in e for e in self.validate()))
    def test_missing_votes_do_not_become_zero(self):
        r=self.tables['measure_results'][0]; r.update(yes_votes=None,calculated_outcome='unknown',outcome_direction='unresolved',source_yes_percent=None)
        self.assertEqual(self.validate(), [])
        r['calculated_outcome']='defeated'
        self.assertTrue(any('calculated outcome' in e for e in self.validate()))
    def test_duplicate_ids_and_missing_foreign_key(self):
        self.tables['jurisdictions'].append(copy.deepcopy(self.tables['jurisdictions'][0]))
        self.tables['elections'][0]['jurisdiction_id']='missing'
        errors=self.validate()
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('unknown jurisdictions reference' in e for e in errors))
    def test_superseded_certification_not_counted(self):
        old=self.tables['measure_results'][0]
        old.update(certification_status='certified', certification_date='2026-11-04')
        new=copy.deepcopy(old)
        new.update(result_observation_id='new',observed_at='2026-11-05T12:00:00Z',
                   certification_status='recount_pending',supersedes_id=old['result_observation_id'])
        self.tables['measure_results'].append(new)
        self.assertEqual(self.validate(), [])
        _, rows=mod.validate(self.path)
        self.assertEqual(mod.certified_result_count(rows), 0)

if __name__ == '__main__': unittest.main()
