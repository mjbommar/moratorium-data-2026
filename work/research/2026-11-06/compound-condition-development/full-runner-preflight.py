"""Offline real SDK/backend/bc-evidence test. Never contacts a provider."""
import asyncio
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=['/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python',str(ROOT/'scripts')]
from bc_llm import ModelSpec,RoleRegistry,PydanticAIBackend,PricingTable
from bc_core.budget import BudgetExceeded
import httpx2
import extract_domain_candidates as domain
from controlled_model_transport import ControlledModelTransport

TEXT='Synthetic proposal: either aggregate capacity or aggregate demand is at least 25 MW.'
def threshold(basis):
    return dict(type='threshold',operator='ge',value=25,unit='MW',measurement_basis=basis,aggregation_rule='aggregate',scope='synthetic facility')
CLAUSE=dict(purpose='prohibition_trigger',assertion_context='proposed',source_text=TEXT,
            expression=dict(type='any',members=[threshold('capacity'),threshold('demand')]))
FACT=dict(target_table='measure_provisions',target_field='condition_clauses',subject_label='Synthetic proposal',value=[CLAUSE],quote=TEXT,assertion_context='proposed',supporting_passages=[])
OUTPUT=dict(relevance=1,summary='',claims=[dict(text='Synthetic condition',quote=TEXT,cells=[0],facts=[FACT])],unresolved_fields=[])

def response():
    return dict(id='resp_mock',object='response',created_at=0,status='completed',model='gpt-6-sol',
                output=[dict(type='message',id='msg_mock',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(OUTPUT),annotations=[])])],
                usage=dict(input_tokens=10,output_tokens=5,total_tokens=15))

def inputs():
    return dict(doc=dict(doc_id='synthetic',text=TEXT,title='Synthetic',final_url=None,url='https://fixture.invalid/proposal',published=None,language='en',body_sha256=hashlib.sha256(TEXT.encode()).hexdigest(),text_sha256=hashlib.sha256(TEXT.encode()).hexdigest()),
                cells=[dict(cell_id='synthetic',subject_label='Synthetic',topic_label='conditions',prospective=False,window_start='2026-01-01',window_end='2026-11-05')],
                question='Extract synthetic source only.',today=dt.date(2026,11,5),max_calls=1,
                model_identity={'model':'openai:gpt-6-sol','pricing':'synthetic fixture rates; no provider spend'},
                budget_policy=dict(max_usd=0.5,reservation_usd=0.5))

def backend(audit,handler):
    spec=ModelSpec(model='openai:gpt-6-sol',output_mode='native',max_tokens=6000,timeout_s=5)
    result=PydanticAIBackend(RoleRegistry(roles={'extractor':spec}),
        pricing=PricingTable({'openai:gpt-6-sol':{'input':1.0,'output':2.0}}),
        http_client_factory=lambda _:audit.client_factory(None,transport=httpx2.MockTransport(handler)),
        max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)
    resolve=result.model_resolver
    result.model_resolver=lambda requested:audit.require_model(resolve(requested))
    result.model_resolver(spec) # No HTTP; enforce actual SDK and controlled client.
    return result

async def main():
    outcomes=[]
    for mode in ('success','failure'):
        requests=[]
        def handler(request):
            requests.append(request)
            return httpx2.Response(200,json=response()) if mode=='success' else httpx2.Response(503,json={'error':{'message':'synthetic failure'}})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);http=root/'http';http.mkdir()
            audit=ControlledModelTransport(http,max_requests=1,context_sha256='2'*64)
            run=root/'run'
            b=backend(audit,handler)
            try:
                if mode=='success':
                    result=await domain.run(run,backend=b,**inputs())
                    assert result['full_text_chunk_coverage']
                    assert result['candidates'][0]['value']==[CLAUSE]
                    assert not result['candidates'][0]['field_schema_errors']
                    assert result['canonical_records_written']==0
                    assert not result['candidates'][0]['accepted']
                else:
                    try:await domain.run(run,backend=b,**inputs())
                    except Exception:pass
                    state=json.loads((run/'state.private.json').read_text())
                    assert len(state['attempts'])==1 and state['attempts'][0]['status']=='failed'
            finally:await b.aclose()
            # Reconstruct both layers against the same persistent budget/cache.
            again=ControlledModelTransport(http,max_requests=1,context_sha256='2'*64)
            b=backend(again,handler)
            try:
                if mode=='success':
                    assert await domain.run(run,backend=b,**inputs())==result
                    # A different extraction workspace still cannot refill HTTP.
                    try:await domain.run(root/'another-run',backend=b,**inputs())
                    except BudgetExceeded:pass
                    else:raise AssertionError('HTTP cap not enforced')
                else:
                    try:await domain.run(run,backend=b,**inputs())
                    except BudgetExceeded:pass
                    else:raise AssertionError('Adapter request cap not enforced')
                assert len(requests)==1
                events=[json.loads(s) for s in audit.ledger.read_text().splitlines()]
                assert [r['state'] for r in events]==['reserved','response']
                outcomes.append(dict(scenario=mode,mock_http_requests=1,reconstructed_backend=True,persistent_caps_verified=True,cache_replay_without_http=(mode=='success')))
            finally:await b.aclose()
    print(json.dumps(dict(schema_version='controlled-domain-runner-preflight-1',provider_requests=0,transport='httpx2.MockTransport only',scenarios=outcomes,passed=True),indent=2))

if __name__=='__main__':
    with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test','PYDANTIC_AI_NO_BANNER':'1'}):asyncio.run(main())
