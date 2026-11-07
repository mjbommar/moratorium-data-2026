#!/usr/bin/env python3
"""Exercise all reviewed units through actual SDK and offline HTTP only."""
import asyncio, datetime, hashlib, json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PRIVATE=Path('/data0/moratorium-refresh-2026/direct-rule-unit-evaluation-2026-11-07/preparation')
sys.path[:0]=['/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python',str(ROOT/'scripts')]
import httpx2
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from bc_llm import ModelSpec,PydanticAIBackend,RoleRegistry
from bc_llm.pricing import PricingTable
from controlled_model_transport import ControlledModelTransport
from private_run_storage import PrivateRunStorage
import extract_rule_units as rules

async def main():
    prior=json.loads((ROOT/'work/research/2026-11-07/compound-contract-evaluation/protocol.json').read_bytes())
    plans={f:json.loads((PRIVATE/(f+'-adapter-plan.private.json')).read_bytes()) for f in ('mandan','harwood')}
    queue=[(family,u['unit_id']) for family in plans for u in plans[family]['units']]
    requests=[]
    def handler(request):
        body=json.loads(request.content)
        assert body['text']['format']['type']=='json_schema'
        family,uid=queue[len(requests)]
        assert uid in json.dumps(body)
        requests.append(uid)
        value=dict(unit_id=uid,outcome='unresolved',clause=None,supporting_quotes=[],unresolved_reason='Offline synthetic unresolved')
        return httpx2.Response(200,json=dict(id='resp_offline',object='response',created_at=0,status='completed',model='gpt-6-sol',output=[dict(type='message',id='msg_offline',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(value),annotations=[])])],usage=dict(input_tokens=100,output_tokens=50,total_tokens=150)))
    with tempfile.TemporaryDirectory(dir=PRIVATE) as temp:
        root=Path(temp); policy=PrivateRunStorage(root,128*1024*1024)
        http=root/'http';http.mkdir(mode=0o700)
        transport=ControlledModelTransport(http,max_requests=86,context_sha256='b'*64,storage_policy=policy)
        client=transport.client_factory(None,transport=httpx2.MockTransport(handler))
        sdk=AsyncOpenAI(api_key='offline-test',http_client=client,max_retries=0)
        model=OpenAIResponsesModel('gpt-6-sol',provider=OpenAIProvider(openai_client=sdk));transport.require_model(model)
        spec=ModelSpec(model='openai:gpt-6-sol',reasoning_effort='low',output_mode='native',max_tokens=14000,timeout_s=120)
        backend=PydanticAIBackend(RoleRegistry(roles={'extractor':spec}),model_resolver=lambda _:model,pricing=PricingTable({'openai:gpt-6-sol':{'input':2,'output':10}}),max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)
        results=[]
        try:
            for family,cap in [('mandan',20),('harwood',66)]:
                c=next(c for c in prior['cases'] if c['family']==family)
                text=Path(c['text_path']).read_text()
                doc=dict(text=text,text_sha256=c['text_sha256'],body_sha256=c['body_sha256'])
                args=dict(backend=backend,model_identity={'model':'openai:gpt-6-sol'},today=datetime.date(2026,11,5),max_calls=cap,max_usd=cap*.75,reservation_usd=.75,max_source_bytes=200000,settings={},storage_policy=policy)
                first=await rules.run(root/family,doc,plans[family],**args)
                before=len(requests)
                replay=await rules.run(root/family,doc,plans[family],**args)
                assert first==replay and len(requests)==before and first['planned_count']==cap and first['unresolved_count']==cap and first['candidate_count']==0
                results.append(dict(case_id=family+'-direct',planned=cap,unresolved=first['unresolved_count'],replay_extra_calls=len(requests)-before))
            events=[json.loads(line) for line in transport.ledger.read_text().splitlines()]
            reservations=sum(e['state']=='reserved' for e in events)
            assert len(requests)==reservations==86
            return dict(provider_calls=0,mock_http_requests=len(requests),http_reservations=reservations,cases=results,quality_gate='must fail: all units unresolved',note='Adapter/SDK integration fixture only; no experiment auditor exercised.')
        finally:
            await backend.aclose();await sdk.close()

if __name__=='__main__':
    result=asyncio.run(main())
    (HERE/'offline-validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
