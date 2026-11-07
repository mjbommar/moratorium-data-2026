"""Complete synthetic source-byte publication and offline event maintenance."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from uuid import uuid5, NAMESPACE_URL

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import expanded_promotion as promotion
from expanded_data import IDS, validate, profile_path
from expanded_identity import Registry,read_events
from check_expanded_publication import check
from build_expanded_csv import build_outputs,publish as csv_publish,download_block
from audit_refresh_returns import evidence_index,audit_expanded_evidence
from test_instrument_event_maintenance import empty,add_event,withdraw,restore,correction


def opaque(value):return str(uuid5(NAMESPACE_URL,'synthetic-event-profile:'+value))


class EventProfilePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.data=self.root/'data';self.data.mkdir();self.destination=self.data/'expanded'
        self.legacy=self.data/'moratorium_inventory.csv';self.legacy.write_text('moratorium_id\nlegacy\n')
        (self.data/'state_legislation.csv').write_text('policy_action_id\n')
        self.registry=self.data/'identities/expanded.jsonl';self.registry.parent.mkdir();self.registry.write_text('')
        self.evidence=self.root/'evidence';self.evidence.mkdir()
        self.body=b'Synthetic source for mechanical tests only. Original adoption and corrected source statements are fixture assertions.\n'
        self.sha=hashlib.sha256(self.body).hexdigest();self.url='https://fixture.invalid/synthetic-ordinance'
        for suffix in ['body','txt']:(self.evidence/('source.'+suffix)).write_bytes(self.body)
        (self.evidence/'source.json').write_text('{}')
        ledger={'state':'finished','kind':'fetch','ok':True,'attempt_id':'synthetic-fetch',
                'artifact':str(self.evidence/'source.json'),'url':self.url,'body_sha256':self.sha,'text_sha256':self.sha}
        (self.evidence/'attempts.private.jsonl').write_text(json.dumps(ledger)+'\n')
        self.raw=empty();add_event(self.raw);self.previous={t:{} for t in IDS}

    def records(self):
        mapping={key:opaque(key) for table in self.raw.values() for key in table}
        def mapped(value):
            if isinstance(value,str):return mapping.get(value,value)
            if isinstance(value,list):return [mapped(v) for v in value]
            if isinstance(value,dict):return {k:mapped(v) for k,v in value.items()}
            return value
        rows={t:{} for t in IDS}
        for table,records in self.raw.items():
            for key,record in records.items():rows[table][mapping[key]]={'schema_version':'1.0.0',**mapped(record)}
        sid=opaque('source')
        rows['source_documents'][sid]={'schema_version':'1.0.0','source_document_id':sid,'url':self.url,
            'body_sha256':self.sha,'text_sha256':self.sha,'retrieved_at':'2026-10-01T12:00:00Z',
            'published_date':None,'retrieval_method':'synthetic fixture, no network','extraction_version':'fixture',
            'access_classification':'synthetic','publication_classification':'reviewed_metadata'}
        for c in rows['claims'].values():c.update(source_document_id=sid,quote='Synthetic source for mechanical tests only.',span=None,
            temporal_support={'earliest':None,'latest':None,'precision':'unknown','original_text':None},extraction_provenance='Synthetic fixture, not factual source entailment.')
        return rows

    def prepare(self,reviewed_at='2026-11-01T13:00:00Z'):
        rows=self.records();registry=Registry(read_events(self.registry.read_bytes()))
        with self.registry.open('a') as f:
            for table,records in rows.items():
                for key in records:
                    if key in registry.entities:continue
                    e={'schema_version':'1.0.0','event_id':opaque('allocation:'+key),'action':'allocate','table':table,
                       'inputs':[],'outputs':[key],'aliases':[{'namespace':'synthetic-event-profile','source_id':key,'record_sha256':promotion.digest(promotion.encode(records[key]).encode())}],'assignments':[],'reviewer':'synthetic reviewer',
                       'reviewed_at':reviewed_at,'rationale':'Synthetic transaction identity only.',
                       'evidence':[{'url':self.url,'body_sha256':self.sha,'locator':'Synthetic source fixture'}]}
                    registry.add(e);f.write(json.dumps(e)+'\n')
        candidate=self.root/'candidate';candidate.mkdir(exist_ok=True)
        for table,raw in promotion.serialized(rows).items():(candidate/(table+'.jsonl')).write_bytes(raw)
        expected=promotion.fingerprint(promotion.serialized(self.previous)) if self.destination.exists() else None
        plan={'schema_version':'1.0.2','expected_sha256':expected,'registry_sha256':promotion.digest(self.registry.read_bytes()),
              'snapshot_sha256':promotion.fingerprint(promotion.serialized(rows)),'reviewer':'synthetic reviewer',
              'reviewed_at':reviewed_at,'rationale':'Synthetic source-byte maintenance transaction, no real event acceptance.',
              'expected_publication_sha256':promotion.digest((self.destination.resolve()/'publication.json').read_bytes()) if self.destination.exists() else None,
              'validation_profile':{'name':'1.0.2','schema_sha256':promotion.digest(profile_path('1.0.2').read_bytes()),'semantics':'event-validity-v1'},'record_reviews':[]}
        for table,records in rows.items():
            for key,r in records.items():
                fields=set(r)-{IDS[table],'schema_version'};old=self.previous[table].get(key)
                withdrawn=table=='instrument_events' and any(d['target']=={'table':table,'id':key} and d['scope']=='event_validity'
                    and d['disposition']=='rejected' and not any(n['supersedes_id']==d['decision_id'] for n in rows['review_decisions'].values()) for d in rows['review_decisions'].values())
                unresolved=[k for k in fields if table=='instrument_events' and r[k] is None]
                plan['record_reviews'].append({'table':table,'id':key,'record_sha256':promotion.digest(promotion.encode(r).encode()),
                    'previous_sha256':promotion.digest(promotion.encode(old).encode()) if old else None,
                    'accepted_fields':[] if withdrawn else sorted(fields-set(unresolved)),
                    'unresolved_fields':[] if withdrawn else unresolved,'historical_fields':sorted(fields) if withdrawn else [],'publication':'reviewed_metadata'})
        index,issues,_=evidence_index(self.evidence);self.assertFalse(issues)
        issues,proofs=audit_expanded_evidence(rows,index);self.assertFalse(issues)
        plan['evidence_sha256']=promotion.evidence_fingerprint(proofs)
        return rows,candidate,plan

    def publish(self,time='2026-11-01T13:00:00Z'):
        rows,candidate,plan=self.prepare(time)
        result=promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],apply=True,moratoria=self.legacy)
        self.previous=copy.deepcopy(rows)
        return rows,candidate,plan,result

    def test_real_source_gate_withdraw_replay_offline_and_separate_views(self):
        self.publish();withdraw(self.raw)
        rows,candidate,plan,result=self.publish('2026-11-02T13:00:00Z')
        self.assertEqual(result['state'],'applied')
        self.assertEqual(result['generation_id'],self.destination.resolve().name)
        self.assertNotEqual(result['generation_id'],result['sha256'])
        self.assertEqual(result['publication_sha256'],promotion.digest((self.destination.resolve()/'publication.json').read_bytes()))
        self.assertEqual(promotion.publish(self.destination,candidate,self.registry,plan,[],apply=True,moratoria=self.legacy)['state'],'already_applied')
        self.assertEqual(check(self.destination,self.registry,self.legacy)['generations_checked'],2)
        generation,outputs=build_outputs(self.destination.resolve())
        self.assertEqual(len(list(csv.DictReader(outputs['instrument_events.csv'].decode().splitlines()))),1)
        self.assertEqual(len(list(csv.DictReader(outputs['instrument_events_current.csv'].decode().splitlines()))),0)
        status=list(csv.DictReader(outputs['instrument_event_status.csv'].decode().splitlines()))[0]
        self.assertEqual(status['review_state'],'withdrawn')
        self.assertEqual(json.loads(outputs['manifest.json'])['validation_profile']['name'],'1.0.2')
        self.assertEqual(len(json.loads(outputs['manifest.json'])['files']),18)
        csv_publish(self.data,generation,outputs)
        (self.data/'README.md').write_text('# Synthetic downloads\n'+download_block(generation,outputs)+'\n')
        shutil.rmtree(self.evidence)
        # No bodies or Git repository in a second root: execute actual restored checkers.
        with tempfile.TemporaryDirectory() as temp:
            restored=Path(temp);shutil.copytree(self.data,restored/'data',symlinks=True)
            scripts=restored/'scripts';scripts.mkdir()
            for name in ['expanded_data','expanded_promotion','expanded_identity','audit_refresh_returns','visual_claim_review',
                         'check_expanded_publication','build_expanded_csv','instrument_event_maintenance','legacy_moratorium_identity','preview_legacy_identity']:
                shutil.copyfile(ROOT/('scripts/'+name+'.py'),scripts/(name+'.py'))
            schemas=restored/'work/schemas/expanded';schemas.mkdir(parents=True)
            for version in ['1.0.0','1.0.1','1.0.2']:shutil.copyfile(profile_path(version),schemas/(version+'.json'))
            for script,args in [('check_expanded_publication.py',[]),('build_expanded_csv.py',['--check'])]:
                result=subprocess.run([sys.executable,str(scripts/script),*args],cwd=restored,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            for dependency in [schemas/'1.0.2.json',scripts/'instrument_event_maintenance.py']:
                content=dependency.read_bytes();dependency.unlink()
                result=subprocess.run([sys.executable,str(scripts/'check_expanded_publication.py')],cwd=restored,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                dependency.write_bytes(content)
            schema=schemas/'1.0.2.json';schema.write_bytes(schema.read_bytes()+b'\n')
            result=subprocess.run([sys.executable,str(scripts/'check_expanded_publication.py')],cwd=restored,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)

    def test_reinstatement_and_second_withdrawal_preserve_all_generations(self):
        self.publish();withdraw(self.raw);self.publish('2026-11-02T13:00:00Z')
        restore(self.raw);self.publish('2026-11-03T13:00:00Z')
        withdraw(self.raw,time='2026-11-04T12:00:00Z');self.publish('2026-11-04T13:00:00Z')
        self.assertEqual(check(self.destination,self.registry,self.legacy)['generations_checked'],4)

    def test_missing_private_source_or_wrong_quote_cannot_promote_withdrawal(self):
        self.publish();before=self.destination.readlink();withdraw(self.raw)
        rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z');(self.evidence/'source.body').unlink()
        with self.assertRaisesRegex(ValueError,'Evidence integrity'):promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],apply=True,moratoria=self.legacy)
        self.assertEqual(self.destination.readlink(),before)

    def test_backdated_transition_and_historical_fields_on_current_or_new_rows_fail(self):
        self.publish();withdraw(self.raw,time='2026-11-01T12:30:00Z')
        rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z')
        with self.assertRaisesRegex(ValueError,'backdates predecessor'):promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)
        fresh=empty();add_event(fresh);self.raw=fresh;self.previous={t:{} for t in IDS}
        rows,candidate,plan=self.prepare()
        review=next(r for r in plan['record_reviews'] if r['table']=='instrument_events')
        review['historical_fields']=review['accepted_fields'];review['accepted_fields']=[]
        registry=Registry(read_events(self.registry.read_bytes()))
        index,_,_=evidence_index(self.evidence);_,proofs=audit_expanded_evidence(rows,index)
        with self.assertRaisesRegex(ValueError,'Historical fields require'):promotion.review_gate(rows,registry,plan,proofs,self.previous)

    def test_correction_uses_new_ids_and_retains_withdrawn_original(self):
        self.publish();add_event(self.raw,'two',time='2026-11-02T12:00:00Z');add_event(self.raw,'three',time='2026-11-02T12:00:00Z');withdraw(self.raw);correction(self.raw,'one',['two','three'])
        self.publish('2026-11-02T13:00:00Z');_,outputs=build_outputs(self.destination.resolve())
        self.assertEqual(len(list(csv.DictReader(outputs['instrument_events.csv'].decode().splitlines()))),3)
        current=list(csv.DictReader(outputs['instrument_events_current.csv'].decode().splitlines()))
        self.assertEqual({r['event_id'] for r in current},{opaque('two'),opaque('three')})

    def test_receipt_profile_or_proof_drift_stops_replay_and_projection(self):
        rows,candidate,plan,_=self.publish();path=self.destination.resolve()/'publication.json';original=path.read_bytes()
        for mutation in ['missing_profile','wrong_profile_hash','missing_proofs','altered_proof_span']:
            receipt=json.loads(original)
            if mutation=='missing_profile':del receipt['plan']['validation_profile']
            elif mutation=='wrong_profile_hash':receipt['plan']['validation_profile']['schema_sha256']='0'*64
            elif mutation=='missing_proofs':receipt['evidence']=[]
            else:receipt['evidence'][0]['verified_span']=[1,3]
            path.write_text(json.dumps(receipt))
            with self.assertRaises(ValueError):build_outputs(self.destination.resolve())
            with self.assertRaises(ValueError):promotion.publish(self.destination,candidate,self.registry,plan,[],moratoria=self.legacy)
            path.write_bytes(original)

    def test_backdated_successor_without_new_event_decisions_is_rejected(self):
        self.publish()
        self.raw['claims']['other']={'claim_id':'other','subject':{'table':'instrument_events','id':'one'},'predicate':'context','value':'Synthetic unused contextual observation'}
        rows,candidate,plan=self.prepare('2026-11-01T12:30:00Z')
        with self.assertRaisesRegex(ValueError,'follow predecessor review'):
            promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)

    def test_missing_predecessor_receipt_stops_maintenance_without_pointer_change(self):
        self.publish();before=self.destination.readlink();withdraw(self.raw)
        rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z');(self.destination.resolve()/'publication.json').unlink()
        with self.assertRaises((OSError,ValueError)):promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)
        self.assertEqual(self.destination.readlink(),before)

    def test_old_profiles_keep_freeform_scope_semantics_but_new_maintenance_cannot_opt_out(self):
        rows,candidate,plan,_=self.publish();path=self.destination.resolve()/'publication.json'
        receipt=json.loads(path.read_text());old=copy.deepcopy(plan);old['schema_version']='1.0.1';old.pop('evidence_sha256');old.pop('expected_publication_sha256')
        old['validation_profile']={'name':'1.0.1','schema_sha256':promotion.digest(profile_path('1.0.1').read_bytes()),'semantics':'event-exact-accepted-v1'}
        for review in old['record_reviews']:review.pop('historical_fields')
        receipt['plan']=old;receipt['plan_sha256']=promotion.digest(promotion.encode(old).encode())
        old_target=path.parent.with_name(receipt['sha256']);path.parent.rename(old_target)
        self.destination.unlink();self.destination.symlink_to('expanded-snapshots/'+old_target.name)
        path=old_target/'publication.json';path.write_text(json.dumps(receipt))
        self.assertEqual(check(self.destination,self.registry,self.legacy)['state'],'consistent')
        with self.assertRaisesRegex(ValueError,'maintenance requires validation profile 1.0.2'):
            promotion.publish(self.root/'other/expanded',candidate,self.registry,old,[self.evidence],moratoria=self.legacy)

    def test_actual_profile1_predecessor_migrates_directly_to_reviewed_withdrawal(self):
        self.raw=empty();add_event(self.raw,validity=False)
        rows,candidate,plan=self.prepare();plan['schema_version']='1.0.1';plan.pop('evidence_sha256');plan.pop('expected_publication_sha256')
        plan['validation_profile']={'name':'1.0.1','schema_sha256':promotion.digest(profile_path('1.0.1').read_bytes()),'semantics':'event-exact-accepted-v1'}
        for review in plan['record_reviews']:review.pop('historical_fields')
        promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],apply=True,moratoria=self.legacy)
        self.previous=copy.deepcopy(rows)
        self.assertNotIn('instrument_events_current.csv',build_outputs(self.destination.resolve())[1])
        withdraw(self.raw);self.publish('2026-11-02T13:00:00Z')
        self.assertEqual(check(self.destination,self.registry,self.legacy)['generations_checked'],2)
        self.assertIn('instrument_events_current.csv',build_outputs(self.destination.resolve())[1])

    def test_new_profile_cannot_downgrade_or_assign_historical_fields_to_sources(self):
        self.publish();withdraw(self.raw);rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z')
        source=next(r for r in plan['record_reviews'] if r['table']=='source_documents')
        source['historical_fields']=source['accepted_fields'];source['accepted_fields']=[]
        with self.assertRaisesRegex(ValueError,'Historical fields require'):
            promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)
        self.raw=empty();add_event(self.raw)
        self.raw['claims']['other']={'claim_id':'other','subject':{'table':'instrument_events','id':'one'},'predicate':'context','value':'Synthetic observation'}
        rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z');plan['schema_version']='1.0.1';plan.pop('evidence_sha256');plan.pop('expected_publication_sha256')
        plan['validation_profile']={'name':'1.0.1','schema_sha256':promotion.digest(profile_path('1.0.1').read_bytes()),'semantics':'event-exact-accepted-v1'}
        for review in plan['record_reviews']:review.pop('historical_fields')
        with self.assertRaisesRegex(ValueError,'Cannot downgrade'):
            promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)

    def test_withdrawal_basis_quote_must_be_located_even_if_plan_pins_failed_proof(self):
        self.publish();before=self.destination.readlink();withdraw(self.raw);rows,candidate,plan=self.prepare('2026-11-02T13:00:00Z')
        claim=next(c for c in rows['claims'].values() if c['predicate']=='event_validity')
        claim['quote']='This quotation is not present anywhere in the retained synthetic source.'
        for table,raw in promotion.serialized(rows).items():(candidate/(table+'.jsonl')).write_bytes(raw)
        plan['snapshot_sha256']=promotion.fingerprint(promotion.serialized(rows))
        next(r for r in plan['record_reviews'] if r['id']==claim['claim_id'])['record_sha256']=promotion.digest(promotion.encode(claim).encode())
        index,_,_=evidence_index(self.evidence);_,proofs=audit_expanded_evidence(rows,index)
        plan['evidence_sha256']=promotion.evidence_fingerprint(proofs)
        with self.assertRaisesRegex(ValueError,'independently verified'):
            promotion.publish(self.destination,candidate,self.registry,plan,[self.evidence],moratoria=self.legacy)
        self.assertEqual(self.destination.readlink(),before)

    def test_coordinated_receipt_rewrite_cannot_reuse_sealed_generation_name(self):
        self.publish();path=self.destination.resolve()/'publication.json';receipt=json.loads(path.read_text())
        receipt['plan']['reviewed_at']='2026-11-01T12:30:00Z'
        receipt['plan_sha256']=promotion.digest(promotion.encode(receipt['plan']).encode())
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'generation name'):check(self.destination,self.registry,self.legacy)
        with self.assertRaisesRegex(ValueError,'generation name'):build_outputs(self.destination.resolve())

    def test_successor_pins_predecessor_receipt_even_if_its_internal_hash_is_recomputed(self):
        self.publish();prior=self.destination.resolve();withdraw(self.raw);self.publish('2026-11-02T13:00:00Z')
        path=prior/'publication.json';receipt=json.loads(path.read_text());receipt['plan']['rationale']='Changed predecessor review'
        receipt['plan_sha256']=promotion.digest(promotion.encode(receipt['plan']).encode());path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'Pinned predecessor publication receipt'):check(self.destination,self.registry,self.legacy)


    def test_receipt_only_successor_has_distinct_seal_and_stale_receipt_cas_is_rejected(self):
        rows,_,_,first=self.publish();before=self.destination.resolve().name
        rows_a,candidate,plan_a=self.prepare('2026-11-02T13:00:00Z')
        rows_b,_,plan_b=self.prepare('2026-11-03T13:00:00Z')
        applied=promotion.publish(self.destination,candidate,self.registry,plan_a,[self.evidence],apply=True,moratoria=self.legacy)
        self.assertEqual(applied['state'],'applied');self.assertNotEqual(before,self.destination.resolve().name)
        self.assertEqual(first['sha256'],applied['sha256']);self.assertEqual(rows,rows_a)
        self.assertEqual(check(self.destination,self.registry,self.legacy)['generations_checked'],2)
        self.assertEqual(promotion.publish(self.destination,candidate,self.registry,plan_a,[],moratoria=self.legacy)['state'],'already_applied')
        with self.assertRaisesRegex(ValueError,'Predecessor publication receipt changed'):
            promotion.publish(self.destination,candidate,self.registry,plan_b,[self.evidence],moratoria=self.legacy)


class EventProfileBundleDependencies(unittest.TestCase):
    def assert_missing_dependency_rejected(self,missing,pattern):
        from unittest.mock import patch
        import build_release_candidate as bundle
        names=['work/research/2026-11-06/pilot-contract-review/manifest.json',
               'scripts/instrument_event_maintenance.py',*[f'work/schemas/expanded/{p}.json' for p in ['1.0.0','1.0.1','1.0.2']]]
        names.remove(missing)
        def git(*args):
            if args[0]=='rev-parse':return b'a'*40
            if args[0]=='ls-tree':return '\n'.join(names).encode()
            if args[0]=='show' and args[1].endswith(':scripts/expanded_data.py'):
                return (ROOT/'scripts/expanded_data.py').read_bytes()
            raise AssertionError('Unexpected Git read: '+repr(args))
        with tempfile.TemporaryDirectory() as temp,patch.object(bundle,'git',side_effect=git):
            with self.assertRaisesRegex(AssertionError,pattern):bundle.build(Path(temp)/'out','synthetic')
            self.assertFalse((Path(temp)/'out').exists())

    def test_declared_profile_cannot_be_missing_from_selected_commit(self):
        self.assert_missing_dependency_rejected('work/schemas/expanded/1.0.2.json','Validator profile absent')

    def test_required_maintenance_module_cannot_be_missing_from_selected_commit(self):
        self.assert_missing_dependency_rejected('scripts/instrument_event_maintenance.py','Missing event maintenance runtime')
