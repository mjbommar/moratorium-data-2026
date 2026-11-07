import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bc_core.budget import BudgetExceeded
from bc_llm.backend import ScriptedBackend

spec = importlib.util.spec_from_file_location('resumable', Path(__file__).resolve().parents[1]
                                             / 'scripts/extract_document_resumable.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class ExtractionTests(unittest.IsolatedAsyncioTestCase):
    def inputs(self):
        return dict(doc=dict(doc_id='synthetic', text=('A public proposal. ' * 900),
                             title='Fixture', final_url=None, url='https://example.invalid',
                             published=None, language='en'),
                    cells=[dict(cell_id='c1', subject_label='Fixture', topic_label='Proposal',
                                prospective=False, window_start='2026-01-01',
                                window_end='2026-11-05')],
                    model_identity={'model': 'scripted:fake', 'effort': None},
                    question='What does this proposal say?', today=dt.date(2026, 11, 5),
                    max_calls=10)

    def backend(self):
        return ScriptedBackend({'*': lambda *args: dict(relevance=0, summary='', claims=[])})

    async def test_complete_run_and_replay_make_no_extra_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = self.backend()
            result = await adapter.run(tmp, backend=backend, **self.inputs())
            self.assertTrue(result['full_text_chunk_coverage'])
            self.assertFalse(result['domain_review_complete'])
            calls = len(backend.calls)
            self.assertGreater(calls, 1)
            self.assertEqual(result, await adapter.run(tmp, backend=backend, **self.inputs()))
            self.assertEqual(calls, len(backend.calls))

    async def test_explicit_policy_requires_support_and_pins_cache_context(self):
        import inspect
        import bc_evidence.extract as native
        with tempfile.TemporaryDirectory() as tmp:
            backend=self.backend()
            if 'chunk_size' not in inspect.signature(native.extract_document).parameters:
                with self.assertRaisesRegex(ValueError,'lacks explicit chunk policy support'):
                    await adapter.run(tmp,backend=backend,chunk_size=50000,chunk_overlap=0,**self.inputs())
                self.assertFalse((Path(tmp)/'state.private.json').exists())
                self.assertEqual(len(backend.calls),0)
                return
            result=await adapter.run(tmp,backend=backend,chunk_size=50000,chunk_overlap=0,**self.inputs())
            self.assertTrue(result['full_text_chunk_coverage'])
            self.assertEqual(len(backend.calls),1)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(state['context']['chunk_policy'],dict(size=50000,overlap=0))
            self.assertEqual(len(state['chunks']),1)
            self.assertEqual(await adapter.run(tmp,backend=backend,chunk_size=50000,chunk_overlap=0,**self.inputs()),result)
            self.assertEqual(len(backend.calls),1)
            with self.assertRaises(adapter.WorkspaceContextChanged):
                await adapter.run(tmp,backend=backend,chunk_size=50001,chunk_overlap=0,**self.inputs())
            self.assertEqual(len(backend.calls),1)

    async def test_invalid_chunk_policy_stops_before_state_or_backend_calls(self):
        for size,overlap in [(True,0),(0,0),(500,True),(500,-1),(500,500),(500.5,0)]:
            with self.subTest(size=size,overlap=overlap),tempfile.TemporaryDirectory() as tmp:
                backend=self.backend()
                with self.assertRaises(ValueError):
                    await adapter.run(tmp,backend=backend,chunk_size=size,chunk_overlap=overlap,**self.inputs())
                self.assertEqual(len(backend.calls),0)
                self.assertFalse((Path(tmp)/'state.private.json').exists())

    async def test_ceiling_cannot_close_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = await adapter.run(tmp, backend=self.backend(), max_chunks=1, **self.inputs())
            self.assertFalse(result['full_text_chunk_coverage'])
            state = json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(state['status'], 'partial')
            self.assertIn('omitted_by_ceiling', [c['status'] for c in state['chunks']])

    async def test_exhausted_cap_is_persistent_and_keeps_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs = self.inputs(); inputs['max_calls'] = 1
            backend = self.backend()
            for _ in range(2):
                with self.assertRaises(BudgetExceeded):
                    await adapter.run(tmp, backend=backend, **inputs)
            self.assertEqual(len(backend.calls), 1)
            state = json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(len(state['successes']), 1)
            self.assertEqual(state['status'], 'incomplete')

    async def test_failed_reservation_consumes_cap_across_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs=self.inputs(); inputs['max_calls']=1
            backend=ScriptedBackend({'*':[BudgetExceeded('synthetic', 'llm')]})
            with self.assertRaises(BudgetExceeded):
                await adapter.run(tmp, backend=backend, **inputs)
            fresh=self.backend()
            with self.assertRaises(BudgetExceeded):
                await adapter.run(tmp, backend=fresh, **inputs)
            self.assertEqual(len(fresh.calls),0)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(state['attempts'][0]['status'],'failed')

    async def test_resume_after_partial_failure_reuses_successful_chunk(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate=dict(text='Synthetic proposal exists.',quote='A public proposal.',cells=[0])
            output=dict(relevance=1,summary='',claims=[candidate])
            first=ScriptedBackend({'*':[output,
                                       BudgetExceeded('synthetic interruption','llm')]})
            with self.assertRaises(BudgetExceeded):
                await adapter.run(tmp,backend=first,**self.inputs())
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(len(state['successes']),1)
            self.assertEqual(state['status'],'incomplete')
            self.assertFalse((Path(tmp)/'result.private.json').exists())
            saved=next(iter(state['successes'].values()))
            self.assertEqual(saved['output']['claims'][0]['text'],candidate['text'])
            fresh=ScriptedBackend({'*':lambda *args:output})
            result=await adapter.run(tmp,backend=fresh,**self.inputs())
            self.assertTrue(result['full_text_chunk_coverage'])
            self.assertFalse(result['domain_review_complete'])
            self.assertEqual(len(result['claims']),1)
            claim=result['claims'][0]
            self.assertEqual(claim['text'],candidate['text'])
            self.assertTrue(claim['verified'])
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(len(fresh.calls),len(state['chunks'])-1)
            self.assertEqual(len(state['attempts']),len(state['chunks'])+1)
            calls=len(fresh.calls)
            self.assertEqual(await adapter.run(tmp,backend=fresh,**self.inputs()),result)
            self.assertEqual(len(fresh.calls),calls)
            self.assertEqual(len(result['claims']),1)

    async def test_context_changes_and_missing_cells_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs=self.inputs()
            await adapter.run(tmp,backend=self.backend(),**inputs)
            for changed in [dict(question='Changed'),dict(model_identity={'model':'other'}),
                            dict(max_calls=11),dict(doc={**inputs['doc'],'text':'Changed text'})]:
                with self.assertRaisesRegex(ValueError,'context changed'):
                    await adapter.run(tmp,backend=self.backend(),**{**inputs,**changed})
            for cells in [[], inputs['cells']*17]:
                with self.assertRaises(ValueError):
                    await adapter.run(tmp,backend=self.backend(),**{**inputs,'cells':cells})
            with self.assertRaises(ValueError):
                await adapter.run(tmp,backend=self.backend(),
                                  **{**inputs,'doc':{**inputs['doc'],'text':'  '}})

    async def test_summary_failure_keeps_document_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            count=0
            def respond(role,prompt,output_type):
                nonlocal count
                if output_type.__name__=='_Summary':
                    raise BudgetExceeded('synthetic reduction failure','llm')
                count+=1
                return dict(relevance=1,summary=f'Chunk summary {count}',claims=[])
            with self.assertRaises(BudgetExceeded):
                await adapter.run(tmp,backend=ScriptedBackend({'*':respond}),**self.inputs())
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertTrue(all(c['status']=='succeeded' for c in state['chunks']))
            self.assertEqual(state['status'],'incomplete')
            self.assertFalse((Path(tmp)/'result.private.json').exists())

    async def test_corrupt_cache_cannot_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            await adapter.run(tmp,backend=self.backend(),**self.inputs())
            path=Path(tmp)/'state.private.json';state=json.loads(path.read_text())
            next(iter(state['successes'].values()))['output']['summary']='Tampered'
            path.write_text(json.dumps(state))
            with patch('bc_evidence.extract.CHUNK_ATTEMPTS',1):
                with self.assertRaisesRegex(ValueError,'hash mismatch'):
                    await adapter.run(tmp,backend=self.backend(),**self.inputs())
            self.assertEqual(json.loads(path.read_text())['status'],'incomplete')
            self.assertFalse((Path(tmp)/'result.private.json').exists())

    async def test_backend_model_mismatch_is_not_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs=self.inputs();inputs['model_identity']={'model':'unexpected:model'}
            with patch('bc_evidence.extract.CHUNK_ATTEMPTS',1):
                with self.assertRaisesRegex(ValueError,'unpinned model'):
                    await adapter.run(tmp,backend=self.backend(),**inputs)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertFalse(state['successes'])
            self.assertEqual(state['attempts'][0]['status'],'failed')

    async def test_dollar_reservations_persist_across_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs={**self.inputs(),'budget_policy':{'max_usd':.002,'reservation_usd':.002}}
            backend=self.backend()
            for _ in range(2):
                with self.assertRaisesRegex(BudgetExceeded,'dollar reservations'):
                    await adapter.run(tmp,backend=backend,**inputs)
            self.assertEqual(len(backend.calls),1)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(state['attempts'][0]['charged_usd'],.001)

    async def test_unpriced_call_retains_reservation_and_stops(self):
        class Unpriced(ScriptedBackend):
            async def generate(self,**kwargs):
                result=await super().generate(**kwargs)
                return result.model_copy(update={'cost_usd':None,'priced':False})
        with tempfile.TemporaryDirectory() as tmp:
            inputs={**self.inputs(),'budget_policy':{'max_usd':.01,'reservation_usd':.01}}
            backend=Unpriced({'*':lambda *a:dict(relevance=0,summary='',claims=[])})
            with self.assertRaisesRegex(BudgetExceeded,'Unpriced'):
                await adapter.run(tmp,backend=backend,**inputs)
            with self.assertRaisesRegex(BudgetExceeded,'Unpriced'):
                await adapter.run(tmp,backend=backend,**inputs)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(len(backend.calls),1)
            self.assertEqual(state['attempts'][0]['reserved_usd'],.01)
            self.assertNotIn('charged_usd',state['attempts'][0])

    async def test_overspend_is_retained_and_not_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs={**self.inputs(),'budget_policy':{'max_usd':.01,'reservation_usd':.0005}}
            with self.assertRaisesRegex(BudgetExceeded,'exceeded reservation'):
                await adapter.run(tmp,backend=self.backend(),**inputs)
            state=json.loads((Path(tmp)/'state.private.json').read_text())
            self.assertEqual(state['attempts'][0]['charged_usd'],.001)
            self.assertFalse(state['successes'])
