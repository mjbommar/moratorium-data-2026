import json
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from native_rule_unit_journal_adapter import raw_output, same_json, strict_json


class RawEvidenceTests(unittest.TestCase):
    def envelope(self, value):
        return json.dumps({'object': 'response', 'status': 'completed', 'output': [
            {'type': 'message', 'role': 'assistant', 'status': 'completed', 'content': [
                {'type': 'output_text', 'text': json.dumps(value)}]}]}).encode()

    def test_strict_type_and_nested_output(self):
        value = {'condition': {'count': 1, 'enabled': True}, 'clause': None}
        parsed = raw_output(self.envelope(value))
        self.assertTrue(same_json(parsed, value))
        self.assertFalse(same_json(parsed, {'condition': {'count': True, 'enabled': True}, 'clause': None}))
        self.assertFalse(same_json(1, 1.0))

    def test_reject_malformed_duplicate_and_ambiguous(self):
        for data in (b'{', b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'{"x":1e-999}', b'{"x":1.0000000000000001}'):
            with self.subTest(data=data), self.assertRaises(ValueError):
                strict_json(data)
        env = json.loads(self.envelope({'x': 1}))
        env['output'].append(env['output'][0])
        with self.assertRaises(ValueError):
            raw_output(json.dumps(env).encode())

if __name__ == '__main__':
    unittest.main()

class ReconciliationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import datetime as dt
        import hashlib
        import httpx2
        from openai import AsyncOpenAI
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from bc_llm import ModelSpec, PydanticAIBackend, RoleRegistry
        from bc_llm.pricing import PricingTable
        import extract_rule_units as rules
        from controlled_model_transport import ControlledModelTransport
        from native_rule_unit_journal_adapter import reconcile
        self.reconcile = reconcile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.http = self.root/'http'; self.http.mkdir(mode=0o700)
        self.run = self.root/'run'
        self.body = self.root/'source.private.body'; self.body.write_bytes(b'synthetic source body'); self.body.chmod(0o600)
        text = 'A synthetic rule applies.'
        doc = dict(text=text, text_sha256=hashlib.sha256(text.encode()).hexdigest(), body_sha256=hashlib.sha256(self.body.read_bytes()).hexdigest())
        plan = dict(source_text_sha256=doc['text_sha256'], units=[dict(unit_id='a', anchor_quote='synthetic rule',label='A',instruction='Extract')])
        self.args = dict(model_identity={'model':'openai:gpt-6-sol'},today=dt.date(2026,11,7), max_calls=2,max_usd=1,reservation_usd=.1,max_source_bytes=1000,role='extractor',settings={})
        self.context = rules.prepare(doc,plan,storage_policy=None,**self.args)
        self.hp = dict(schema_version='controlled-model-http-1',max_requests=3,context_sha256=rules.digest(self.context))
        self.cp = dict(capture_format='controlled-model-capture-3',max_request_bytes=4096*1024,max_response_bytes=4096*1024)
        self.transport = ControlledModelTransport(self.http,max_requests=3,context_sha256=self.hp['context_sha256'],max_request_bytes=self.cp['max_request_bytes'],max_response_bytes=self.cp['max_response_bytes'])
        self.value = dict(unit_id='a',outcome='unresolved',clause=None,supporting_quotes=[],unresolved_reason='Unknown')
        def handler(request):
            return httpx2.Response(200,json=dict(id='resp_offline',object='response',created_at=0,status='completed',model='gpt-6-sol',output=[dict(type='message',id='msg_offline',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(self.value),annotations=[])])],usage=dict(input_tokens=100,output_tokens=50,total_tokens=150)))
        self.client = self.transport.client_factory(None,transport=httpx2.MockTransport(handler))
        self.sdk = AsyncOpenAI(api_key='offline-test',http_client=self.client,max_retries=0)
        model = OpenAIResponsesModel('gpt-6-sol',provider=OpenAIProvider(openai_client=self.sdk))
        registry = RoleRegistry(roles={'extractor':ModelSpec(model='openai:gpt-6-sol',output_mode='native')})
        self.backend = PydanticAIBackend(registry,model_resolver=lambda _:model,pricing=PricingTable({'openai:gpt-6-sol':{'input':1,'output':1}}),max_attempts=1,agent_retries=0,max_model_requests=1,flex_fallback=False)
        await rules.run(self.run,doc,plan,backend=self.backend,request_binding=self.transport.bind_request_descriptor,**self.args)

    async def asyncTearDown(self):
        await self.backend.aclose()
        await self.sdk.close()
        self.tmp.cleanup()

    def inspect(self):
        return self.reconcile(run_dir=self.run,http_dir=self.http,source_body=self.body,expected_context=self.context,expected_http_policy=self.hp,expected_capture_policy=self.cp)

    def snapshot(self):
        import hashlib
        return {str(p.relative_to(self.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}

    def codes(self, result):
        return {x['code'] for x in result['errors']}

    def test_real_native_trace_and_read_only(self):
        before = self.snapshot()
        r = self.inspect()
        self.assertEqual(self.codes(r), {'complete_history_unattested'})
        self.assertTrue(r['retained_records_consistent'])
        self.assertFalse(r['structural_evidence_complete'])
        self.assertFalse(r['planned_trace_complete'])
        self.assertEqual(r['logical_invocations'][0]['http_cardinality'], 'at_least_1')
        self.assertEqual(r['logical_invocations'][0]['output_comparison'],'equal')
        self.assertEqual(r['counts']['http_reservations'],1)
        self.assertEqual(r['known_generated_lower_bound'],0)
        self.assertEqual(r['generated_cardinality'],'unknown')
        self.assertFalse(r['endpoint_identity_complete'])
        self.assertFalse(r['wire_contract_complete'])
        self.assertFalse(r['response_accounting_complete'])
        self.assertEqual(before,self.snapshot())

    def test_missing_tamper_seal_and_source(self):
        seal = self.run/'rule-units-seal.private.json'
        seal.write_text('{"sha256":"bad"}'); seal.chmod(0o600)
        self.assertIn('state_seal_mismatch',self.codes(self.inspect()))
        self.body.write_bytes(b'changed')
        self.assertIn('source_body_hash_mismatch',self.codes(self.inspect()))
        seal.unlink()
        self.assertIn('seal_unavailable',self.codes(self.inspect()))

    def test_partial_response_and_zero_observed_dispatch(self):
        ledger = self.http/'http-attempts.private.jsonl'
        lines = ledger.read_bytes().splitlines(keepends=True)
        ledger.write_bytes(lines[0])
        r = self.inspect()
        self.assertIn('response_missing',self.codes(r))
        self.assertEqual(r['http_attempts'][0]['disposition'],'no_response')
        ledger.write_bytes(b'')
        r = self.inspect()
        self.assertEqual(r['logical_invocations'][0]['dispatch'],'unproven')
        self.assertIn('logical_dispatch_unproven',self.codes(r))
        self.assertGreater(len(r['unjournaled_artifacts']),0)
        self.assertEqual(r['counts']['http_reservations'],0)

    def test_raw_coercion_and_ambiguous_output(self):
        import hashlib
        ledger = self.http/'http-attempts.private.jsonl'
        events = [json.loads(s) for s in ledger.read_text().splitlines()]
        response = events[1]; body = self.http/response['response_body_file']
        env = json.loads(body.read_bytes())
        value = json.loads(env['output'][0]['content'][0]['text'])
        value['supporting_quotes'] = [True]
        env['output'][0]['content'][0]['text'] = json.dumps(value)
        raw = json.dumps(env).encode(); body.write_bytes(raw)
        response['wire_response_bytes']=len(raw); response['wire_response_sha256']=hashlib.sha256(raw).hexdigest()
        ledger.write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in events))
        r = self.inspect()
        self.assertEqual(r['logical_invocations'][0]['output_comparison'],'mismatch')
        self.assertIn('raw_boundary_mismatch',self.codes(r))
        env['output'].append(env['output'][0]); raw=json.dumps(env).encode(); body.write_bytes(raw)
        response['wire_response_bytes']=len(raw); response['wire_response_sha256']=hashlib.sha256(raw).hexdigest()
        ledger.write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in events))
        self.assertIn('raw_output_unverified',self.codes(self.inspect()))

    def test_duplicate_and_unbound_and_partial_line(self):
        ledger = self.http/'http-attempts.private.jsonl'
        lines=ledger.read_text().splitlines()
        row=json.loads(lines[0]); row['logical_invocation_id']=None
        ledger.write_text(json.dumps(row)+'\n'+lines[1]+'\n'+json.dumps(row)+'\n'+ '{')
        r=self.inspect()
        self.assertIn('duplicate_http_reservation',self.codes(r))
        self.assertIn('http_linkage_unbound',self.codes(r))
        self.assertIn('journal_partial_line',self.codes(r))
        self.assertEqual(r['counts']['unbound_http'],1)
        self.assertEqual(r['logical_invocations'][0]['http_cardinality'],'at_least_0')

    async def test_real_retry_is_preserved_and_ambiguous(self):
        state=json.loads((self.run/'rule-units-state.private.json').read_text())
        attempt=state['attempts'][0]
        with self.transport.bind_request_descriptor(attempt['request_sha256'],attempt['logical_invocation_id']):
            await self.client.post('https://example.test/synthetic',json={'retry':True})
        r=self.inspect()
        self.assertEqual(len(r['logical_invocations'][0]['http_attempt_ids']),2)
        self.assertEqual(r['counts']['http_reservations'],2)
        self.assertEqual(r['logical_invocations'][0]['output_comparison'],'unknown_multiple_or_zero_http_attempts')
        self.assertIn('successful_output_ambiguous',self.codes(r))

    def test_old_capture_and_partial_event(self):
        ledger=self.http/'http-attempts.private.jsonl'
        events=[json.loads(s) for s in ledger.read_text().splitlines()]
        events[0]['capture_format']='controlled-model-capture-2'
        events[1]['response_capture_complete']=False
        ledger.write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in events))
        r=self.inspect()
        self.assertIn('old_or_unknown_capture',self.codes(r))
        self.assertIn('response_capture_incomplete',self.codes(r))
        self.assertEqual(r['counts']['partial_response'],1)
        self.assertFalse(r['structural_evidence_complete'])

    def test_private_safety_and_changed_artifact(self):
        state=self.run/'rule-units-state.private.json'
        state.chmod(0o644)
        self.assertIn('state_unavailable',self.codes(self.inspect()))
        state.chmod(0o600)
        event=json.loads((self.http/'http-attempts.private.jsonl').read_text().splitlines()[0])
        (self.http/event['request_body_file']).write_bytes(b'changed')
        self.assertTrue({'artifact_length_mismatch','artifact_digest_mismatch'} & self.codes(self.inspect()))

    def test_cli_json_nonzero_and_no_writes(self):
        import os
        import subprocess
        paths=[]
        for name, value in [('context',self.context),('http-policy',self.hp),('capture-policy',self.cp)]:
            p=self.root/(name+'.json'); p.write_text(json.dumps(value)); p.chmod(0o600); paths.append(p)
        before=self.snapshot()
        cli=Path(__file__).resolve().parents[1]/'scripts/native_rule_unit_journal_adapter.py'
        proc=subprocess.run([sys.executable,str(cli),'--run-dir',str(self.run),'--http-dir',str(self.http),'--source-body',str(self.body),'--expected-context',str(paths[0]),'--expected-http-policy',str(paths[1]),'--expected-capture-policy',str(paths[2])],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        self.assertNotEqual(proc.returncode,0)
        self.assertTrue(json.loads(proc.stdout)['retained_records_consistent'])
        self.assertFalse(json.loads(proc.stdout)['structural_evidence_complete'])
        self.assertEqual(before,self.snapshot())

    def test_failed_sdk_rejection_and_unknown_output(self):
        import extract_rule_units as rules
        state_path=self.run/'rule-units-state.private.json'
        state=json.loads(state_path.read_text())
        attempt=state['attempts'][0]
        attempt.pop('accounting'); attempt.pop('charged_usd')
        attempt.update(status='failed',error_type='UnexpectedModelBehavior')
        state['successes']={}
        state_path.write_text(json.dumps(state,sort_keys=True)+'\n')
        (self.run/'rule-units-seal.private.json').write_text(json.dumps({'sha256':rules.digest(state)}))
        (self.run/'rule-units-candidates.private.json').write_text(json.dumps(rules.packet(state,self.context)))
        r=self.inspect()
        self.assertEqual(r['logical_invocations'][0]['status'],'failed')
        self.assertEqual(r['logical_invocations'][0]['error_type'],'UnexpectedModelBehavior')
        self.assertEqual(r['logical_invocations'][0]['charged_usd'],.1)
        self.assertEqual(r['generated_cardinality'],'unknown')
        self.assertEqual(r['counts']['failed_logical'],1)
        self.assertTrue(r['retained_records_consistent'])
        self.assertFalse(r['structural_evidence_complete'])
        (self.http/'http-attempts.private.jsonl').write_bytes(b'')
        no_wire = self.inspect()
        self.assertEqual(no_wire['logical_invocations'][0]['dispatch'], 'unproven')
        self.assertEqual(no_wire['logical_invocations'][0]['charged_usd'], .1)
        self.assertEqual(no_wire['counts']['http_reservations'], 0)

    def test_journal_truncation_does_not_synthesize_response(self):
        ledger=self.http/'http-attempts.private.jsonl'
        lines=ledger.read_bytes().splitlines(keepends=True)
        ledger.write_bytes(lines[0]+lines[1][:25])
        r=self.inspect()
        self.assertEqual(r['http_history_cardinality'],'unknown_lower_bound')
        self.assertEqual(r['http_attempts'][0]['disposition'],'no_response')
        self.assertEqual(r['logical_invocations'][0]['http_cardinality'],'at_least_1')
        self.assertIn('journal_line_invalid',self.codes(r))

    def test_descriptor_mismatch_remains_a_visible_attempt(self):
        ledger=self.http/'http-attempts.private.jsonl'
        events=[json.loads(s) for s in ledger.read_text().splitlines()]
        events[0]['request_descriptor_sha256']='a'*64
        ledger.write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in events))
        r=self.inspect()
        self.assertIn('http_linkage_ambiguous_or_descriptor_mismatch',self.codes(r))
        self.assertEqual(r['counts']['http_reservations'],1)
        self.assertEqual(len(r['logical_invocations'][0]['http_attempt_ids']),1)

    def test_coherent_empty_history_is_unobserved_not_complete(self):
        import extract_rule_units as rules
        state_path = self.run/'rule-units-state.private.json'
        state = json.loads(state_path.read_text())
        state['attempts'] = []
        state['successes'] = {}
        state_path.write_text(json.dumps(state))
        (self.run/'rule-units-seal.private.json').write_text(json.dumps({'sha256': rules.digest(state)}))
        (self.run/'rule-units-candidates.private.json').write_text(json.dumps(rules.packet(state, self.context)))
        (self.http/'http-attempts.private.jsonl').write_bytes(b'')
        for p in self.http.iterdir():
            if p.name.endswith(('-request.private.body', '-response.private.body', '-journal-reservation.private.bytes')):
                p.unlink()
        before = self.snapshot()
        r = self.inspect()
        self.assertTrue(r['retained_records_consistent'])
        self.assertFalse(r['structural_evidence_complete'])
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(r['counts']['unattempted_units'], 1)
        self.assertEqual(r['counts']['planned_dispatch_unproven'], 1)
        self.assertEqual(r['http_history_cardinality'], 'unknown_lower_bound')
        self.assertEqual(r['logical_history_cardinality'], 'unknown_lower_bound')
        self.assertIn('planned_units_unobserved', self.codes(r))
        self.assertEqual(before, self.snapshot())

    def test_missing_state_packet_and_request_body(self):
        state = self.run/'rule-units-state.private.json'
        packet = self.run/'rule-units-candidates.private.json'
        state.unlink(); packet.unlink()
        row = json.loads((self.http/'http-attempts.private.jsonl').read_text().splitlines()[0])
        (self.http/row['request_body_file']).unlink()
        r = self.inspect()
        self.assertTrue({'state_unavailable', 'packet_unavailable', 'artifact_unavailable'} <= self.codes(r))
        self.assertFalse(r['retained_records_consistent'])
        self.assertFalse(r['structural_evidence_complete'])
        self.assertEqual(r['counts']['http_reservations'], 1)

    def test_fifo_and_symlink_fail_without_blocking(self):
        import os
        state = self.run/'rule-units-state.private.json'
        state.unlink()
        os.mkfifo(state, 0o600)
        self.assertIn('state_unavailable', self.codes(self.inspect()))
        state.unlink()
        state.symlink_to(self.body)
        self.assertIn('state_unavailable', self.codes(self.inspect()))

    def test_orphan_response_is_retained(self):
        ledger = self.http/'http-attempts.private.jsonl'
        lines = ledger.read_bytes().splitlines(keepends=True)
        ledger.write_bytes(lines[1])
        r = self.inspect()
        self.assertIn('orphan_or_duplicate_response', self.codes(r))
        self.assertTrue(any(x['disposition'] == 'orphan_or_duplicate_response' for x in r['http_attempts']))
        self.assertEqual(r['logical_invocations'][0]['http_cardinality'], 'at_least_0')
        self.assertFalse(r['planned_trace_complete'])
