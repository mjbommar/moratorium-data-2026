"""Synthetic policy succession through schema, review, publication and CSV."""
import copy
import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_event_profile_publication as fixture
from test_instrument_event_maintenance import add_event, decide
from instrument_event_maintenance import event_target
from expanded_data import profile_path, validate
from expanded_promotion import publish, digest
from check_expanded_publication import check
from build_expanded_csv import build_outputs

QUAL='Policy succession does not establish formal termination, overlap, or current force.'

def upgrade(plan):
    plan['schema_version']='1.0.4'
    plan['validation_profile']={'name':'1.0.4','schema_sha256':digest(profile_path('1.0.4').read_bytes()),'semantics':'event-validity-conditions-policy-succession-v1'}

class SuccessionTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.EventProfilePublicationTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.legacy.write_text('moratorium_id\nlegacy\npredecessor\n')
        self.f.publish()
        event=add_event(self.f.raw,'succession',time='2026-11-02T12:00:00Z')
        event['action']='policy_successor_adopted'
        event['related_instrument']={'relation':'policy_predecessor','instrument':{'kind':'moratorium','id':'predecessor'},'qualification':QUAL}
        claim=self.f.raw['claims']['exact-succession']
        claim['value']={k:event[k] for k in ('instrument','action','occurrence','related_instrument')}
        decide(self.f.raw,event_target('succession'),'related_instrument',['exact-succession'],time='2026-11-02T12:00:00Z')

    def prepare(self):
        rows,candidate,plan=self.f.prepare('2026-11-02T13:00:00Z');upgrade(plan)
        return rows,candidate,plan

    def test_publication_replay_csv_restore_and_old_bytes(self):
        f=self.f;old=f.destination.resolve();before={p.name:p.read_bytes() for p in old.iterdir()}
        rows,candidate,plan=self.prepare()
        publish(f.destination,candidate,f.registry,plan,[f.evidence],apply=True,moratoria=f.legacy)
        self.assertEqual(before,{p.name:p.read_bytes() for p in old.iterdir()})
        self.assertEqual(check(f.destination,f.registry,f.legacy)['generations_checked'],2)
        self.assertEqual(publish(f.destination,candidate,f.registry,plan,[],apply=True,moratoria=f.legacy)['state'],'already_applied')
        _,outputs=build_outputs(f.destination.resolve())
        events=list(csv.DictReader(io.StringIO(outputs['instrument_events_current.csv'].decode())))
        relation=next(row for row in events if row['action']=='policy_successor_adopted')
        self.assertEqual(json.loads(relation['related_instrument'])['qualification'],QUAL)
        self.assertEqual(len(events),2)
        f.previous=copy.deepcopy(rows)
        _,candidate,downgrade=f.prepare('2026-11-03T13:00:00Z')
        with self.assertRaisesRegex(ValueError,'Invalid candidate'):
            publish(f.destination,candidate,f.registry,downgrade,[f.evidence],apply=True,moratoria=f.legacy)
        with tempfile.TemporaryDirectory() as temp:
            restored=Path(temp);shutil.copytree(f.data,restored/'data',symlinks=True)
            shutil.copytree(ROOT/'scripts',restored/'scripts');shutil.copytree(ROOT/'work/schemas/expanded',restored/'work/schemas/expanded')
            p=subprocess.run([sys.executable,str(restored/'scripts/check_expanded_publication.py')],cwd=restored,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            sys.path.insert(0,str(restored/'scripts'))
            p=subprocess.run([sys.executable,'-c',"from build_expanded_csv import build_outputs; from pathlib import Path; print(build_outputs(Path('data/expanded'))[0])"],cwd=restored,env={'PYTHONPATH':str(restored/'scripts')},capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)

    def test_valid_old_style_profile_downgrade_and_offline_history_guard(self):
        from unittest.mock import patch
        import expanded_promotion as promotion
        f=fixture.EventProfilePublicationTests();f.setUp();self.addCleanup(f.doCleanups)
        rows,candidate,plan=f.prepare();upgrade(plan)
        self.assertEqual(validate(candidate,f.legacy,profile='1.0.4')[0],[])
        publish(f.destination,candidate,f.registry,plan,[f.evidence],apply=True,moratoria=f.legacy)
        f.previous=copy.deepcopy(rows)
        for version,semantics in [('1.0.2','event-validity-v1'),('1.0.3','event-validity-conditions-v1')]:
            with self.subTest(version=version):
                _,candidate,old=f.prepare('2026-11-02T13:00:00Z')
                old['schema_version']=version
                old['validation_profile']={'name':version,'schema_sha256':digest(profile_path(version).read_bytes()),'semantics':semantics}
                self.assertEqual(validate(candidate,f.legacy,profile=version)[0],[])
                with self.assertRaisesRegex(ValueError,'Cannot downgrade condition publication profile'):
                    publish(f.destination,candidate,f.registry,old,[f.evidence],moratoria=f.legacy)
        # Construct a sealed invalid history by bypassing only the online guard.
        # The offline checker must independently reject the otherwise valid receipt.
        original=promotion.require
        def bypass(condition,message):
            if message=='Cannot downgrade condition publication profile': return
            original(condition,message)
        with patch.object(promotion,'require',side_effect=bypass):
            publish(f.destination,candidate,f.registry,old,[f.evidence],apply=True,moratoria=f.legacy)
        with self.assertRaisesRegex(ValueError,'Cannot downgrade condition publication profile'):
            check(f.destination,f.registry,f.legacy)

    def test_registry_resolves_restriction_aliases_at_review_gate(self):
        from expanded_identity import Registry, read_events
        from expanded_promotion import review_gate
        from audit_refresh_returns import evidence_index, audit_expanded_evidence
        from test_expanded_identity import event as identity_event, alias, uid
        f=self.f
        # Two separately allocated restrictions are retained from a prior snapshot;
        # merging the identities does not mutate their historical records.
        rows,candidate,plan=self.prepare()
        a,b=uid(1),uid(2)
        event=next(e for e in rows['instrument_events'].values() if e['action']=='policy_successor_adopted')
        event['instrument']={'kind':'restriction','id':a}
        event['related_instrument']['instrument']={'kind':'restriction','id':b}
        rows['claims'][event['claim_ids'][0]]['value']={k:event[k] for k in ('instrument','action','occurrence','related_instrument')}
        # The same relation also passes the full 1.0.4 domain validator when
        # its two retained restriction rows use complete schema-valid records.
        from test_expanded_data import ExpandedContracts
        from expanded_promotion import serialized
        valid=copy.deepcopy(rows)
        town=json.loads((ROOT/'work/schemas/expanded/fixtures/synthetic/jurisdictions.jsonl').read_text())
        valid['jurisdictions'][town['jurisdiction_id']]=town
        for key in (a,b):
            restriction=ExpandedContracts().restriction();restriction['restriction_id']=key
            valid['local_restrictions'][key]=restriction
        for table,content in serialized(valid).items():(candidate/(table+'.jsonl')).write_bytes(content)
        self.assertEqual(validate(candidate,f.legacy,profile='1.0.4')[0],[])
        previous=copy.deepcopy(f.previous)
        for key in (a,b):
            row={'schema_version':'1.0.0','restriction_id':key}
            rows['local_restrictions'][key]=row;previous['local_restrictions'][key]=copy.deepcopy(row)
            plan['record_reviews'].append({'table':'local_restrictions','id':key,'record_sha256':digest(json.dumps(row,sort_keys=True,separators=(',',':')).encode()),'previous_sha256':digest(json.dumps(row,sort_keys=True,separators=(',',':')).encode()),'accepted_fields':[],'unresolved_fields':[],'historical_fields':[],'publication':'reviewed_metadata'})
        for review in plan['record_reviews']:
            record=rows[review['table']][review['id']]
            review['record_sha256']=digest(json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
        index,_,_=evidence_index(f.evidence);_,proofs=audit_expanded_evidence(rows,index)
        from expanded_promotion import evidence_fingerprint
        plan['evidence_sha256']=evidence_fingerprint(proofs)
        registry=Registry(read_events(f.registry.read_bytes()))
        for n,key in [(1,a),(2,b)]:registry.add(identity_event(n,'allocate',[],[key],[alias(n)],table='local_restrictions'))
        registry.add(identity_event(3,'merge',[a,b],[a],table='local_restrictions'))
        self.assertEqual(registry.resolve(a),registry.resolve(b))
        self.assertEqual(registry.resolve_alias('local_restrictions',alias(2)),{a})
        with self.assertRaisesRegex(ValueError,'Policy succession references resolve to the same identity'):
            review_gate(rows,registry,plan,proofs,previous,'2026-11-01T13:00:00Z')
        registry.add(identity_event(4,'split',[a],[uid(3),uid(4)],assignments=[{'alias':alias(1),'canonical_id':uid(3)},{'alias':alias(2),'canonical_id':None}],table='local_restrictions'))
        self.assertEqual(registry.resolve_alias('local_restrictions',alias(2)),{uid(3),uid(4)})
        with self.assertRaisesRegex(ValueError,'Policy succession restriction reference is ambiguous'):
            review_gate(rows,registry,plan,proofs,previous,'2026-11-01T13:00:00Z')
        # A later reviewed withdrawal preserves the original event bytes even
        # when the retained restriction identity has since split.
        from test_instrument_event_maintenance import withdraw
        prior=copy.deepcopy(rows);f.previous=prior
        raw=f.raw['instrument_events']['succession']
        raw['instrument']={'kind':'restriction','id':a}
        raw['related_instrument']['instrument']={'kind':'restriction','id':b}
        f.raw['claims']['exact-succession']['value']={k:copy.deepcopy(raw[k]) for k in ('instrument','action','occurrence','related_instrument')}
        withdraw(f.raw,'succession',time='2026-11-03T12:00:00Z')
        decide(f.raw,event_target('succession'),'related_instrument',['exact-succession'],'rejected',time='2026-11-03T12:00:00Z')
        later,_,later_plan=f.prepare('2026-11-03T13:00:00Z');upgrade(later_plan)
        for key in (a,b):
            later['local_restrictions'][key]=copy.deepcopy(prior['local_restrictions'][key])
            later_plan['record_reviews'].append(next(copy.deepcopy(r) for r in plan['record_reviews'] if r['table']=='local_restrictions' and r['id']==key))
        index,_,_=evidence_index(f.evidence);_,later_proofs=audit_expanded_evidence(later,index)
        later_plan['evidence_sha256']=evidence_fingerprint(later_proofs)
        later_registry=Registry(read_events(f.registry.read_bytes()))
        for identity in registry.events.values():
            if identity['event_id'] not in later_registry.events:later_registry.add(identity)
        self.assertEqual(later['instrument_events'][event['event_id']],prior['instrument_events'][event['event_id']])
        review_gate(later,later_registry,later_plan,later_proofs,prior,'2026-11-02T13:00:00Z')

    def test_schema_and_review_reject_mutations(self):
        rows,candidate,plan=self.prepare();f=self.f
        event=next(r for r in rows['instrument_events'].values() if r['action']=='policy_successor_adopted')
        schema=json.loads(profile_path('1.0.4').read_text());v=Draft202012Validator({'$ref':'#/$defs/instrument_events','$defs':schema['$defs']})
        self.assertTrue(v.is_valid(event));self.assertFalse(Draft202012Validator({'$ref':'#/$defs/instrument_events','$defs':json.loads(profile_path('1.0.3').read_text())['$defs']}).is_valid(event))
        for mutation in ('missing','wrong_kind','relation','qualification','other_action','undated','unknown','self','claim','unreviewed'):
            with self.subTest(mutation=mutation):
                data=copy.deepcopy(rows);e=data['instrument_events'][event['event_id']];rel=e['related_instrument']
                if mutation=='missing':del e['related_instrument']
                elif mutation=='wrong_kind':rel['instrument']['kind']='ballot_measure'
                elif mutation=='relation':rel['relation']='replaces'
                elif mutation=='qualification':rel['qualification']='terminated'
                elif mutation=='other_action':e['action']='terminated'
                elif mutation=='undated':e['occurrence']['precision']='unknown';e['occurrence']['earliest']=e['occurrence']['latest']=None
                elif mutation=='unknown':rel['instrument']['id']='absent'
                elif mutation=='self':rel['instrument']=copy.deepcopy(e['instrument'])
                elif mutation=='claim':data['claims'][e['claim_ids'][0]]['value']['related_instrument']['instrument']['id']='tampered'
                elif mutation=='unreviewed':
                    data['review_decisions']={k:d for k,d in data['review_decisions'].items() if not (d['target']==event_target(e['event_id']) and d['scope']=='related_instrument')}
                for table,records in data.items():
                    (candidate/(table+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in records.values()))
                errors,_=validate(candidate,f.legacy,profile='1.0.4')
                self.assertTrue(errors,mutation)

if __name__=='__main__':unittest.main()
