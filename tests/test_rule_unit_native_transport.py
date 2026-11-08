"""Exercise direct rule extraction through the real SDK with offline HTTP."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import extract_rule_units as rules
from controlled_model_transport import ControlledModelTransport
from native_rule_unit_journal_adapter import raw_output, same_json


class NativeRuleTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, fail):
        import httpx2
        from openai import AsyncOpenAI
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from bc_core.budget import BudgetExceeded
        from bc_llm import ModelSpec, PydanticAIBackend, RoleRegistry
        from bc_llm.pricing import PricingTable

        text = 'Rule Alpha applies. Rule Beta is unresolved.'
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        doc = dict(text=text, text_sha256=text_hash, body_sha256='a' * 64)
        plan = dict(source_text_sha256=text_hash, units=[
            dict(unit_id=name, anchor_quote=anchor, label=anchor, instruction='Extract this rule')
            for name, anchor in [('alpha', 'Rule Alpha'), ('beta', 'Rule Beta')]])
        requests = []

        def handler(request):
            payload = json.loads(request.content)
            requests.append(payload)
            self.assertIn(text, json.dumps(payload))
            self.assertEqual(payload['text']['format']['type'], 'json_schema')
            # NativeOutput may serialize strict=False for constrained schemas.
            # Typed post-response and canonical validation remain mandatory.
            self.assertIsInstance(payload['text']['format']['strict'], bool)
            if fail is True:
                return httpx2.Response(503, json={'error': {'message': 'offline failure'}})
            unit = ['alpha', 'beta'][len(requests) - 1]
            value = dict(unit_id=unit, outcome='unresolved', clause=None,
                         supporting_quotes=[], unresolved_reason='Source interpretation unresolved')
            if unit == 'alpha':
                value.update(outcome='candidate', unresolved_reason=None,
                             clause=dict(purpose='other', assertion_context='unknown',
                                         source_text='Rule Alpha applies.',
                                         expression=dict(type='text_predicate', text='Rule Alpha applies.')),
                             supporting_quotes=['Rule Alpha applies.'])
            if fail == 'malformed':
                value['supporting_quotes'] = 'not a list'
            return httpx2.Response(200, json=dict(
                id='resp_offline', object='response', created_at=0, status='completed',
                model='gpt-6-sol', output=[dict(type='message', id='msg_offline',
                    role='assistant', status='completed', content=[dict(
                        type='output_text', text=json.dumps(value), annotations=[])])],
                usage=dict(input_tokens=100, output_tokens=50, total_tokens=150)))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cap = 1 if fail else 2
            (root / 'http').mkdir(mode=0o700)
            transport = ControlledModelTransport(root / 'http', max_requests=cap,
                                                 context_sha256='b' * 64)
            client = transport.client_factory(None, transport=httpx2.MockTransport(handler))
            sdk = AsyncOpenAI(api_key='offline-test', http_client=client, max_retries=0)
            model = OpenAIResponsesModel('gpt-6-sol', provider=OpenAIProvider(openai_client=sdk))
            transport.require_model(model)
            registry = RoleRegistry(roles={'extractor': ModelSpec(
                model='openai:gpt-6-sol', output_mode='native')})
            backend = PydanticAIBackend(registry, model_resolver=lambda _: model,
                pricing=PricingTable({'openai:gpt-6-sol': {'input': 1, 'output': 1}}),
                max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False)
            args = dict(backend=backend, model_identity={'model': 'openai:gpt-6-sol'},
                        today=dt.date(2026, 11, 7), max_calls=cap, max_usd=1,
                        reservation_usd=.1, max_source_bytes=1000, settings={},
                        request_binding=transport.bind_request_descriptor)
            try:
                if fail:
                    with self.assertRaises(Exception):
                        await rules.run(root / 'run', doc, plan, **args)
                    with self.assertRaises(BudgetExceeded):
                        await rules.run(root / 'run', doc, plan, **args)
                    state = json.loads((root / 'run/rule-units-state.private.json').read_text())
                    self.assertEqual(state['attempts'][0]['status'], 'failed')
                    self.assertEqual(state['attempts'][0]['reserved_usd'], .1)
                else:
                    first = await rules.run(root / 'run', doc, plan, **args)
                    second = await rules.run(root / 'run', doc, plan, **args)
                    self.assertEqual(first, second)
                    self.assertEqual((first['candidate_count'], first['unresolved_count']), (1, 1))
                    self.assertFalse(first['accepted'])
                    self.assertTrue(first['boundary_output_accounting_complete'])
                    self.assertFalse(first['response_accounting_complete'])
                    self.assertTrue(all(not unit['accepted'] for unit in first['units']))
                self.assertEqual(len(requests), cap)
                events = [json.loads(line) for line in transport.ledger.read_text().splitlines()]
                self.assertEqual(sum(event['state'] == 'reserved' for event in events), cap)
                state = json.loads((root / 'run/rule-units-state.private.json').read_text())
                reservations = [event for event in events if event['state'] == 'reserved']
                self.assertEqual([event['logical_invocation_id'] for event in reservations],
                                 [attempt['logical_invocation_id'] for attempt in state['attempts']])
                self.assertEqual(len({a['logical_invocation_id'] for a in state['attempts']}), cap)
                if not fail:
                    responses = {event['attempt_id']: event for event in events if event['state'] == 'response'}
                    for attempt, reservation in zip(state['attempts'], reservations):
                        response = responses[reservation['attempt_id']]
                        raw = (root / 'http' / response['response_body_file']).read_bytes()
                        self.assertTrue(same_json(raw_output(raw), state['successes'][attempt['unit_id']]['output']))
                self.assertEqual(
                    [event['request_descriptor_sha256'] for event in events if event['state'] == 'reserved'],
                    [attempt['request_sha256'] for attempt in state['attempts']],
                )
            finally:
                await backend.aclose()
                await sdk.close()

    async def test_native_output_and_free_replay(self):
        await self.exercise(False)

    async def test_native_failure_cannot_escape_persistent_cap(self):
        await self.exercise(True)

    async def test_native_malformed_response_stops_before_adapter_receives_output(self):
        await self.exercise('malformed')
