import asyncio
import copy
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import httpx
from bc_web.settings import BcWebSettings
from bc_web.search import Searcher
import test_search_refresh_batch as fixtures
import search_refresh_batch as batch
import research_client


def setup_contract(root, plan, settings):
    contract = {'schema_version':'refresh-priced-budget-1', 'plan_sha256':batch.preview(plan)['plan_sha256'],
                'runtime':batch.runtime_fingerprint(), 'settings_sha256':batch.settings_fingerprint(settings),
                'plan_caps':plan['caps'], 'max_usd':25, 'hold_usd':.02, 'search_attempts':1200,
                'llm_calls':0, 'fetch_attempts':500, 'browser_attempts':20, 'browser_contexts':2,
                'prices':{'exa_auto_le_10_usd':.007, 'serpapi_allocated_usd':.01}}
    path=root/'contract.json'; path.write_text(json.dumps(contract))
    return path, batch.sha(path.read_bytes()), contract


def priced_plan():
    p=fixtures.plan(); p['allow_unpriced']=False
    return p


def settings():
    return BcWebSettings(exa_api_key='secret-a', serpapi_api_key='secret-b',
                         serpapi_cost_per_search=.01, serpapi_rate_per_hour=3600000)


class BudgetTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_fetches_compete_for_one_remaining_slot_after_valid_seal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = priced_plan()
            path, digest, _ = setup_contract(root, plan, settings())
            run = root/'run'
            await batch.execute(plan, run, settings=settings(),
                transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'results':[], 'organic_results':[]})),
                budget_path=path, budget_sha256=digest)
            with (run/'attempts.private.jsonl').open('a') as stream:
                for _ in range(499):
                    stream.write(json.dumps({'state':'reserved', 'kind':'fetch', 'intent':{'mode':'http'}})+'\n')
            def attempt(index):
                try:
                    research_client.reserve(run, 'fetch', intent={'mode':'http', 'url':f'https://example.org/{index}'})
                    return 'admitted'
                except RuntimeError:
                    return 'rejected'
            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(sorted(pool.map(attempt, (1, 2))), ['admitted', 'rejected'])

    async def test_fetch_rejects_interrupted_seal_and_changed_search_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = priced_plan()
            path, digest, _ = setup_contract(root, plan, settings())
            run = root/'run'
            await batch.execute(plan, run, settings=settings(),
                transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'results':[], 'organic_results':[]})),
                budget_path=path, budget_sha256=digest)
            seal = run/'completed.private.json'
            valid_seal = seal.read_bytes()
            ledger = run/'attempts.private.jsonl'
            valid_ledger = ledger.read_bytes()
            for invalid in (b'', b'{}', b'{"result_sha256":"wrong"}'):
                seal.write_bytes(invalid)
                with self.assertRaises((ValueError, KeyError)):
                    research_client.reserve(run, 'fetch', intent={'mode':'http', 'url':'https://example.org'})
                self.assertEqual(ledger.read_bytes(), valid_ledger)
            seal.write_bytes(valid_seal)
            payload = next(run.glob('*-response-*.private.body'))
            valid_payload = payload.read_bytes()
            payload.write_bytes(valid_payload + b' ')
            with self.assertRaisesRegex(ValueError, 'artifact drift'):
                research_client.reserve(run, 'fetch', intent={'mode':'http', 'url':'https://example.org'})
            self.assertEqual(ledger.read_bytes(), valid_ledger)
            payload.write_bytes(valid_payload)
            attempt = research_client.reserve(run, 'fetch', intent={'mode':'http', 'url':'https://example.org'})
            research_client.finish(run, attempt, outcome='response')
            self.assertTrue(batch.verify_completed_search(run))

    async def test_observed_cost_above_hold_stops_next_cell(self):
        p=priced_plan(); c=copy.deepcopy(p['cells'][0]); c.update(id='next',intent='next'); p['cells'].append(c)
        p['caps'].update(exa=2,serpapi=2,search_total=4)
        calls=[]
        def handler(request):
            calls.append(request)
            return (httpx.Response(200,json={'results':[],'costDollars':{'total':.03}})
                    if request.url.host=='api.exa.ai' else httpx.Response(200,json={'organic_results':[]}))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path,digest,_=setup_contract(root,p,settings())
            with self.assertRaisesRegex(RuntimeError,'exceeds reserved hold'):
                await batch.execute(p,root/'run',settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)
            self.assertEqual(len(calls),2)

    async def test_cross_cell_shared_searcher_meter_and_limiter_with_holds(self):
        p=priced_plan(); c=copy.deepcopy(p['cells'][0]); c.update(id='second',intent='second'); p['cells'].append(c)
        p['caps'].update(exa=2,serpapi=2,search_total=4)
        seen=[]; calls=[]; original=Searcher._metered
        async def instrument(self, backend, query):
            b=self.backend(backend); seen.append((id(self),id(self.meter),backend,id(b),id(b._limiter)))
            return await original(self,backend,query)
        def handler(request):
            calls.append(request)
            events=[json.loads(x) for x in (root/'run/attempts.private.jsonl').read_text().splitlines()]
            self.assertGreaterEqual(sum(x['state']=='reserved' for x in events),len(calls))
            if request.url.host=='api.exa.ai':
                body=json.loads(request.content); self.assertNotIn('contents',body)
                return httpx.Response(503,text='failure') if len([r for r in calls if r.url.host=='api.exa.ai'])==1 else httpx.Response(200,json={'results':[]})
            return httpx.Response(200,json={'organic_results':[]})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path,digest,_=setup_contract(root,p,settings())
            with patch.object(Searcher,'_metered',instrument):
                result=await batch.execute(p,root/'run',settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)
            self.assertEqual(len(calls),4)
            self.assertEqual(len({x[0] for x in seen}),1); self.assertEqual(len({x[1] for x in seen}),1)
            for backend in ('exa','serpapi'):
                self.assertEqual(len({(x[3],x[4]) for x in seen if x[2]==backend}),1)
            states=result['cells'][0]['coverage']['variants']
            self.assertEqual(states['exa-semantic'],'error'); self.assertEqual(states['google-exact'],'zero_hits')
            events=[json.loads(x) for x in (root/'run/attempts.private.jsonl').read_text().splitlines()]
            reserved=[x for x in events if x['state']=='reserved']; self.assertEqual(len(reserved),4)
            self.assertTrue(all(x['allocated_hold_usd']==.02 for x in reserved))
            finished=[x for x in events if x['state']=='finished']
            self.assertTrue(any(x['outcome']=='error' and x['cost_usd'] is None for x in finished))
            self.assertTrue(any(x['outcome']=='response' and x['cost_usd'] is None for x in finished))
            self.assertTrue(any(x['cost_usd']==.01 for x in finished))
            replay=await batch.execute(p,root/'run',settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)
            self.assertTrue(replay['replay']); self.assertEqual(len(calls),4)

    async def test_contract_drift_and_price_context_fail_before_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p=priced_plan(); path,digest,contract=setup_contract(root,p,settings())
            def never(request): self.fail('transport called')
            async def rejected(plan, sett, expected=digest):
                with self.assertRaises(ValueError):
                    await batch.execute(plan,root/'run',settings=sett,transport=httpx.MockTransport(never),budget_path=path,budget_sha256=expected)
                self.assertFalse((root/'run').exists())
            await rejected(p,settings(),'0'*64)
            altered=copy.deepcopy(p); altered['cells'][0]['intent']='stale'; await rejected(altered,settings())
            altered=copy.deepcopy(p); altered['cells'][0]['variants'][0]['include_highlights']=True
            path2,digest2,_=setup_contract(root,altered,settings()); await rejected(altered,settings(),digest2)
            p=priced_plan(); path,digest,contract=setup_contract(root,p,settings())
            bad=settings(); bad.serpapi_cost_per_search=None; await rejected(p,bad,digest)
            contract['runtime']['bc_modules_commit']='stale'; path.write_text(json.dumps(contract)); await rejected(p,settings(),batch.sha(path.read_bytes()))

    async def test_persistent_limits_fetch_modes_and_incomplete_conflict(self):
        p=priced_plan()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path,digest,contract=setup_contract(root,p,settings())
            def handler(request): return httpx.Response(200,json={'results':[],'organic_results':[]})
            run=root/'run'
            await batch.execute(p,run,settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)
            with self.assertRaisesRegex(RuntimeError,'cap reached'):
                research_client.reserve(run,'exa',intent={'budget_contract_sha256':digest})
            with self.assertRaisesRegex(RuntimeError,'explicit HTTP'):
                research_client.reserve(run,'fetch',intent={'mode':'auto','url':'https://example.org'})
            with self.assertRaisesRegex(RuntimeError,'prior HTTP'):
                research_client.reserve(run,'fetch',intent={'mode':'browser','url':'https://example.org'})
            http_attempt=research_client.reserve(run,'fetch',intent={'mode':'http','url':'https://example.org'})
            research_client.finish(run,http_attempt,outcome='response')
            for _ in range(20): research_client.reserve(run,'fetch',intent={'mode':'browser','url':'https://example.org'})
            with self.assertRaisesRegex(RuntimeError,'pydoll cap'):
                research_client.reserve(run,'fetch',intent={'mode':'browser','url':'https://example.org'})
            replay=await batch.execute(p,run,settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)
            self.assertTrue(replay['replay'])
            with (run/'attempts.private.jsonl').open('a') as f:
                for _ in range(479): f.write(json.dumps({'kind':'fetch','state':'reserved','intent':{'mode':'http'}})+'\n')
            with self.assertRaisesRegex(RuntimeError,'fetch cap'):
                research_client.reserve(run,'fetch',intent={'mode':'http','url':'https://other.example'})
            (run/'completed.private.json').unlink()
            with self.assertRaisesRegex(ValueError,'unfinished'):
                await batch.execute(p,run,settings=settings(),transport=httpx.MockTransport(handler),budget_path=path,budget_sha256=digest)

    async def test_money_and_search_caps_rebuilt_under_lock(self):
        p=priced_plan(); p['caps'].update(exa=1200,serpapi=1,search_total=1200)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); path,digest,c=setup_contract(root,p,settings()); run=root/'run'; run.mkdir()
            (run/'budget-contract.private.json').write_bytes(path.read_bytes()); batch.save(run/'plan.private.json',p)
            phase={'contract_sha256':digest,**{k:c[k] for k in ('max_usd','hold_usd','search_attempts','browser_attempts')}}
            batch.save(run/'client-config.json',{'caps':{**p['caps'],'fetch':500},'priced_phase':phase})
            ledger=run/'attempts.private.jsonl'
            def seed(n): ledger.write_text(''.join(json.dumps({'kind':'exa','state':'reserved','allocated_hold_usd':.02})+'\n' for _ in range(n)))
            seed(1200)
            with self.assertRaises(Exception): research_client.reserve(run,'exa',intent={'budget_contract_sha256':digest})
            # Independent money gate even if a future phase has a lower remaining envelope.
            seed(1250)
            with self.assertRaisesRegex(Exception,'budget'): research_client.reserve(run,'exa',intent={'budget_contract_sha256':digest})
