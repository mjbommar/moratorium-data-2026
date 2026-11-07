import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import httpx2
from bc_llm.backend import ScriptedBackend

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import extract_document_resumable as resumable
import extract_domain_candidates as domain
from controlled_model_transport import ControlledModelTransport
from private_run_storage import PrivateRunStorage, StorageBudgetExceeded


class RecordingStorage:
    def __init__(self, store):
        self.store = store
        self.writes = []

    def describe(self):
        return self.store.describe()

    def save_json(self, path, value, **kwargs):
        self.writes.append(('json', Path(path).name))
        return self.store.save_json(path, value, **kwargs)

    def append_jsonl_stream(self, stream, value):
        self.writes.append(('event', value['state']))
        return self.store.append_jsonl_stream(stream, value)


def inputs():
    text = 'This proposal expires 180 days from the effective date.'
    return dict(doc=dict(doc_id='fixture', text=text, title='Proposal', final_url=None,
                         url='https://example.invalid', published=None, language='en',
                         body_sha256='0' * 64, text_sha256=hashlib.sha256(text.encode()).hexdigest()),
                cells=[dict(cell_id='c', subject_label='Fixture', topic_label='Clauses',
                            prospective=False, window_start='2026-01-01', window_end='2026-11-05')],
                question='Extract candidates', today=dt.date(2026, 11, 5), max_calls=5,
                model_identity={'model': 'scripted:fake'})


def backend():
    return ScriptedBackend({'*': lambda *args: dict(relevance=0, summary='', claims=[],
                                                    unresolved_fields=[])})


class StoragePipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_domain_pipeline_uses_storage_and_replays_frozen_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RecordingStorage(PrivateRunStorage(tmp, 1_000_000))
            model = backend()
            result = await domain.run(tmp, backend=model, storage_policy=store, **inputs())
            state = json.loads((Path(tmp) / 'state.private.json').read_text())
            self.assertEqual(state['context']['storage_policy'], store.describe())
            self.assertEqual(result, await domain.run(tmp, backend=model, storage_policy=store, **inputs()))
            self.assertEqual(len(model.calls), 1)
            self.assertTrue({('json', name) for name in ('state.private.json', 'result.private.json',
                            'domain-candidates.private.json')} <= set(store.writes))
            with self.assertRaises(resumable.WorkspaceContextChanged):
                await domain.run(tmp, backend=model, **inputs())
            self.assertEqual(len(model.calls), 1)

    async def test_storage_rejection_before_model_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 1000)
            model = backend()
            with self.assertRaises(StorageBudgetExceeded):
                await domain.run(tmp, backend=model, storage_policy=store, **inputs())
            self.assertEqual(model.calls, [])
            self.assertFalse((Path(tmp) / 'result.private.json').exists())
            self.assertFalse((Path(tmp) / 'domain-candidates.private.json').exists())

    async def test_http_policy_and_events_use_storage(self):
        with tempfile.TemporaryDirectory() as tmp:
            class LockCheckingStorage(RecordingStorage):
                def check_ledger_locked(self):
                    with (Path(tmp) / 'http-attempts.private.jsonl').open('a+') as ledger:
                        with self_test.assertRaises(BlockingIOError):
                            fcntl.flock(ledger, fcntl.LOCK_EX | fcntl.LOCK_NB)

                def save_json(self, path, value, **kwargs):
                    self.check_ledger_locked()
                    return super().save_json(path, value, **kwargs)

                def append_jsonl_stream(self, stream, value):
                    self.check_ledger_locked()
                    return super().append_jsonl_stream(stream, value)

            self_test = self
            store = LockCheckingStorage(PrivateRunStorage(tmp, 100_000))
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store)
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                await client.post('https://example.invalid/model')
            self.assertEqual(len(seen), 1)
            self.assertEqual(store.writes, [('json', 'http-policy.private.json'),
                                            ('event', 'reserved'), ('event', 'response')])
            self.assertEqual([e['state'] for e in map(json.loads, audit.ledger.read_text().splitlines())],
                             ['reserved', 'response'])

    async def test_http_reservation_rejection_prevents_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 2000)
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store)
            used = sum(p.stat().st_size for p in Path(tmp).rglob('*') if p.is_file())
            store.put_bytes('filler', b'x' * (store.max_bytes - used))
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.invalid/model')
            self.assertEqual(seen, [])
            self.assertEqual(audit.ledger.read_text(), '')

    async def test_http_response_rejection_retains_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 2000)
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store)
            seen = []
            def handler(request):
                seen.append(request)
                used = sum(p.stat().st_size for p in Path(tmp).rglob('*') if p.is_file())
                store.put_bytes('filler', b'x' * (store.max_bytes - used))
                return httpx2.Response(200)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.invalid/model')
            self.assertEqual(len(seen), 1)
            self.assertEqual([e['state'] for e in map(json.loads, audit.ledger.read_text().splitlines())],
                             ['reserved'])

    def test_http_policy_rejection_does_not_write_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 500)
            used = sum(p.stat().st_size for p in Path(tmp).rglob('*') if p.is_file())
            store.put_bytes('filler', b'x' * (store.max_bytes - used))
            with self.assertRaises(StorageBudgetExceeded):
                ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                         storage_policy=store)
            self.assertFalse((Path(tmp) / 'http-policy.private.json').exists())

    async def test_legacy_context_omits_storage_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            await domain.run(tmp, backend=backend(), **inputs())
            state = json.loads((Path(tmp) / 'state.private.json').read_text())
            self.assertNotIn('storage_policy', state['context'])


if __name__ == '__main__':
    unittest.main()
