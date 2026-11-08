import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
from unittest.mock import patch
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
            self_test = self

            class LockCheckingStorage(PrivateRunStorage):
                def __init__(self, *args):
                    self.reservations = []
                    super().__init__(*args)

                def _reserve(self, size):
                    # A separate open description must not acquire either lock.
                    with (self.root / '.storage.lock').open('r+') as lock:
                        with self_test.assertRaises(BlockingIOError):
                            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    ledger_path = self.root / 'http-attempts.private.jsonl'
                    if ledger_path.exists():
                        with ledger_path.open('a+') as ledger:
                            with self_test.assertRaises(BlockingIOError):
                                fcntl.flock(ledger, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.reservations.append(size)
                    return super()._reserve(size)

            store = LockCheckingStorage(tmp, 100_000)
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store, max_response_bytes=64)
            before_request = len(store.reservations)
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200, content=b'response')
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                response = await client.post('https://example.invalid/model', content=b'request')
            self.assertEqual(response.content, b'response')
            self.assertEqual(len(seen), 1)
            self.assertEqual(len(store.reservations), before_request + 1)
            self.assertGreater(store.reservations[-1], len(b'request') + 64)
            rows = [json.loads(line) for line in audit.ledger.read_text().splitlines()]
            self.assertEqual([e['state'] for e in rows], ['reserved', 'response'])
            self.assertEqual(rows[0]['response_capacity_bytes'], 64)
            self.assertEqual((Path(tmp) / rows[0]['request_body_file']).read_bytes(), b'request')
            self.assertEqual((Path(tmp) / rows[1]['response_body_file']).read_bytes(), b'response')
            # Reserved capacity remains charged, including unused response bytes.
            response_bound = dict(rows[1], response_capture_complete=False,
                                  wire_response_sha256='f' * 64, wire_response_bytes=64,
                                  status=999, observed_at='9999-12-31T23:59:59.999999+00:00')
            remaining = len(audit._encoded(response_bound)) + 64 - len(b'response') - len(audit._encoded(rows[1]))
            slot = Path(tmp) / rows[0]['journal_reservation_file']
            self.assertEqual(slot.read_bytes(), bytes(remaining))

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

    async def test_http_response_capacity_rejection_prevents_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 2000)
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store)
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.invalid/model')
            self.assertEqual(seen, [])
            self.assertEqual(audit.ledger.read_text(), '')
            self.assertFalse(list(Path(tmp).glob('*-request.private.body')))
            self.assertFalse(list(Path(tmp).glob('*-response.pending.private.body')))
            self.assertFalse(list(Path(tmp).glob('*-journal-reservation.private.bytes')))

    async def test_http_reserved_capacity_rejects_competing_write_after_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 10_000)
            audit = ControlledModelTransport(tmp, max_requests=1, context_sha256='0' * 64,
                                             storage_policy=store, max_response_bytes=64)
            seen = []
            def handler(request):
                seen.append(request)
                used = sum(p.stat().st_size for p in Path(tmp).rglob('*') if p.is_file())
                # One byte beyond remaining space must be rejected before writing.
                with self.assertRaises(StorageBudgetExceeded):
                    store.put_bytes('filler', b'x' * (store.max_bytes - used + 1))
                self.assertFalse((Path(tmp) / 'filler').exists())
                return httpx2.Response(200, content=b'response')
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                response = await client.post('https://example.invalid/model')
            self.assertEqual(response.content, b'response')
            self.assertEqual(len(seen), 1)
            self.assertEqual([json.loads(line)['state'] for line in audit.ledger.read_text().splitlines()],
                             ['reserved', 'response'])

    async def test_http_response_journal_write_failure_retains_charge_and_blocks_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 100_000)
            audit = ControlledModelTransport(tmp, max_requests=2, context_sha256='0' * 64,
                                             storage_policy=store, max_response_bytes=64)
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200, content=b'response')
            append = audit._append_reserved
            def fail_response(stream, event, slot):
                if event['state'] == 'response':
                    raise OSError('injected response journal failure')
                return append(stream, event, slot)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with patch.object(audit, '_append_reserved', side_effect=fail_response):
                    with self.assertRaisesRegex(OSError, 'injected response journal failure'):
                        await client.post('https://example.invalid/model', content=b'request')
                with self.assertRaisesRegex(ValueError, 'unresolved reservation'):
                    await client.post('https://example.invalid/model')
            self.assertEqual(len(seen), 1)
            rows = [json.loads(line) for line in audit.ledger.read_text().splitlines()]
            self.assertEqual([e['state'] for e in rows], ['reserved'])
            row = rows[0]
            self.assertEqual((Path(tmp) / row['request_body_file']).read_bytes(), b'request')
            self.assertEqual((Path(tmp) / (row['attempt_id'] + '-response.private.body')).read_bytes(), b'response')
            self.assertGreaterEqual((Path(tmp) / row['journal_reservation_file']).stat().st_size, 64 - len(b'response'))
            self.assertFalse((Path(tmp) / row['response_pending_file']).exists())

    async def test_http_response_body_cap_persists_incomplete_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PrivateRunStorage(tmp, 100_000)
            audit = ControlledModelTransport(tmp, max_requests=2, context_sha256='0' * 64,
                                             storage_policy=store, max_response_bytes=4)
            seen = []
            def handler(request):
                seen.append(request)
                return httpx2.Response(200, content=b'12345')
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with self.assertRaisesRegex(ValueError, 'response capture byte limit exceeded'):
                    await client.post('https://example.invalid/model')
                with self.assertRaisesRegex(ValueError, 'Incomplete response capture'):
                    await client.post('https://example.invalid/model')
            self.assertEqual(len(seen), 1)
            rows = [json.loads(line) for line in audit.ledger.read_text().splitlines()]
            self.assertEqual([row['state'] for row in rows], ['reserved', 'response'])
            self.assertFalse(rows[1]['response_capture_complete'])
            self.assertEqual(rows[1]['wire_response_bytes'], 4)
            self.assertEqual((Path(tmp) / rows[1]['response_body_file']).read_bytes(), b'1234')

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
