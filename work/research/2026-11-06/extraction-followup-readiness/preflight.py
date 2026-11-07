import asyncio, hashlib, json, os, sys, tempfile
from pathlib import Path
from unittest.mock import patch
sdkroot=Path('/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python')
sys.path.insert(0,str(sdkroot))
sys.path.insert(0,str(Path.cwd()/'scripts'))
import bc_llm.pydantic_ai_backend as module
from bc_llm import ModelSpec, RoleRegistry, PydanticAIBackend
from bc_core.budget import BudgetExceeded
from controlled_model_transport import ControlledModelTransport
from pydantic import BaseModel
import httpx2
class Output(BaseModel):
    ok: bool
async def main():
    requests=[]
    def handler(req):
        requests.append(req)
        return httpx2.Response(503,json={'error':{'message':'offline preflight failure'}})
    with tempfile.TemporaryDirectory() as tmp:
        guard=ControlledModelTransport(tmp,max_requests=1,context_sha256='1'*64)
        def factory(proxy):
            return guard.client_factory(None,transport=httpx2.MockTransport(handler))
        registry=RoleRegistry(roles={'extractor':ModelSpec(model='openai:gpt-6-sol',output_mode='native')})
        backend=PydanticAIBackend(registry,http_client_factory=factory,max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)
        resolver=backend.model_resolver
        backend.model_resolver=lambda spec:guard.require_model(resolver(spec))
        errors=[]
        try:
            for _ in range(2):
                try:
                    await backend.generate(role='extractor',prompt='offline mock',output_type=Output)
                    raise AssertionError('mock unexpectedly succeeded')
                except Exception as exc:
                    chain=[]
                    while exc:
                        chain.append(type(exc).__name__)
                        exc=exc.__cause__
                    errors.append(chain)
            assert len(requests)==1, len(requests)
            assert 'ModelHTTPError' in errors[0],errors
            assert 'BudgetExceeded' in errors[1],errors
            assert backend._openai_client.max_retries==0
            events=[json.loads(line) for line in guard.ledger.read_text().splitlines()]
            assert [e['state'] for e in events]==['reserved','response']
            assert events[-1]['status']==503
            print(json.dumps({'schema_version':'controlled-backend-preflight-1','network':'httpx2.MockTransport only; no provider requests','backend_module':str(Path(module.__file__).resolve()),'backend_sha256':hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),'sdk_retries':backend._openai_client.max_retries,'backend_max_attempts':1,'agent_retries':0,'max_model_requests':1,'persistent_http_cap':1,'generate_invocations':2,'mock_http_requests':len(requests),'http_states':[e['state'] for e in events],'first_http_status':events[-1]['status'],'exception_chains':errors,'passed':True},indent=2))
        finally:
            await backend.aclose()
with patch.dict(os.environ,{'OPENAI_API_KEY':'offline-test-key','PYDANTIC_AI_NO_BANNER':'1'}):
    asyncio.run(main())
