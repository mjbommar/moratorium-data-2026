import asyncio
import datetime as dt
import hashlib
import json
import os
from unittest.mock import patch
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from bc_core.budget import BudgetExceeded
from bc_llm.backend import ScriptedBackend
import extract_rule_units as ext

TEXT = 'Rule Alpha applies unless the site is small. Definition: small means under five. Rule Beta applies to large sites.'
H = hashlib.sha256(TEXT.encode()).hexdigest()
DOC = dict(text=TEXT, text_sha256=H, body_sha256='a'*64)
PLAN = dict(source_text_sha256=H, units=[dict(unit_id='u1', anchor_quote='Rule Alpha', label='First rule', instruction='Extract this unit'), dict(unit_id='u2', anchor_quote='Rule Beta', label='Second rule', instruction='Extract this unit')])
ARGS = dict(model_identity={'model':'scripted:fake', 'settings_id':'fixed'}, today=dt.date(2026,11,7), max_calls=4, max_usd=1.0, reservation_usd=.1, max_source_bytes=1000, settings={})

def candidate(unit, quote='Rule Alpha applies unless the site is small.'):
    return dict(unit_id=unit, outcome='candidate', clause=dict(purpose='exemption', assertion_context='enacted_text', source_text=quote, expression=dict(type='text_predicate', text='site is small')), supporting_quotes=[quote, 'Definition: small means under five.'], unresolved_reason=None)

def unknown(unit):
    return dict(unit_id=unit, outcome='unresolved', clause=None, supporting_quotes=[], unresolved_reason='Cannot determine')

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_proposed_source_enacted_claim_is_flagged_without_repair(self):
        with tempfile.TemporaryDirectory() as d:
            mismatch=candidate('u1')
            consistent=candidate('u2')
            consistent['clause']['assertion_context']='proposed'
            backend=ScriptedBackend({'*':[mismatch,consistent]})
            out=await ext.run(d,{**DOC,'reviewed_source_role':'proposed'},PLAN,
                              backend=backend,**ARGS)
            first,second=out['units']
            self.assertIn('reviewed_source_role_conflict',first['review_flags'])
            self.assertNotIn('reviewed_source_role_conflict',second['review_flags'])
            self.assertEqual(first['clause']['assertion_context'],'enacted_text')
            self.assertFalse(first['accepted'])
            self.assertTrue(first['review_required'])
            self.assertEqual(out,await ext.run(d,{**DOC,'reviewed_source_role':'proposed'},
                                             PLAN,backend=backend,**ARGS))
            self.assertEqual(len(backend.calls),2)

    async def test_document_context_in_actual_requests_and_replay(self):
        for role in ('proposed', 'enacted_text', 'source_reported', 'unknown', None):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as d:
                doc = {**DOC, 'title': 'Enrolled synthetic measure'}
                if role is not None:
                    doc['reviewed_source_role'] = role
                backend = ScriptedBackend({'*': [unknown('u1'), unknown('u2')]})
                packet = await ext.run(d, doc, PLAN, backend=backend, **ARGS)
                prefixes = []
                for call, unit in zip(backend.calls, PLAN['units']):
                    prefix, locator = call['prompt'].rsplit('\nLocal slot (JSON):\n', 1)
                    prefixes.append(prefix)
                    metadata, source = prefix.split('\nFull source:\n', 1)
                    self.assertEqual(source, TEXT)
                    self.assertEqual(json.loads(metadata.removeprefix('Document context (JSON):\n')),
                                     {'title': doc['title'], 'reviewed_source_role': role or 'unknown'})
                    self.assertEqual(json.loads(locator), unit)
                    self.assertEqual(call['role'], 'extractor')
                self.assertEqual(len(prefixes), 2)
                self.assertEqual(prefixes[0], prefixes[1])
                self.assertEqual(packet['provenance'].get('reviewed_source_role'), role)
                self.assertEqual(packet, await ext.run(d, doc, PLAN, backend=backend, **ARGS))
                self.assertEqual(len(backend.calls), 2)

    async def test_metadata_change_rejects_resume_without_calls_or_writes(self):
        with tempfile.TemporaryDirectory() as d:
            doc = {**DOC, 'title': 'Synthetic title', 'reviewed_source_role': 'proposed'}
            backend = ScriptedBackend({'*': [unknown('u1'), unknown('u2')]})
            await ext.run(d, doc, PLAN, backend=backend, **ARGS)
            before = {p.name: p.read_bytes() for p in Path(d).iterdir()}
            for changed in ({**doc, 'title': 'Changed'},
                            {**doc, 'reviewed_source_role': 'enacted_text'},
                            {k: v for k, v in doc.items() if k != 'reviewed_source_role'},
                            {**doc, 'url': 'https://example.test/'}):
                with self.assertRaises(ext.WorkspaceContextChanged):
                    await ext.run(d, changed, PLAN, backend=backend, **ARGS)
                self.assertEqual({p.name: p.read_bytes() for p in Path(d).iterdir()}, before)
            self.assertEqual(len(backend.calls), 2)

    async def test_malformed_metadata_rejected_before_workspace_creation(self):
        for key, value in [('title', None), ('title', ''), ('title', '  '), ('title', 1),
                           ('reviewed_source_role', None), ('reviewed_source_role', ''),
                           ('reviewed_source_role', 'adopted'), ('reviewed_source_role', []),
                           ('reviewed_source_role', 1)]:
            with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as d:
                workspace = Path(d) / 'new'
                backend = ScriptedBackend({})
                with self.assertRaises(ValueError):
                    await ext.run(workspace, {**DOC, key: value}, PLAN, backend=backend, **ARGS)
                self.assertFalse(workspace.exists())
                self.assertEqual(backend.calls, [])

    async def test_slots_full_context_replay_and_unaccepted_quotes(self):
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[candidate('u1'), candidate('u2', 'not in source')]})
            out=await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            self.assertEqual((out['planned_count'],out['candidate_count'],out['unresolved_count']),(2,2,0))
            self.assertEqual(len(backend.calls),2)
            for call in backend.calls:
                self.assertIn(TEXT,call['prompt']); self.assertNotIn('12 claims',call['prompt'])
                self.assertIn('"reviewed_source_role": "unknown"', call['prompt'])
                self.assertNotIn('"title"', call['prompt'])
            self.assertFalse(out['units'][0]['accepted'])
            self.assertIn('quote_unlocated_or_ambiguous',out['units'][1]['review_flags'])
            self.assertEqual(out,await ext.run(d,DOC,PLAN,backend=backend,**ARGS))
            self.assertEqual(len(backend.calls),2)

    async def test_old_implementation_namespace_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            backend = ScriptedBackend({'*': [unknown('u1'), unknown('u2')]})
            await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
            state_path = Path(d) / 'rule-units-state.private.json'
            seal_path = Path(d) / 'rule-units-seal.private.json'
            state = json.loads(state_path.read_text())
            state['context']['implementation_sha256'] = '0' * 64
            state['context_sha256'] = ext.digest(state['context'])
            state_path.write_text(json.dumps(state))
            seal_path.write_text(json.dumps({'sha256': ext.digest(state)}))
            before = {p.name: p.read_bytes() for p in Path(d).iterdir()}
            with self.assertRaises(ext.WorkspaceContextChanged):
                await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
            self.assertEqual({p.name: p.read_bytes() for p in Path(d).iterdir()}, before)
            self.assertEqual(len(backend.calls), 2)

    async def test_context_and_plan_rejected_preserve_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
            await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            path=Path(d)/'rule-units-candidates.private.json'; before=path.read_bytes()
            variations=[(DOC,PLAN,{**ARGS,'reservation_usd':.2}), (DOC,{**PLAN,'units':[{**PLAN['units'][0],'label':'Changed'}, PLAN['units'][1]]},ARGS), ({**DOC,'body_sha256':'b'*64},PLAN,ARGS)]
            for doc,plan,args in variations:
                with self.assertRaises(ValueError): await ext.run(d,doc,plan,backend=backend,**args)
                self.assertEqual(path.read_bytes(),before)
            for anchor in ['missing','Rule']:
                plan={**PLAN,'units':[{**PLAN['units'][0], 'anchor_quote':anchor}]}
                with self.assertRaises(ValueError): await ext.run(d,DOC,plan,backend=backend,**ARGS)
            self.assertEqual(len(backend.calls),2)

    async def test_failure_and_cancellation_consume_reservations(self):
        for failure in (RuntimeError('fail'), asyncio.CancelledError()):
            with tempfile.TemporaryDirectory() as d:
                args={**ARGS,'max_calls':1}
                with self.assertRaises(BaseException): await ext.run(d,DOC,PLAN,backend=ScriptedBackend({'*':[failure]}),**args)
                backend=ScriptedBackend({'*':[unknown('u1')]})
                with self.assertRaises(BudgetExceeded): await ext.run(d,DOC,PLAN,backend=backend,**args)
                self.assertEqual(len(backend.calls),0)
                p=json.loads((Path(d)/'rule-units-candidates.private.json').read_text())
                self.assertEqual(p['unresolved_count'],2)

    async def test_unpriced_overreservation_modelswap_and_bad_response(self):
        class Backend:
            def __init__(self,kind): self.kind=kind; self.calls=0
            async def generate(self,**kw):
                self.calls+=1
                if self.kind=='malformed': return SimpleNamespace(output=SimpleNamespace(model_dump=lambda **kw: {'bad':1}),model='scripted:fake',priced=True,cost_usd=.01)
                return SimpleNamespace(output=ext.Response.model_validate(unknown('u2' if self.kind=='wrong_id' else 'u1')),model='other' if self.kind=='model' else 'scripted:fake',priced=self.kind!='unpriced',cost_usd=.2 if self.kind=='over' else .01)
        for kind in ['unpriced','over','model','malformed','wrong_id']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as d:
                backend=Backend(kind)
                with self.assertRaises(Exception): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                state=json.loads((Path(d)/'rule-units-state.private.json').read_text())
                self.assertEqual(state['attempts'][0]['status'],'failed')
                self.assertFalse(state['successes'])
                if kind in ('unpriced','over','model'):
                    with self.assertRaises(BudgetExceeded): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                    self.assertEqual(backend.calls,1)

    async def test_invalid_accounting_stops_durably(self):
        class Backend:
            def __init__(self, cost, tokens=None):
                self.cost, self.tokens, self.calls = cost, tokens, 0
            async def generate(self, **kwargs):
                self.calls += 1
                return SimpleNamespace(model='scripted:fake', priced=True, cost_usd=self.cost,
                                       input_tokens=self.tokens, output_tokens=0,
                                       output=ext.Response.model_validate(unknown('u1')))
        for cost, tokens in [(float('nan'), None), (float('inf'), None),
                             (float('-inf'), None), ('bad', None), (.01, 'bad')]:
            with self.subTest(cost=cost, tokens=tokens), tempfile.TemporaryDirectory() as d:
                backend = Backend(cost, tokens)
                with self.assertRaises(BudgetExceeded):
                    await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
                state = json.loads((Path(d) / 'rule-units-state.private.json').read_text())
                self.assertTrue(state['budget_stop'])
                self.assertNotIn('accounting', state['attempts'][0])
                with self.assertRaises(BudgetExceeded):
                    await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
                self.assertEqual(backend.calls, 1)

    async def test_unknown_expression_remains_unresolved(self):
        value=candidate('u1')
        value['clause']['expression']=dict(type='unknown', source_text='Rule Alpha')
        with tempfile.TemporaryDirectory() as d:
            out=await ext.run(d,DOC,PLAN,backend=ScriptedBackend({'*':[value,unknown('u2')]}),**ARGS)
            self.assertEqual(out['unresolved_count'],2)
            self.assertIn('unknown_expression',out['units'][0]['review_flags'])
            self.assertFalse(out['units'][0]['accepted'])

    async def test_schema_and_cache_integrity(self):
        schema=json.dumps(ext.Response.model_json_schema())
        for keyword in ['"uniqueItems"','"minItems"','"maxItems"','"allOf"','"if"','"then"']:
            self.assertNotIn(keyword,schema)
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
            result=await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            self.assertEqual(result['unresolved_count'],2)
            path=Path(d)/'rule-units-state.private.json'; state=json.loads(path.read_text())
            state['successes']['u1']['output']['unresolved_reason']='altered'; path.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError,'hash mismatch'): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            self.assertEqual(len(backend.calls),2)

class IntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def test_resealed_structural_corruption_and_unsealed_deletion(self):
        def bad_attempt(s): s['attempts'][0]['unit_id'] = 'unknown'
        def bad_request(s): s['attempts'][0]['request_sha256'] = '0' * 64
        def bad_charge(s): s['attempts'][0]['charged_usd'] = float('nan')
        def bad_reservation(s): s['attempts'][0]['reserved_usd'] = 0
        def bad_status(s): s['attempts'][0]['status'] = 'mystery'
        def bad_account(s): s['attempts'][0]['accounting']['input_tokens'] = -1
        def bad_success(s): s['successes']['u1']['request_sha256'] = 'x'
        def bad_output(s): s['successes']['u1']['output']['unit_id'] = 'u2'
        def bad_extra(s): s['unexpected'] = 1
        def bad_context(s): s['context']['plan']['units'][0]['label'] = 'altered'
        def bad_unknown_success(s): s['successes']['other'] = s['successes']['u1']
        def bad_bijection(s): del s['successes']['u1']
        def bad_stop(s): s['budget_stop'] = False
        for mutate in (bad_attempt, bad_request, bad_charge, bad_reservation, bad_status, bad_account, bad_success, bad_output, bad_extra, bad_context, bad_unknown_success, bad_bijection, bad_stop):
            with self.subTest(mutate=mutate.__name__), tempfile.TemporaryDirectory() as d:
                backend = ScriptedBackend({'*': [unknown('u1'), unknown('u2')]})
                await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
                path = Path(d)/'rule-units-state.private.json'; state = json.loads(path.read_text())
                mutate(state)
                path.write_text(json.dumps(state))
                if mutate != bad_charge:
                    (Path(d)/'rule-units-seal.private.json').write_text(json.dumps({'sha256':ext.digest(state)}))
                with self.assertRaises((ValueError, TypeError)):
                    await ext.run(d, DOC, PLAN, backend=backend, **ARGS)
                self.assertEqual(len(backend.calls), 2)
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
            await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            path=Path(d)/'rule-units-state.private.json'; state=json.loads(path.read_text())
            state['attempts'].pop(); path.write_text(json.dumps(state))
            with self.assertRaises(ValueError): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            self.assertEqual(len(backend.calls),2)
        for name in ('rule-units-state.private.json', 'rule-units-seal.private.json'):
            with tempfile.TemporaryDirectory() as d:
                backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
                await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                (Path(d)/name).unlink()
                with self.assertRaises(ValueError): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                self.assertEqual(len(backend.calls),2)

    async def test_reservation_and_failed_writes_prevent_redispatch(self):
        for fail_name, occurrence in [('rule-units-state.private.json', 3), ('rule-units-seal.private.json', 3), ('rule-units-candidates.private.json', 2)]:
            with self.subTest(fail_name=fail_name), tempfile.TemporaryDirectory() as d:
                backend=ScriptedBackend({'*':[unknown('u1'), unknown('u2')]})
                real = ext._write; hits = 0
                def faulty(path, value, policy):
                    nonlocal hits
                    if path.name == fail_name:
                        hits += 1
                        if hits == occurrence: raise OSError('injected')
                    return real(path, value, policy)
                with patch.object(ext, '_write', side_effect=faulty):
                    with self.assertRaises(OSError): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                self.assertEqual(len(backend.calls),1)
                if fail_name == 'rule-units-candidates.private.json':
                    # The response and seal were durable; replay safely continues with the next unit.
                    await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                    self.assertEqual(len(backend.calls),2)
                else:
                    with self.assertRaises((ValueError, BudgetExceeded)): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
                    self.assertEqual(len(backend.calls),1)

    async def test_private_permissions_and_symlinks(self):
        with tempfile.TemporaryDirectory() as parent:
            d=Path(parent)/'run'; old=os.umask(0)
            try: await ext.run(d,DOC,PLAN,backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]}),**ARGS)
            finally: os.umask(old)
            self.assertEqual(d.stat().st_mode & 0o777,0o700)
            for path in d.iterdir(): self.assertEqual(path.stat().st_mode & 0o777,0o600)
        with tempfile.TemporaryDirectory() as d:
            os.chmod(d,0o755)
            with self.assertRaises(ValueError): await ext.run(d,DOC,PLAN,backend=ScriptedBackend({}),**ARGS)
        for name in ('rule-units.lock','rule-units-state.private.json','rule-units-seal.private.json','rule-units-candidates.private.json'):
            with tempfile.TemporaryDirectory() as d:
                (Path(d)/name).symlink_to('/tmp/nonexistent-rule-file')
                with self.assertRaises(ValueError): await ext.run(d,DOC,PLAN,backend=ScriptedBackend({}),**ARGS)
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'target'; target.mkdir(mode=0o700); (Path(d)/'link').symlink_to(target)
            with self.assertRaises(ValueError): await ext.run(Path(d)/'link',DOC,PLAN,backend=ScriptedBackend({}),**ARGS)

    async def test_preflight_settings_bytes_and_context_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
            await ext.run(d,{**DOC,'doc_id':'one','url':'https://example.test/'},PLAN,backend=backend,**ARGS)
            files={p.name:p.read_bytes() for p in Path(d).iterdir()}
            for doc,args in [({**DOC,'doc_id':'two','url':'https://example.test/'},ARGS), (DOC,{**ARGS,'settings':{'output_type':'bad'}}), (DOC,{**ARGS,'settings':{'temperature':float('nan')}})]:
                with self.assertRaises(ValueError): await ext.run(d,doc,PLAN,backend=backend,**args)
                self.assertEqual(files,{p.name:p.read_bytes() for p in Path(d).iterdir()})
            out=json.loads((Path(d)/'rule-units-candidates.private.json').read_text())
            self.assertEqual(out['provenance']['doc_id'],'one')
        text='é Rule Alpha'; h=ext.sha(text)
        doc=dict(text=text,text_sha256=h,body_sha256='a'*64)
        plan=dict(source_text_sha256=h,units=[PLAN['units'][0]])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): await ext.run(d,doc,plan,backend=ScriptedBackend({}),**{**ARGS,'max_source_bytes':len(text)})
            self.assertEqual(list(Path(d).iterdir()),[])
            out=await ext.run(d,doc,plan,backend=ScriptedBackend({'*':[unknown('u1')]}),**{**ARGS,'max_source_bytes':len(text.encode())})
            self.assertEqual(out['units'][0]['status'],'succeeded')

    async def test_interrupted_reservation_and_packet_rebuild(self):
        with tempfile.TemporaryDirectory() as d:
            backend=ScriptedBackend({'*':[RuntimeError('interrupted')]})
            with self.assertRaises(RuntimeError): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            state_path=Path(d)/'rule-units-state.private.json'
            state=json.loads(state_path.read_text()); attempt=state['attempts'][0]
            attempt.pop('error_type'); attempt['status']='reserved'
            state_path.write_text(json.dumps(state))
            (Path(d)/'rule-units-seal.private.json').write_text(json.dumps({'sha256':ext.digest(state)}))
            (Path(d)/'rule-units-candidates.private.json').write_text('corrupted derivative')
            with self.assertRaises(BudgetExceeded): await ext.run(d,DOC,PLAN,backend=backend,**ARGS)
            packet=json.loads((Path(d)/'rule-units-candidates.private.json').read_text())
            self.assertEqual([u['status'] for u in packet['units']],['reserved','not_attempted'])
            self.assertEqual(len(backend.calls),1)

    async def test_storage_policy_bounds(self):
        from private_run_storage import PrivateRunStorage
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as other:
            policy=PrivateRunStorage(root, 1000000)
            backend=ScriptedBackend({'*':[unknown('u1'),unknown('u2')]})
            with self.assertRaises(ValueError): await ext.run(other,DOC,PLAN,backend=backend,storage_policy=policy,**ARGS)
            self.assertEqual(len(backend.calls),0)
            path=Path(root)/'workspace'
            await ext.run(path,DOC,PLAN,backend=backend,storage_policy=policy,**ARGS)
            state=json.loads((path/'rule-units-state.private.json').read_text())
            self.assertEqual(state['context']['storage_policy'],policy.describe())

    async def test_mixed_charges_and_failed_reservation_at_dollar_cap(self):
        text=TEXT+' Rule Gamma applies.'; h=ext.sha(text)
        doc={**DOC,'text':text,'text_sha256':h}
        plan={'source_text_sha256':h,'units':PLAN['units']+[dict(unit_id='u3',anchor_quote='Rule Gamma',label='Third',instruction='Extract this unit')]}
        class Backend:
            def __init__(self): self.calls=0
            async def generate(self,**kwargs):
                self.calls+=1
                if self.calls==3: raise RuntimeError('failed request')
                return SimpleNamespace(model='scripted:fake',priced=True,cost_usd=.04 if self.calls==1 else 0,
                                       input_tokens=0,output_tokens=0,output=ext.Response.model_validate(unknown('u'+str(self.calls))))
        with tempfile.TemporaryDirectory() as d:
            backend=Backend(); args={**ARGS,'max_usd':.14,'reservation_usd':.1}
            with self.assertRaises(RuntimeError): await ext.run(d,doc,plan,backend=backend,**args)
            with self.assertRaises(BudgetExceeded): await ext.run(d,doc,plan,backend=backend,**args)
            state=json.loads((Path(d)/'rule-units-state.private.json').read_text())
            self.assertEqual([a.get('charged_usd',a['reserved_usd']) for a in state['attempts']],[.04,0,.1])
            self.assertEqual(backend.calls,3)

    async def test_partial_packet_and_mixed_budget(self):
        class Backend:
            def __init__(self): self.calls=0
            async def generate(self,**kw):
                self.calls+=1
                if self.calls==2: raise RuntimeError('failure')
                return SimpleNamespace(model='scripted:fake',priced=True,cost_usd=0, input_tokens=0,output_tokens=0,output=ext.Response.model_validate(unknown('u1')))
        with tempfile.TemporaryDirectory() as d:
            backend=Backend(); args={**ARGS,'max_usd':.1,'reservation_usd':.1}
            with self.assertRaises(RuntimeError): await ext.run(d,DOC,PLAN,backend=backend,**args)
            with self.assertRaises(BudgetExceeded): await ext.run(d,DOC,PLAN,backend=backend,**args)
            out=json.loads((Path(d)/'rule-units-candidates.private.json').read_text())
            self.assertEqual([u['status'] for u in out['units']],['succeeded','failed'])
            self.assertEqual(backend.calls,2)

if __name__ == '__main__': unittest.main()
