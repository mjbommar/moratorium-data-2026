"""Identity changes preserve history, ambiguity, pinned aliases and atomic writes."""
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from uuid import UUID

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('expanded_identity',ROOT/'scripts/expanded_identity.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def uid(n):return str(UUID(int=n))
def alias(n):return {'namespace':'synthetic-job','source_id':str(n),'record_sha256':'a'*64}
def event(n,action,inputs,outputs,aliases=(),assignments=(),table='ballot_measures'):
    return {'schema_version':'1.0.0','event_id':uid(1000+n),'action':action,'table':table,
            'inputs':inputs,'outputs':outputs,'aliases':list(aliases),'assignments':list(assignments),
            'reviewer':'synthetic-reviewer','reviewed_at':'2026-11-05T12:00:00Z',
            'rationale':'Synthetic identity evidence, never actual election facts.',
            'evidence':[{'url':'https://example.invalid/ballot','body_sha256':'b'*64,'locator':'invented fixture'}]}
def plan(events,previous=None):return {'schema_version':'1.0.0','expected_sha256':previous,'events':events}

class IdentityTests(unittest.TestCase):
    def test_same_names_do_not_infer_identity_and_alias_collision_refused(self):
        r=m.Registry([event(1,'allocate',[],[uid(1)],[alias(1)]),event(2,'allocate',[],[uid(2)],[alias(2)])])
        before=copy.deepcopy(r.aliases)
        with self.assertRaisesRegex(ValueError,'Alias collision'):
            r.add(event(3,'alias',[uid(2)],[uid(2)],[alias(1)]))
        self.assertEqual(r.aliases,before)
        self.assertEqual(r.resolve_alias('ballot_measures',alias(1)),{uid(1)})

    def test_merge_retains_old_ids_and_split_preserves_explicit_ambiguity(self):
        r=m.Registry([event(1,'allocate',[],[uid(1)],[alias(1)]),event(2,'allocate',[],[uid(2)],[alias(2)])])
        r.add(event(3,'merge',[uid(1),uid(2)],[uid(1)]))
        self.assertEqual(r.resolve(uid(2)),{uid(1)})
        # Both aliases follow the merge; split must explicitly address both.
        split=event(4,'split',[uid(1)],[uid(3),uid(4)],assignments=[{'alias':alias(1),'canonical_id':uid(3)}])
        with self.assertRaisesRegex(ValueError,'Every affected alias'):r.add(split)
        split['assignments'].append({'alias':alias(2),'canonical_id':None});r.add(split)
        self.assertEqual(r.resolve_alias('ballot_measures',alias(1)),{uid(3)})
        self.assertEqual(r.resolve_alias('ballot_measures',alias(2)),{uid(3),uid(4)})
        self.assertEqual(r.resolve(uid(2)),{uid(3),uid(4)})
        self.assertEqual(len(r.events),4)

    def test_retired_or_cross_table_inputs_and_id_reuse_rejected(self):
        r=m.Registry([event(1,'allocate',[],[uid(1)],[alias(1)]),event(2,'allocate',[],[uid(2)],[alias(2)],table='jurisdictions')])
        with self.assertRaisesRegex(ValueError,'same table'):r.add(event(3,'merge',[uid(1),uid(2)],[uid(1)]))
        with self.assertRaisesRegex(ValueError,'collision or reuse'):r.add(event(4,'allocate',[],[uid(1)],[alias(3)]))
        with self.assertRaises(ValueError):r.add(event(5,'split',[uid(1)],[uid(1),uid(3)]))

    def test_plan_atomic_conflict_and_idempotent_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'registry.jsonl';first=plan([event(1,'allocate',[],[uid(1)],[alias(1)])])
            preview=m.apply_plan(p,first);self.assertFalse(p.exists())
            applied=m.apply_plan(p,first,True);self.assertEqual(preview['sha256'],applied['sha256'])
            before=p.read_bytes();self.assertEqual(m.apply_plan(p,first,True)['state'],'already_applied')
            stale=plan([event(2,'allocate',[],[uid(2)],[alias(2)])])
            with self.assertRaisesRegex(ValueError,'changed since'):m.apply_plan(p,stale,True)
            invalid=plan([event(2,'allocate',[],[uid(2)],[alias(2)]),event(3,'alias',[uid(2)],[uid(2)],[alias(1)])],hashlib.sha256(before).hexdigest())
            with self.assertRaisesRegex(ValueError,'Alias collision'):m.apply_plan(p,invalid,True)
            self.assertEqual(p.read_bytes(),before)
            # Reusing an event ID for a different decision is never an idempotent replay.
            changed=copy.deepcopy(first);changed['events'][0]['rationale']='different decision'
            with self.assertRaises(ValueError):m.apply_plan(p,changed,True)
            self.assertEqual(p.read_bytes(),before)

    def test_review_evidence_and_opaque_ids_are_required(self):
        for field,value in [('evidence',[]),('reviewer',''),('reviewed_at','2026-11-05'),('outputs',['eliot-question-5'])]:
            e=event(1,'allocate',[],[uid(1)],[alias(1)]);e[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):m.Registry([e])

    def test_concurrent_plans_cannot_lose_an_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'registry.jsonl'
            def attempt(n):
                try:return m.apply_plan(path,plan([event(n,'allocate',[],[uid(n)],[alias(n)])]),True)['state']
                except ValueError:return 'conflict'
            with ThreadPoolExecutor(max_workers=2) as pool:
                states=list(pool.map(attempt,[1,2]))
            self.assertCountEqual(states,['applied','conflict'])
            self.assertEqual(len(m.read_events(path.read_bytes())),1)

if __name__=='__main__':unittest.main()
