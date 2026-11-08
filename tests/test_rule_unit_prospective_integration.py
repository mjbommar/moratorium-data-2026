"""Offline end-to-end prospective witness and native audit tests."""
import copy
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import httpx2
import extract_rule_units as rules
from audit_rule_unit_trial import audit_native
from controlled_model_transport import ControlledModelTransport
from native_rule_unit_wire_contract import PROFILE, workload
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from bc_llm import ModelSpec, PydanticAIBackend, RoleRegistry
from bc_llm.pricing import PricingTable


class ProspectiveTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.http = self.root / 'http'; self.http.mkdir(mode=0o700)
        self.run_dir = self.root / 'run'
        self.body = self.root / 'source'; self.body.write_bytes(b'synthetic source'); self.body.chmod(0o600)
        text = 'A synthetic rule applies.'; sha = hashlib.sha256(text.encode()).hexdigest()
        self.doc = dict(text=text, text_sha256=sha, body_sha256=hashlib.sha256(self.body.read_bytes()).hexdigest(), reviewed_source_role='proposed')
        self.plan = dict(source_text_sha256=sha, units=[dict(unit_id='a', anchor_quote='synthetic rule', label='A', instruction='Extract')])
        self.args = dict(model_identity={'model':'openai:gpt-6.1-terra','native_wire_profile':PROFILE}, today=dt.date(2026,11,8), max_calls=1, max_usd=1, reservation_usd=.1, max_source_bytes=1000, role='extractor', settings={})
        self.ctx = rules.prepare(self.doc, self.plan, storage_policy=None, **self.args)
        self.witness = workload(self.ctx); self.anchor = rules.digest(self.witness)
        self.hp = dict(schema_version='controlled-model-http-1', max_requests=1, context_sha256=rules.digest(self.ctx))
        self.cp = dict(capture_format='controlled-model-capture-3', max_request_bytes=8388608, max_response_bytes=8388608)
        self.transport = ControlledModelTransport(self.http, max_requests=1, context_sha256=rules.digest(self.ctx))
        self.requests = 0
        def handler(request):
            self.requests += 1
            value = dict(unit_id='a', outcome='unresolved', clause=None, supporting_quotes=[], unresolved_reason='Unknown')
            return httpx2.Response(200, json=dict(id='resp_offline',object='response',created_at=0,status='completed',model='gpt-6.1-terra',output=[dict(type='message',id='msg_offline',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(value),annotations=[])])],usage=dict(input_tokens=10,output_tokens=10,total_tokens=20)))
        self.client = self.transport.client_factory(None, transport=httpx2.MockTransport(handler))
        self.sdk = AsyncOpenAI(api_key='offline', http_client=self.client, max_retries=0)
        model = OpenAIResponsesModel('gpt-6.1-terra', provider=OpenAIProvider(openai_client=self.sdk))
        spec = ModelSpec(model='openai:gpt-6.1-terra', output_mode='native')
        self.backend = PydanticAIBackend(RoleRegistry(roles={'extractor':spec}), model_resolver=lambda _:model, pricing=PricingTable({'openai:gpt-6.1-terra':{'input':1,'output':1}}),max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)

    async def asyncTearDown(self):
        await self.backend.aclose(); await self.sdk.close(); self.tmp.cleanup()

    async def extract(self, **overrides):
        kw = dict(self.args, backend=self.backend, request_binding=self.transport.bind_request_descriptor, prospective_workload=self.witness, workload_sha256=self.anchor)
        kw.update(overrides)
        return await rules.run(self.run_dir, self.doc, self.plan, **kw)

    async def audit(self, **overrides):
        kw = dict(run_dir=self.run_dir,http_dir=self.http,source_body=self.body,witness=self.witness,anchor=self.anchor,http_policy=self.hp,capture_policy=self.cp)
        kw.update(overrides)
        return await audit_native(**kw)

    async def test_round_trip_and_tampering(self):
        await self.extract()
        result = await self.audit()
        self.assertTrue(result['response_accounting_complete'], result['errors'])
        self.assertTrue(result['wire_contract_complete'])
        self.assertEqual(result['quality'], 'not_scored')
        self.assertIn('provider authentication not established',result['requested_endpoint_scope'])
        files = []
        for name, value in [('witness', self.witness), ('http-policy', self.hp), ('capture-policy', self.cp)]:
            path = self.root / name; path.write_text(json.dumps(value)); path.chmod(0o600); files.append(path)
        cli = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_rule_unit_trial.py'
        proc = subprocess.run([sys.executable, str(cli), '--run-dir', str(self.run_dir), '--http-dir', str(self.http),
            '--source-body', str(self.body), '--witness', str(files[0]), '--anchor', self.anchor,
            '--http-policy', str(files[1]), '--capture-policy', str(files[2])], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)['response_accounting_complete'])
        bad = await self.audit(anchor='0'*64)
        self.assertFalse(bad['response_accounting_complete'])
        self.assertEqual(bad['observed_http_reservation_lower_bound'],1)
        self.body.write_bytes(b'wrong source')
        bad = await self.audit()
        self.assertFalse(bad['response_accounting_complete'])
        self.assertIn('source_body_hash_mismatch', [e['code'] for e in bad['errors']])
        self.body.write_bytes(b'synthetic source')
        row = json.loads(self.transport.ledger.read_text().splitlines()[0]); path = self.http / row['request_body_file']
        data = json.loads(path.read_bytes()); data['model'] = 'different'
        changed = json.dumps(data).encode(); path.write_bytes(changed)
        # Retained body and journal both changed: wire comparator must still reject it.
        rows = [json.loads(x) for x in self.transport.ledger.read_text().splitlines()]
        rows[0]['wire_request_sha256'] = hashlib.sha256(changed).hexdigest(); rows[0]['wire_request_bytes'] = len(changed)
        self.transport.ledger.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows))
        bad = await self.audit()
        self.assertFalse(bad['wire_contract_complete'])
        self.assertIn('wire_comparison_failed', [e['code'] for e in bad['errors']])

    async def test_reject_anchor_context_and_model_before_dispatch(self):
        for kw in ({'workload_sha256':None}, {'workload_sha256':'0'*64}, {'prospective_workload':dict(self.witness, dispatches=[])}, {'settings':{'temperature':0}}, {'model_identity':{'model':'openai:gpt-6-sol','native_wire_profile':PROFILE}}):
            with self.subTest(kw=kw), self.assertRaises(ValueError): await self.extract(**kw)
        self.assertEqual(self.requests, 0)
        self.backend.max_attempts = 2
        with self.assertRaises(ValueError): await self.extract()
        self.backend.max_attempts = 1
        self.doc['reviewed_source_role'] = 'enacted_text'
        with self.assertRaises(ValueError): await self.extract()
        self.assertEqual(self.requests, 0)

    async def test_omitted_extra_and_partial(self):
        await self.extract()
        marker = self.run_dir / 'rule-units-workload.private.json'
        saved = marker.read_bytes(); marker.unlink()
        missing = await self.audit()
        self.assertFalse(missing['prospective_anchor_verified'])
        self.assertEqual(missing['observed_http_reservation_lower_bound'], 1)
        marker.write_bytes(saved); marker.chmod(0o600)
        rows = [json.loads(x) for x in self.transport.ledger.read_text().splitlines()]
        original = self.transport.ledger.read_bytes()
        self.transport.ledger.write_text('')
        omitted = await self.audit()
        self.assertIn('prospective_dispatch_population_mismatch', [e['code'] for e in omitted['errors']])
        self.assertFalse(omitted['response_accounting_complete'])
        self.transport.ledger.write_bytes(original)
        with self.transport.ledger.open('ab') as stream:
            stream.write((json.dumps(rows[0])+'\n').encode())
        extra = await self.audit()
        self.assertFalse(extra['response_accounting_complete'])
        self.assertIn('duplicate_http_reservation', [e['code'] for e in extra['errors']])
        self.transport.ledger.write_bytes(original)
        extra_row = dict(rows[0]); extra_row['attempt_id'] = 'f' * 32
        with self.transport.ledger.open('ab') as stream:
            stream.write((json.dumps(extra_row)+'\n').encode())
        extra = await self.audit()
        self.assertIn('prospective_http_population_mismatch', [e['code'] for e in extra['errors']])
        self.transport.ledger.write_bytes(original)
        witness = copy.deepcopy(self.witness); witness['dispatches'].append(copy.deepcopy(witness['dispatches'][0]))
        result = await self.audit(witness=witness, anchor=rules.digest(witness))
        self.assertFalse(result['response_accounting_complete'])
        self.assertIn('prospective_dispatch_population_mismatch', [e['code'] for e in result['errors']])
        rows[1]['response_capture_complete'] = False
        self.transport.ledger.write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows))
        result = await self.audit()
        self.assertFalse(result['response_accounting_complete'])
        self.assertEqual(result['counts']['partial_response'],1)
        self.transport.ledger.write_text(json.dumps(rows[0])+'\n')
        result = await self.audit()
        self.assertFalse(result['response_accounting_complete'])
        self.assertEqual(result['counts']['no_response'],1)

    async def test_two_unit_http_reservation_order(self):
        await self.backend.aclose(); await self.sdk.close()
        self.plan['units'].append(dict(unit_id='b', anchor_quote='applies', label='B', instruction='Extract'))
        self.args['max_calls'] = 2
        self.ctx = rules.prepare(self.doc, self.plan, storage_policy=None, **self.args)
        self.witness = workload(self.ctx); self.anchor = rules.digest(self.witness)
        self.hp.update(max_requests=2, context_sha256=rules.digest(self.ctx))
        self.http = self.root / 'http-two'; self.http.mkdir(mode=0o700)
        self.transport = ControlledModelTransport(self.http, max_requests=2, context_sha256=rules.digest(self.ctx))
        self.requests = 0
        def handler(request):
            uid = ['a', 'b'][self.requests]; self.requests += 1
            value = dict(unit_id=uid, outcome='unresolved', clause=None, supporting_quotes=[], unresolved_reason='Unknown')
            return httpx2.Response(200, json=dict(id='resp_offline', object='response', created_at=0, status='completed', model='gpt-6.1-terra', output=[dict(type='message', id='msg_offline', role='assistant', status='completed', content=[dict(type='output_text', text=json.dumps(value), annotations=[])])], usage=dict(input_tokens=10, output_tokens=10, total_tokens=20)))
        self.client = self.transport.client_factory(None, transport=httpx2.MockTransport(handler))
        self.sdk = AsyncOpenAI(api_key='offline', http_client=self.client, max_retries=0)
        model = OpenAIResponsesModel('gpt-6.1-terra', provider=OpenAIProvider(openai_client=self.sdk))
        spec = ModelSpec(model='openai:gpt-6.1-terra', output_mode='native')
        self.backend = PydanticAIBackend(RoleRegistry(roles={'extractor':spec}), model_resolver=lambda _:model, pricing=PricingTable({'openai:gpt-6.1-terra':{'input':1,'output':1}}), max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False)

        await self.extract()
        valid = await self.audit()
        self.assertTrue(valid['response_accounting_complete'], valid['errors'])
        self.assertEqual([x['unit_id'] for x in valid['logical_invocations']], ['a', 'b'])
        lines = self.transport.ledger.read_text().splitlines()
        self.assertEqual([json.loads(line)['state'] for line in lines], ['reserved', 'response', 'reserved', 'response'])
        self.transport.ledger.write_text('\n'.join(lines[2:4] + lines[0:2]) + '\n')
        swapped = await self.audit()
        self.assertFalse(swapped['response_accounting_complete'])
        self.assertIn('prospective_http_dispatch_order_mismatch', [e['code'] for e in swapped['errors']])
        for result in (valid, swapped):
            self.assertEqual(result['observed_http_reservation_lower_bound'], 2)
            self.assertEqual(result['observed_logical_record_count'], 2)
            self.assertEqual(result['http_history_cardinality'], 'unknown_lower_bound')
            self.assertEqual(result['logical_history_cardinality'], 'unknown_lower_bound')
            self.assertEqual(result['quality'], 'not_scored')
