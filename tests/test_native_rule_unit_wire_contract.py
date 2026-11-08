import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import httpx2
import extract_rule_units as rules
from native_rule_unit_wire_contract import ENDPOINT, PROFILE, endpoint_contract, compare_frozen_request


class EndpointTests(unittest.TestCase):
    def test_fixed_endpoint_only(self):
        for url, method, valid in [
            ('https://api.openai.com/v1/responses','POST',True),
            ('https://api.openai.com:443/v1/responses','POST',True),
            ('https://api.openai.com/v1/responses?key=secret','POST',False),
            ('https://api.openai.com/v1/%72esponses','POST',False),
            ('https://api.openai.com/v1/responses/','POST',False),
            ('https://u:p@api.openai.com/v1/responses','POST',False),
            ('https://api.openai.com:444/v1/responses','POST',False),
            ('http://api.openai.com/v1/responses','POST',False),
            ('https://api.openai.com.evil.test/v1/responses','POST',False),
            ('https://api.openai.com/v1/responses','GET',False)]:
            with self.subTest(url=url,method=method):
                self.assertEqual(endpoint_contract(httpx2.Request(method,url)), ENDPOINT if valid else None)


class CaptureTests(unittest.IsolatedAsyncioTestCase):
    async def test_normalized_address_at_mock_transport_boundary(self):
        observed = []
        def handler(request):
            observed.append((str(request.url), request.url.userinfo,
                             request.url.port, request.url.raw_path,
                             endpoint_contract(request)))
            return httpx2.Response(200)

        async with httpx2.AsyncClient(transport=httpx2.MockTransport(handler)) as client:
            for url in ('https://api.openai.com/v1/responses',
                        'https://@api.openai.com/v1/responses',
                        'https://API.OPENAI.COM:443/v1/responses',
                        'https://api.openai.com/v1/responses?'):
                await client.post(url)
        normalized = ('https://api.openai.com/v1/responses', b'', None,
                      b'/v1/responses', ENDPOINT)
        self.assertEqual(observed[:3], [normalized] * 3)
        self.assertEqual(observed[3][1:], (b'', None, b'/v1/responses?', None))

    async def test_identifier_and_unknown_are_recorded_without_url_secrets_and_cap_persists(self):
        from controlled_model_transport import ControlledModelTransport
        from bc_core.budget import BudgetExceeded
        with tempfile.TemporaryDirectory() as tmp:
            audit = ControlledModelTransport(tmp, max_requests=2, context_sha256='a'*64)
            async with audit.client_factory(None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))) as client:
                await client.post('https://api.openai.com/v1/responses', json={})
                await client.post('https://u:secret@api.openai.com/hidden?token=secret', json={})
                with self.assertRaises(BudgetExceeded):
                    await client.post('https://api.openai.com/v1/responses', json={})
            rows = [json.loads(x) for x in audit.ledger.read_text().splitlines()]
            self.assertEqual(rows[0]['endpoint_contract'], ENDPOINT)
            self.assertNotIn('endpoint_contract', rows[2])
            self.assertNotIn('secret', audit.ledger.read_text())
            self.assertNotIn('hidden', audit.ledger.read_text())
            reopened = ControlledModelTransport(tmp, max_requests=2, context_sha256='a'*64)
            async with reopened.client_factory(None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))) as client:
                with self.assertRaises(BudgetExceeded):
                    await client.post('https://api.openai.com/v1/responses', json={})


class WireTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from openai import AsyncOpenAI
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from bc_llm import ModelSpec, RoleRegistry, PydanticAIBackend
        self.source=b'raw source'; text='A rule applies.'
        doc={'text':text,'text_sha256':rules.sha(text),'body_sha256':hashlib.sha256(self.source).hexdigest()}
        plan={'source_text_sha256':doc['text_sha256'],'units':[{'unit_id':'a','anchor_quote':'rule','label':'A','instruction':'Extract'}]}
        self.ctx=rules.prepare(doc,plan,model_identity={'model':'openai:gpt-6-sol','native_wire_profile':PROFILE},today=datetime.date(2026,11,7),max_calls=1,max_usd=1,reservation_usd=.1,max_source_bytes=1000,role='extractor',settings={},storage_policy=None)
        captured=[]
        def handler(req):
            captured.append(req.content)
            return httpx2.Response(200,json={'id':'resp_1','object':'response','created_at':0,'status':'completed','model':'gpt-6-sol','output':[{'type':'message','id':'msg_1','role':'assistant','status':'completed','content':[{'type':'output_text','text':'{"unit_id":"a","outcome":"unresolved","clause":null,"supporting_quotes":[],"unresolved_reason":"unknown"}','annotations':[]}]}], 'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2}})
        client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        sdk=AsyncOpenAI(api_key='offline-test',http_client=client,max_retries=0)
        model=OpenAIResponsesModel('gpt-6-sol',provider=OpenAIProvider(openai_client=sdk))
        backend=PydanticAIBackend(RoleRegistry(roles={'extractor':ModelSpec(model='openai:gpt-6-sol',output_mode='native')}),model_resolver=lambda _:model,max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)
        request=rules.request_for(plan['units'][0],self.ctx)
        try:
            await backend.generate(role='extractor',stage='rule_unit',prompt=request['prompt'],system=request['system'],output_type=rules.Response)
        finally:
            await backend.aclose(); await sdk.close()
        self.raw=captured[0]

    async def check(self, raw=None, ctx=None, source=None):
        return await compare_frozen_request(ctx or self.ctx,'a',self.source if source is None else source,self.raw if raw is None else raw)

    async def test_full_sdk_json_and_adversarial_mutations(self):
        self.assertTrue(await self.check())
        obj=json.loads(self.raw)
        mutations=[]
        for key, value in [('model','other'),('tools',[{'type':'web_search'}]),('temperature',True),('input',[])]:
            altered=copy.deepcopy(obj); altered[key]=value; mutations.append(altered)
        altered=copy.deepcopy(obj); altered['text']['format']['schema']['title']='mutated'; mutations.append(altered)
        for altered in mutations:
            self.assertFalse(await self.check(json.dumps(altered).encode()))
        for raw in (b'{"model":1,"model":1}',b'{"x":NaN}',b'{"x":1e999}'):
            with self.assertRaises(ValueError): await self.check(raw)

    async def test_context_source_and_unfrozen_profile_rejected(self):
        for key in ('system','schema','implementation_sha256'):
            changed=copy.deepcopy(self.ctx); changed[key]='changed'
            with self.assertRaises(ValueError): await self.check(ctx=changed)
        changed=copy.deepcopy(self.ctx); changed['settings']={'temperature':0}
        with self.assertRaises(ValueError): await self.check(ctx=changed)
        changed=copy.deepcopy(self.ctx); changed['model_identity'].pop('native_wire_profile')
        with self.assertRaises(ValueError): await self.check(ctx=changed)
        with self.assertRaises(ValueError): await self.check(source=b'other')
