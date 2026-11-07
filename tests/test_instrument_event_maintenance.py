"""Synthetic review transitions; never claims about a real event's validity."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import instrument_event_maintenance as m


def empty():return {'instrument_events':{},'claims':{},'review_decisions':{}}


def decide(rows,target,scope,claims,disposition='accepted',time='2026-11-01T12:00:00Z'):
    candidates=[d for d in rows['review_decisions'].values() if d['target']==target and d['scope']==scope]
    parent=max(candidates,key=lambda d:m.instant(d['decided_at']))['decision_id'] if candidates else None
    key='decision-'+str(len(rows['review_decisions']))
    rows['review_decisions'][key]={'decision_id':key,'target':target,'scope':scope,'claim_ids':claims,
        'disposition':disposition,'supersedes_id':parent,'decided_at':time,
        'reviewer':'synthetic reviewer','method':'synthetic source-review fixture','rationale':'Synthetic reviewed transition, no real legal-force finding.'}
    return rows['review_decisions'][key]


def add_event(rows,key='one',time='2026-11-01T12:00:00Z',validity=True):
    event={'schema_version':'1.0.0','event_id':key,'instrument':{'kind':'moratorium','id':'legacy'},
           'action':'adopted','occurrence':{'earliest':'2026-01-01','latest':'2026-01-01','precision':'day','original_text':'January 1'},
           'observed_at':'2026-10-01T12:00:00Z','published_at':None,'claim_ids':['exact-'+key]}
    rows['instrument_events'][key]=event
    cid='exact-'+key
    rows['claims'][cid]={'claim_id':cid,'subject':m.event_target(key),'predicate':'instrument_event',
                         'value':{f:event[f] for f in ('instrument','action','occurrence')}}
    decide(rows,m.claim_target(cid),'instrument_event',[cid],time=time)
    for field in m.EVENT_FIELDS:
        if event[field] is not None:decide(rows,m.event_target(key),field,[cid],time=time)
    if validity:decide(rows,m.event_target(key),'event_validity',[cid],time=time)
    return event


def withdraw(rows,key='one',time='2026-11-02T12:00:00Z',reject_exact=True):
    cid='basis-'+key+'-'+str(len(rows['claims']))
    rows['claims'][cid]={'claim_id':cid,'subject':m.event_target(key),'predicate':'event_validity',
                         'value':{'disposition':'rejected','basis':'Synthetic evidence shows the original event was incorrectly characterized.'}}
    decide(rows,m.claim_target(cid),'event_validity',[cid],time=time)
    if reject_exact:decide(rows,m.claim_target('exact-'+key),'instrument_event',['exact-'+key],'rejected',time)
    for field in m.EVENT_FIELDS:
        if rows['instrument_events'][key][field] is not None:
            decide(rows,m.event_target(key),field,['exact-'+key],'rejected',time)
    decide(rows,m.event_target(key),'event_validity',[cid],'rejected',time)


def restore(rows,key='one',time='2026-11-03T12:00:00Z'):
    cid='exact-'+key
    decide(rows,m.claim_target(cid),'instrument_event',[cid],time=time)
    for field in m.EVENT_FIELDS:
        if rows['instrument_events'][key][field] is not None:decide(rows,m.event_target(key),field,[cid],time=time)
    decide(rows,m.event_target(key),'event_validity',[cid],time=time)


def correction(rows,old,replacements,time='2026-11-02T12:00:00Z'):
    cid='correction-'+old
    rows['claims'][cid]={'claim_id':cid,'subject':m.event_target(old),'predicate':'event_correction',
                         'value':{'replacement_event_ids':replacements}}
    decide(rows,m.claim_target(cid),'event_correction',[cid],time=time)


class EventMaintenanceTests(unittest.TestCase):
    def setUp(self):self.rows=empty();add_event(self.rows)

    def test_withdrawal_after_claim_rejection_retains_original_and_historical_support(self):
        previous=copy.deepcopy(self.rows);withdraw(self.rows)
        result=m.transition(self.rows,previous)
        self.assertEqual(result['current_events'],[])
        self.assertEqual(result['statuses'][0]['review_state'],'withdrawn')
        self.assertEqual(self.rows['instrument_events'],previous['instrument_events'])
        self.assertTrue(set(previous['claims'])<=set(self.rows['claims']))

    def test_reinstatement_and_second_withdrawal_require_new_support(self):
        previous=copy.deepcopy(self.rows);withdraw(self.rows);m.transition(self.rows,previous)
        withdrawn=copy.deepcopy(self.rows);restore(self.rows);m.transition(self.rows,withdrawn)
        self.assertEqual(len(m.inspect(self.rows)['current_events']),1)
        restored=copy.deepcopy(self.rows);withdraw(self.rows,time='2026-11-04T12:00:00Z');m.transition(self.rows,restored)
        self.assertEqual(m.inspect(self.rows)['current_events'],[])

    def test_missing_validity_and_rejected_claim_alone_do_not_silently_remove_event(self):
        data=copy.deepcopy(self.rows)
        for key,d in list(data['review_decisions'].items()):
            if d['scope']=='event_validity':del data['review_decisions'][key]
        with self.assertRaisesRegex(ValueError,'explicit accepted/rejected'):m.inspect(data)
        decide(self.rows,m.claim_target('exact-one'),'instrument_event',['exact-one'],'rejected','2026-11-02T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'accepted exact'):m.inspect(self.rows)

    def test_dangling_live_field_acceptance_and_unsupported_withdrawal_fail(self):
        withdraw(self.rows);data=copy.deepcopy(self.rows)
        rejected=next(k for k,d in data['review_decisions'].items() if d['scope']=='action' and d['disposition']=='rejected')
        del data['review_decisions'][rejected]
        with self.assertRaisesRegex(ValueError,'rejected field'):m.inspect(data)
        basis=next(c for c in self.rows['claims'].values() if c['predicate']=='event_validity');basis['value']['basis']=' '
        with self.assertRaisesRegex(ValueError,'validity-basis evidence'):m.inspect(self.rows)

    def test_historical_support_cannot_come_from_a_later_acceptance(self):
        withdraw(self.rows)
        first=next(d for d in self.rows['review_decisions'].values() if d['target']==m.claim_target('exact-one') and d['supersedes_id'] is None)
        first['decided_at']='2026-11-01T13:00:00Z'
        with self.assertRaisesRegex(ValueError,'support'):m.inspect(self.rows)

    def test_new_withdrawn_events_and_historical_mutation_cannot_bypass_publication(self):
        withdraw(self.rows)
        with self.assertRaisesRegex(ValueError,'New already-withdrawn'):m.transition(self.rows,empty())
        previous=copy.deepcopy(self.rows);self.rows['instrument_events']['one']['action']='effective'
        # Keep the malformed event from failing exact support before retention check.
        self.rows['claims']['exact-one']['value']['action']='effective'
        with self.assertRaisesRegex(ValueError,'deleted or mutated'):m.transition(self.rows,previous)

    def test_legacy_profile_migration_uses_prior_accepted_baseline_without_fabricated_validity(self):
        legacy=empty();add_event(legacy,validity=False)
        upgraded=copy.deepcopy(legacy);withdraw(upgraded)
        self.assertEqual(m.transition(upgraded,legacy)['statuses'][0]['review_state'],'withdrawn')
        bad=copy.deepcopy(legacy)
        decide(bad,m.claim_target('exact-one'),'instrument_event',['exact-one'],'rejected','2026-11-01T13:00:00Z')
        bad_upgrade=copy.deepcopy(bad);withdraw(bad_upgrade)
        with self.assertRaisesRegex(ValueError,'accepted exact'):m.transition(bad_upgrade,bad)

    def test_one_to_many_correction_preserves_old_and_new_event_ids(self):
        previous=copy.deepcopy(self.rows);add_event(self.rows,'two');add_event(self.rows,'three');withdraw(self.rows)
        correction(self.rows,'one',['two','three'])
        result=m.transition(self.rows,previous)
        self.assertEqual({e['event_id'] for e in result['current_events']},{'two','three'})
        old=next(s for s in result['statuses'] if s['event_id']=='one')
        self.assertEqual(old['replacement_event_ids'],['three','two'])

    def test_wrong_correction_target_self_link_and_future_replacement_acceptance_fail(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two'])
        for values,pattern in [(['one'],'self'),(['missing'],'Missing')]:
            data=copy.deepcopy(self.rows);data['claims']['correction-one']['value']['replacement_event_ids']=values
            with self.assertRaisesRegex(ValueError,pattern):m.inspect(data)
        data=copy.deepcopy(self.rows)
        d=next(d for d in data['review_decisions'].values() if d['target']==m.event_target('two') and d['scope']=='event_validity')
        d['decided_at']='2026-11-03T12:00:00Z'
        with self.assertRaisesRegex(ValueError,'not accepted at correction'):m.inspect(data)

    def test_review_chain_branches_disconnected_roots_and_wrong_scopes_fail(self):
        withdraw(self.rows)
        reject=next(d for d in self.rows['review_decisions'].values() if d['scope']=='action' and d['disposition']=='rejected')
        for change,pattern in [({'decision_id':'extra'},'Branched'),({'decision_id':'extra','supersedes_id':None},'one root'),
                               ({'decision_id':'extra','scope':'other'},'changes target/scope')]:
            data=copy.deepcopy(self.rows);data['review_decisions']['extra']={**reject,**change}
            with self.assertRaisesRegex(ValueError,pattern):m.inspect(data)

    def test_equivalent_timezones_and_same_batch_dependencies_are_supported(self):
        data=copy.deepcopy(self.rows)
        for d in data['review_decisions'].values():d['decided_at']='2026-11-01T07:00:00-05:00'
        self.assertEqual(m.inspect(self.rows)['current_events'],m.inspect(data)['current_events'])
        withdraw(data,time='2026-11-01T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'strictly earlier'):m.inspect(data)

    def test_historical_withdrawal_cannot_borrow_a_later_basis_acceptance(self):
        withdraw(self.rows);restore(self.rows)
        basis=next(d for d in self.rows['review_decisions'].values()
                   if d['target']['table']=='claims' and d['scope']=='event_validity')
        basis['decided_at']='2026-11-02T13:00:00Z'
        with self.assertRaisesRegex(ValueError,'basis at review time'):m.inspect(self.rows)

    def test_correction_cannot_precede_original_withdrawal(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two'],time='2026-11-01T13:00:00Z')
        with self.assertRaisesRegex(ValueError,'Original was not withdrawn at correction'):m.inspect(self.rows)

    def test_correction_cycles_fail_after_individually_supported_historical_transitions(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two'])
        restore(self.rows,time='2026-11-03T12:00:00Z')
        withdraw(self.rows,'two',time='2026-11-04T12:00:00Z')
        correction(self.rows,'two',['one'],time='2026-11-04T12:00:00Z')
        withdraw(self.rows,time='2026-11-05T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'Cyclic event corrections'):m.inspect(self.rows)

    def test_reinstating_corrected_original_requires_retiring_current_correction_claim(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two']);restore(self.rows)
        with self.assertRaisesRegex(ValueError,'requires withdrawn original'):m.inspect(self.rows)
        decide(self.rows,m.claim_target('correction-one'),'event_correction',['correction-one'],'rejected','2026-11-03T12:00:00Z')
        self.assertEqual({e['event_id'] for e in m.inspect(self.rows)['current_events']},{'one','two'})

    def test_new_current_event_cannot_include_a_prepublication_withdrawal(self):
        withdraw(self.rows);restore(self.rows)
        with self.assertRaisesRegex(ValueError,'pre-publication withdrawal'):m.transition(self.rows,empty())

    def test_intermediate_acceptance_while_withdrawn_is_not_hidden_by_later_rejection(self):
        withdraw(self.rows)
        decide(self.rows,m.claim_target('exact-one'),'instrument_event',['exact-one'],time='2026-11-02T13:00:00Z')
        decide(self.rows,m.event_target('one'),'action',['exact-one'],time='2026-11-02T13:00:00Z')
        decide(self.rows,m.event_target('one'),'action',['exact-one'],'rejected','2026-11-02T14:00:00Z')
        with self.assertRaisesRegex(ValueError,'intermediate field acceptance'):m.inspect(self.rows)

    def test_support_lapse_between_validity_transitions_cannot_be_hidden_by_reacceptance(self):
        decide(self.rows,m.claim_target('exact-one'),'instrument_event',['exact-one'],'rejected','2026-11-02T12:00:00Z')
        decide(self.rows,m.claim_target('exact-one'),'instrument_event',['exact-one'],time='2026-11-03T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'accepted exact'):m.inspect(self.rows)

    def test_superseded_factual_field_requires_exact_support_at_its_own_time(self):
        self.rows['claims']['other']={'claim_id':'other','subject':m.event_target('one'),'predicate':'other','value':'A nearby source fact'}
        decide(self.rows,m.claim_target('other'),'other',['other'],time='2026-11-02T12:00:00Z')
        decide(self.rows,m.event_target('one'),'action',['other'],time='2026-11-02T12:00:00Z')
        decide(self.rows,m.event_target('one'),'action',['exact-one'],time='2026-11-03T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'own review time'):m.inspect(self.rows)

    def test_canonical_retention_distinguishes_boolean_and_numeric_values(self):
        self.rows['claims']['unreviewed']={'claim_id':'unreviewed','subject':m.event_target('one'),'predicate':'other','value':1}
        previous=copy.deepcopy(self.rows);self.rows['claims']['unreviewed']['value']=True
        self.assertEqual(previous['claims']['unreviewed'],self.rows['claims']['unreviewed'])  # Python equality is insufficient.
        with self.assertRaisesRegex(ValueError,'Historical claims deleted or mutated'):m.transition(self.rows,previous)

    def test_correction_claim_acceptance_requires_its_own_source_evidence(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two'])
        key=next(k for k,d in self.rows['review_decisions'].items() if d['target']==m.claim_target('correction-one'))
        for refs in [[],['missing'],['exact-one']]:
            data=copy.deepcopy(self.rows);data['review_decisions'][key]['claim_ids']=refs
            with self.assertRaisesRegex(ValueError,'exact source claim'):m.inspect(data)

    def test_retracting_correction_does_not_hide_unsupported_historical_acceptance(self):
        add_event(self.rows,'two');withdraw(self.rows);correction(self.rows,'one',['two'])
        acceptance=next(d for d in self.rows['review_decisions'].values() if d['target']==m.claim_target('correction-one'))
        acceptance['claim_ids']=[]
        decide(self.rows,m.claim_target('correction-one'),'event_correction',['correction-one'],'rejected','2026-11-03T12:00:00Z')
        with self.assertRaisesRegex(ValueError,'exact source claim'):m.inspect(self.rows)
