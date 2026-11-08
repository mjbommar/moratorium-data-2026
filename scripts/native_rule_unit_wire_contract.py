"""Offline, explicitly frozen native Responses request contract; no network access."""
import datetime
import hashlib
import importlib
from pathlib import Path
import re

ENDPOINT = 'openai-official-responses-https-1'
PROFILE = 'native-rule-unit-default-spec-offline-1'
# Hash every Python source file in each pinned import tree, including bc-llm.
PINNED = {
    'pydantic_ai': 'b9ff199164a0730ff58ef2ae5ad8e4bf543424be1b4fc67df42d9c48cb3e4809',
    'openai': 'c33397064460b328124935a8f4030b1ed9bf652d7431856999d8704e6e2ebe58',
    'httpx2': 'a0c10ff50c21a1a2f4b668f4fc3a1a12094c680237ea96ad98942191570a3f87',
    'pydantic': 'e6dbc0e3ff0909e837c3f9c797b24644c3f7ec87895208b010c53352e1d38de1',
    'pydantic_core': 'baee6eeac4faf219fe322057191445e1bbc100c8a292ad0bb6e7728e0d5267ea',
    'bc_llm': '6a9513fb3f1c282910bdd8735335270b82800a42a4ea2e13667cd02165c6b6e1',
}


def endpoint_contract(request):
    """Identify a normalized request address, not its original spelling or provider.

    Empty normalized userinfo does not prove the input lacked an ``@``.
    Return only a fixed identifier, never an arbitrary URL component.
    """
    u = request.url
    if (request.method == 'POST' and u.scheme == 'https' and u.host == 'api.openai.com'
            and u.port is None and u.raw_path == b'/v1/responses' and not u.userinfo):
        return ENDPOINT
    return None


def check_pins():
    for name, expected in PINNED.items():
        root = Path(importlib.import_module(name).__file__).resolve().parent
        h = hashlib.sha256()
        for f in sorted(root.rglob('*')):
            if f.is_file() and (f.suffix == '.py' or (name == 'pydantic_core' and f.suffix == '.so')):
                h.update(str(f.relative_to(root)).encode() + b'\0' + hashlib.sha256(f.read_bytes()).digest())
        if h.hexdigest() != expected:
            raise ValueError('unsupported SDK source pin: ' + name)


async def compare_frozen_request(context, unit_id, source_bytes, observed_bytes):
    """Compare complete typed JSON against an offline SDK serialization.

    PROFILE explicitly fixes default ModelSpec with native output, no per-call
    settings or tools, no retries and the pinned source trees. It must be in
    the frozen model identity before dispatch; it cannot be inferred afterward.
    Returns a boolean; unsupported or invalid context raises ValueError.
    """
    import extract_rule_units as rules
    from native_rule_unit_journal_adapter import same_json, strict_json
    identity = context.get('model_identity', {})
    if (not isinstance(identity, dict) or set(identity) != {'model', 'native_wire_profile'}
            or identity.get('native_wire_profile') != PROFILE
            or not isinstance(identity.get('model'), str)
            or not re.fullmatch(r'openai:[A-Za-z0-9][A-Za-z0-9._-]*', identity['model'])
            or context.get('settings') != {}):
        raise ValueError('missing or unsupported frozen native model spec/profile/settings')
    rebuilt = rules.prepare(context['document'], context['plan'], model_identity=identity,
        today=datetime.date.fromisoformat(context['today']), max_calls=context['max_calls'],
        max_usd=context['max_usd'], reservation_usd=context['reservation_usd'],
        max_source_bytes=context['max_source_bytes'], role=context['role'], settings=context['settings'],
        storage_policy=None)
    rebuilt['storage_policy'] = context['storage_policy']
    if not same_json(rebuilt, context):
        raise ValueError('frozen context or extractor implementation mismatch')
    if hashlib.sha256(source_bytes).hexdigest() != context['document']['body_sha256']:
        raise ValueError('source body mismatch')
    units = [u for u in context['plan']['units'] if u['unit_id'] == unit_id]
    if len(units) != 1:
        raise ValueError('unknown unit')
    check_pins()
    import httpx2
    from openai import AsyncOpenAI
    from pydantic_ai.models.openai import OpenAIResponsesModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from bc_llm import ModelSpec, RoleRegistry, PydanticAIBackend
    captured = []
    def handler(request):
        if endpoint_contract(request) != ENDPOINT:
            raise ValueError('offline serializer endpoint mismatch')
        captured.append(request.content)
        return httpx2.Response(200, json={'id':'resp_offline','object':'response','created_at':0,
            'status':'completed','model':identity['model'].split(':',1)[1], 'output':[{'type':'message',
            'id':'msg_offline','role':'assistant','status':'completed','content':[{'type':'output_text',
            'text': '{"unit_id":"offline","outcome":"unresolved","clause":null,"supporting_quotes":[],"unresolved_reason":"offline"}', 'annotations':[]}]}],
            'usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}})
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler), follow_redirects=False)
    sdk = AsyncOpenAI(api_key='offline-dummy-credential', http_client=client, max_retries=0)
    spec = ModelSpec(model=identity['model'], output_mode='native')
    model = OpenAIResponsesModel(spec.model_name, provider=OpenAIProvider(openai_client=sdk))
    backend = PydanticAIBackend(RoleRegistry(roles={context['role']:spec}), model_resolver=lambda _:model,
        max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False)
    request = rules.request_for(units[0], context)
    try:
        await backend.generate(role=context['role'], stage='rule_unit', prompt=request['prompt'],
                               system=request['system'], output_type=rules.Response)
    finally:
        await backend.aclose()
        await sdk.close()
    if len(captured) != 1:
        raise ValueError('offline serializer request cardinality unsupported')
    return same_json(strict_json(captured[0]), strict_json(observed_bytes))
