"""Publication transactions and explicit review gates are distinct from schema acceptance."""
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import expanded_promotion as m
from expanded_identity import Registry


def rows():
    return {table:{} for table in m.IDS}


def make_plan(records, registry, previous=None):
    return {'schema_version':'1.0.0','expected_sha256':previous,
            'registry_sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),
            'snapshot_sha256':m.fingerprint(m.serialized(records)),
            'reviewer':'synthetic reviewer','reviewed_at':'2026-11-05T16:00:00Z',
            'rationale':'Synthetic transaction regression only','record_reviews':[]}


class PublicationTests(unittest.TestCase):
    def test_event_exact_claim_must_be_accepted_and_cited_by_event_fields(self):
        data=rows();target={'table':'instrument_events','id':'event'}
        event=dict(schema_version='1.0.0',event_id='event',instrument={'kind':'moratorium','id':'legacy'},
            action='adopted',occurrence={'earliest':'2026-02-03','latest':'2026-02-03','precision':'day','original_text':'February 3'},claim_ids=['exact','other'])
        data['instrument_events']['event']=event
        for cid in ['exact','other']:
            data['claims'][cid]=dict(schema_version='1.0.0',claim_id=cid,subject=target,
                predicate='instrument_event' if cid=='exact' else 'other',
                value={f:event[f] for f in ('instrument','action','occurrence')} if cid=='exact' else 'Unrelated source fact')
        def accepted(key,t,scope,cid):
            data['review_decisions'][key]=dict(schema_version='1.0.0',decision_id=key,target=t,
                scope=scope,claim_ids=[cid],disposition='accepted',supersedes_id=None)
        accepted('accept-other',{'table':'claims','id':'other'},'other','other')
        for field in ['instrument','action','occurrence']:accepted(field,target,field,'other')
        registry=Registry();plan=make_plan(data,self.registry)
        plan.update(schema_version='1.0.1',validation_profile=dict(name='1.0.1',
            schema_sha256=m.digest(m.profile_path('1.0.1').read_bytes()),semantics='event-exact-accepted-v1'))
        def refresh():
            plan['record_reviews']=[]
            for table,records in data.items():
                for key,record in records.items():
                    registry.entities[key]={'table':table,'successors':[]}
                    plan['record_reviews'].append(dict(table=table,id=key,record_sha256=m.digest(m.encode(record).encode()),
                        previous_sha256=None,accepted_fields=sorted(set(record)-{m.IDS[table],'schema_version'}),unresolved_fields=[],publication='reviewed_metadata'))
        proofs=[{'claim_id':cid,'evidence_verified':True} for cid in ['exact','other']]
        refresh()
        with self.assertRaisesRegex(ValueError,'accepted exact event claim'):m.review_gate(data,registry,plan,proofs,rows())
        accepted('accept-exact',{'table':'claims','id':'exact'},'instrument_event','exact');refresh()
        with self.assertRaisesRegex(ValueError,'Event field must cite'):m.review_gate(data,registry,plan,proofs,rows())
        for field in ['instrument','action','occurrence']:data['review_decisions'][field]['claim_ids']=['exact']
        refresh();m.review_gate(data,registry,plan,proofs,rows())
        plan.pop('validation_profile');plan['schema_version']='1.0.0'
        with self.assertRaisesRegex(ValueError,'explicit validation profile'):m.review_gate(data,registry,plan,proofs,rows())

    def test_profile_pin_is_independent_of_record_format_and_cannot_drift(self):
        plan=copy.deepcopy(self.plan);m.validate_plan(plan)
        plan.update(schema_version='1.0.1',validation_profile=dict(name='1.0.1',
            schema_sha256=m.digest(m.profile_path('1.0.1').read_bytes()),semantics='event-exact-accepted-v1'))
        m.validate_plan(plan)
        plan['validation_profile']['schema_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'profile pin'):m.validate_plan(plan)

    def test_new_publication_cannot_opt_out_of_event_profile(self):
        data=rows();data['instrument_events']['event']={'schema_version':'1.0.0','event_id':'event'}
        plan=make_plan(data,self.registry)
        # Isolate the publication policy even if a historical structural checker
        # reports success and other review checks are stubbed by a caller/test.
        with patch.object(m,'validate',return_value=([],data)), patch.object(m,'review_gate') as gate:
            with self.assertRaisesRegex(ValueError,'cannot downgrade validation profile'):
                m.publish(self.destination,self.candidate,self.registry,plan,[])
            gate.assert_not_called()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.registry=self.root/'registry.jsonl';self.registry.write_text('')
        self.candidate=self.root/'candidate';self.candidate.mkdir();self.destination=self.root/'public'/'expanded'
        self.data=rows();self.plan=make_plan(self.data,self.registry)

    def publish(self,plan=None,apply=False):
        return m.publish(self.destination,self.candidate,self.registry,plan or self.plan,[],apply)

    def test_empty_preview_apply_replay_and_snapshot_reader(self):
        self.assertEqual(self.publish()['state'],'ready')
        self.assertFalse(self.destination.parent.exists())
        self.assertEqual(self.publish(apply=True)['state'],'applied')
        self.assertTrue(self.destination.is_symlink())
        pinned=self.destination.resolve()
        self.assertEqual(m.read_snapshot(self.destination),m.serialized(self.data))
        self.assertEqual(self.publish(apply=True)['state'],'already_applied')
        self.assertEqual(self.destination.resolve(),pinned)

    def test_stale_baseline_and_registry_never_publish(self):
        plan=copy.deepcopy(self.plan);plan['expected_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'Snapshot changed'):
            self.publish(plan,True)
        self.assertFalse(self.destination.exists())
        self.registry.write_text('\n')
        with self.assertRaisesRegex(ValueError,'Identity registry changed'):
            self.publish(apply=True)
        self.assertFalse(self.destination.exists())

    def test_changed_candidate_and_schema_error_leave_pointer_unchanged(self):
        self.publish(apply=True);before=self.destination.readlink()
        with patch.object(m,'validate',return_value=(['invalid field'],rows())):
            with self.assertRaisesRegex(ValueError,'Invalid candidate'):self.publish(apply=True)
        self.assertEqual(self.destination.readlink(),before)
        (self.candidate/'unknown.jsonl').write_text('{}\n')
        with self.assertRaisesRegex(ValueError,'Invalid candidate'):self.publish(apply=True)
        self.assertEqual(self.destination.readlink(),before)

    def test_changed_replay_plan_is_rejected(self):
        self.publish(apply=True);plan=copy.deepcopy(self.plan);plan['rationale']='changed acceptance'
        with self.assertRaisesRegex(ValueError,'Replay plan differs'):self.publish(plan,True)

    def test_changed_retained_plan_cannot_hide_behind_original_hash(self):
        self.publish(apply=True)
        path=self.destination.resolve()/'publication.json'
        receipt=json.loads(path.read_text())
        receipt['plan']['rationale']='Changed retained plan after publication'
        path.write_text(json.dumps(receipt)+'\n')
        with self.assertRaisesRegex(ValueError,'receipt drift'):
            self.publish(apply=True)

    def test_concurrent_identical_publication_has_one_apply_one_replay(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            states=list(pool.map(lambda _:self.publish(apply=True)['state'],range(2)))
        self.assertCountEqual(states,['applied','already_applied'])

    def test_schema_validity_cannot_bypass_identity_or_field_review(self):
        record={'schema_version':'1.0.0','jurisdiction_id':str(UUID(int=1)), 'name':'Synthetic jurisdiction'}
        data=rows();key=record['jurisdiction_id'];data['jurisdictions'][key]=record
        plan=make_plan(data,self.registry)
        with self.assertRaisesRegex(ValueError,'Every snapshot record'):
            m.review_gate(data,Registry(),plan,[],rows())
        review={'table':'jurisdictions','id':key,'record_sha256':m.digest(m.encode(record).encode()),
                'previous_sha256':None,'accepted_fields':['name'],'unresolved_fields':[],
                'publication':'reviewed_metadata'}
        plan['record_reviews']=[review]
        with self.assertRaisesRegex(ValueError,'allocated identity'):
            m.review_gate(data,Registry(),plan,[],rows())
        registry=Registry();registry.entities[key]={'table':'jurisdictions','successors':[]}
        with self.assertRaisesRegex(ValueError,'scoped acceptance'):
            m.review_gate(data,registry,plan,[],rows())
        review['accepted_fields']=[];review['unresolved_fields']=['name']
        with self.assertRaisesRegex(ValueError,'factual assertion'):
            m.review_gate(data,registry,plan,[],rows())

    def test_empty_structured_date_is_unresolved_but_date_assertions_are_not(self):
        key=str(UUID(int=411))
        unknown={'earliest':None,'latest':None,'precision':'unknown','original_text':None}
        record={'schema_version':'1.0.0','restriction_id':key,'adoption':unknown}
        data=rows();data['local_restrictions'][key]=record
        registry=Registry();registry.entities[key]={'table':'local_restrictions','successors':[]}
        plan=make_plan(data,self.registry)
        review={'table':'local_restrictions','id':key,'record_sha256':m.digest(m.encode(record).encode()),
                'previous_sha256':None,'accepted_fields':[],'unresolved_fields':['adoption'],
                'publication':'reviewed_metadata'}
        plan['record_reviews']=[review]
        m.review_gate(data,registry,plan,[],rows())
        for field,value in [('earliest','2026-11-03'),('original_text','effective after certification'),('unexpected',None)]:
            with self.subTest(field=field):
                record['adoption']={**unknown,field:value}
                review['record_sha256']=m.digest(m.encode(record).encode())
                with self.assertRaisesRegex(ValueError,'factual assertion'):
                    m.review_gate(data,registry,plan,[],rows())

    def test_interrupted_pointer_swap_keeps_old_publication_absent(self):
        with patch.object(Path,'replace',side_effect=OSError('simulated interruption')):
            with self.assertRaisesRegex(OSError,'simulated interruption'):
                self.publish(apply=True)
        self.assertFalse(self.destination.exists())
        snapshots=self.destination.parent/'expanded-snapshots'
        self.assertEqual(len(list(snapshots.iterdir())),1)
        with self.assertRaisesRegex(ValueError,'Unreferenced snapshot exists'):
            self.publish(apply=True)

    def test_field_acceptance_binds_exact_record_and_allows_reviewed_interpretation(self):
        data=rows();key=str(UUID(int=1));cid=str(UUID(int=2));did=str(UUID(int=3))
        data['jurisdictions'][key]={'schema_version':'1.0.0','jurisdiction_id':key,'name':'Synthetic'}
        data['claims'][cid]={'schema_version':'1.0.0','claim_id':cid,'predicate':'name',
                            'subject':{'table':'jurisdictions','id':key}}
        data['review_decisions'][did]={'schema_version':'1.0.0','decision_id':did,
            'target':{'table':'jurisdictions','id':key},'scope':'name',
            'disposition':'accepted','supersedes_id':None,'claim_ids':[cid]}
        registry=Registry();plan=make_plan(data,self.registry)
        def refresh():
            plan['record_reviews']=[]
            for table,records in data.items():
                for identifier,record in records.items():
                    registry.entities[identifier]={'table':table,'successors':[]}
                    plan['record_reviews'].append({'table':table,'id':identifier,
                        'record_sha256':m.digest(m.encode(record).encode()),'previous_sha256':None,
                        'accepted_fields':sorted(set(record)-{m.IDS[table],'schema_version'}),
                        'unresolved_fields':[],'publication':'reviewed_metadata'})
        refresh();proofs=[{'claim_id':cid,'evidence_verified':True}]
        # Full structural validation separately enforces claim-level acceptance.
        m.review_gate(data,registry,plan,proofs,rows())
        data['jurisdictions'][key]['name']='Changed after review'
        with self.assertRaisesRegex(ValueError,'fingerprint changed'):
            m.review_gate(data,registry,plan,proofs,rows())
        refresh();data['claims'][cid]['predicate']='unrelated';refresh()
        # Source transcription and reviewed interpretation have distinct scopes.
        m.review_gate(data,registry,plan,proofs,rows())
        data['review_decisions'][did]['scope']='other_field';refresh()
        with self.assertRaisesRegex(ValueError,'scoped acceptance'):
            m.review_gate(data,registry,plan,proofs,rows())

    def test_source_quote_proofs_cannot_be_skipped(self):
        data=rows();data['claims']['synthetic-claim']={'claim_id':'synthetic-claim'}
        plan=make_plan(data,self.registry)
        plan['record_reviews']=[{'table':'claims','id':'synthetic-claim','record_sha256':'a'*64,
            'previous_sha256':None,'accepted_fields':[],'unresolved_fields':[], 'publication':'reviewed_excerpt'}]
        with self.assertRaisesRegex(ValueError,'independently verified'):
            m.review_gate(data,Registry(),plan,[],rows())


if __name__=='__main__':unittest.main()
