import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from controlled_model_transport import ControlledModelTransport


class ControlledModelTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_sdk_failure_and_budget_stop_are_observed(self):
        import httpx2
        from openai import AsyncOpenAI
        from pydantic import BaseModel
        from pydantic_ai.models.openai import OpenAIResponsesModel
        from pydantic_ai.providers.openai import OpenAIProvider
        from pydantic_ai.exceptions import ModelHTTPError
        from bc_core.budget import BudgetExceeded
        from bc_llm import ModelSpec, RoleRegistry, PydanticAIBackend

        class Output(BaseModel):
            ok: bool

        requests = []

        def handler(request):
            requests.append(request)
            return httpx2.Response(503, json={"error": {"message": "mock failure"}})

        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            client = audit.client_factory(None, transport=httpx2.MockTransport(handler))
            sdk = AsyncOpenAI(api_key="test", http_client=client, max_retries=0)
            model = OpenAIResponsesModel(
                "gpt-6-sol", provider=OpenAIProvider(openai_client=sdk)
            )
            audit.require_model(model)
            registry = RoleRegistry(
                roles={
                    "extractor": ModelSpec(
                        model="openai:gpt-6-sol", output_mode="native"
                    )
                }
            )
            backend = PydanticAIBackend(
                registry,
                model_resolver=lambda _: model,
                max_attempts=1,
                agent_retries=0,
                max_model_requests=1,
                flex_fallback=False,
            )
            try:
                with self.assertRaises(ModelHTTPError):
                    await backend.generate(
                        role="extractor", prompt="mock", output_type=Output
                    )
                with self.assertRaises(Exception) as captured:
                    await backend.generate(
                        role="extractor", prompt="mock", output_type=Output
                    )
                error = captured.exception
                causes = []
                while error is not None:
                    causes.append(error)
                    error = error.__cause__
                self.assertTrue(
                    any(isinstance(error, BudgetExceeded) for error in causes)
                )
                self.assertEqual(len(requests), 1)
                events = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
                self.assertEqual([e["state"] for e in events], ["reserved", "response"])
                self.assertEqual(events[-1]["status"], 503)
            finally:
                await backend.aclose()
                await sdk.close()

    async def test_cap_persists_across_clients_without_recording_credentials(self):
        import httpx2
        from bc_core.budget import BudgetExceeded

        requests = []

        def handler(request):
            requests.append(request)
            return httpx2.Response(200, json={"ok": True})

        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            async with audit.client_factory(
                None, transport=httpx2.MockTransport(handler)
            ) as client:
                await client.post(
                    "https://api.example.test/v1/model?api_key=secret-query",
                    headers={"Authorization": "Bearer secret-header"},
                    json={"text": "private-prompt"},
                )
            reloaded = ControlledModelTransport(
                d, max_requests=1, context_sha256="0" * 64
            )
            async with reloaded.client_factory(
                None, transport=httpx2.MockTransport(handler)
            ) as client:
                with self.assertRaises(BudgetExceeded):
                    await client.post("https://api.example.test/v1/model")
            self.assertEqual(len(requests), 1)
            text = audit.ledger.read_text()
            for secret in ("secret-query", "secret-header", "private-prompt"):
                self.assertNotIn(secret, text)
            self.assertEqual(
                [e["state"] for e in map(json.loads, text.splitlines())],
                ["reserved", "response"],
            )

    async def test_connection_failure_still_consumes_reservation(self):
        import httpx2
        from bc_core.budget import BudgetExceeded

        def handler(request):
            raise httpx2.ConnectError("mock", request=request)

        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            async with audit.client_factory(
                None, transport=httpx2.MockTransport(handler)
            ) as client:
                with self.assertRaises(httpx2.ConnectError):
                    await client.post("https://api.example.test/model")
                with self.assertRaisesRegex(ValueError, "Incomplete response capture"):
                    await client.post("https://api.example.test/model")
            self.assertEqual(len(audit.ledger.read_text().splitlines()), 1)

    async def test_sdk_retry_and_unobserved_transport_rejected_before_spend(self):
        import httpx2

        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            async with audit.client_factory(
                None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))
            ) as client:
                model = SimpleNamespace(
                    client=SimpleNamespace(max_retries=2, _client=client)
                )
                with self.assertRaisesRegex(ValueError, "SDK retries"):
                    audit.require_model(model)
                model.client.max_retries = 0
                self.assertIs(audit.require_model(model), model)
                model.client._client = object()
                with self.assertRaisesRegex(ValueError, "controlled HTTP transport"):
                    audit.require_model(model)
            self.assertEqual(audit.ledger.read_text(), "")

    def test_existing_policy_cannot_be_refilled_or_rebound(self):
        with tempfile.TemporaryDirectory() as d:
            ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "policy changed"):
                ControlledModelTransport(d, max_requests=2, context_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "policy changed"):
                ControlledModelTransport(d, max_requests=1, context_sha256="1" * 64)

    async def test_incomplete_ledger_fails_closed(self):
        import httpx2

        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64)
            audit.ledger.write_text('{"state":"reserved"')
            async with audit.client_factory(
                None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))
            ) as client:
                with self.assertRaisesRegex(ValueError, "Incomplete HTTP ledger"):
                    await client.post("https://api.example.test/model")


class CaptureBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_sdk_malformed_bytes_and_binding(self):
        import hashlib
        import httpx2
        from openai import AsyncOpenAI

        observed = []
        raw = b'{"id": "malformed", "output": '
        def handler(request):
            observed.append(request.content)
            return httpx2.Response(200, headers={"content-type": "application/json"},
                                   stream=httpx2.ByteStream(raw))
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256="0" * 64,
                                             max_response_bytes=1024)
            client = audit.client_factory(None, transport=httpx2.MockTransport(handler))
            sdk = AsyncOpenAI(api_key="secret-header", http_client=client, max_retries=0,
                              base_url="https://api.example.test/v1?key=secret-query")
            try:
                with audit.bind_request_descriptor("a" * 64):
                    with self.assertRaises(Exception):
                        await sdk.responses.create(model="test", input="private-prompt")
                events = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
                reservation, response = events
                req = Path(d, reservation['request_body_file']).read_bytes()
                res = Path(d, response['response_body_file']).read_bytes()
                self.assertEqual(req, observed[0])
                self.assertEqual(res, raw)
                self.assertEqual(reservation['wire_request_sha256'], hashlib.sha256(req).hexdigest())
                self.assertEqual(reservation['wire_request_bytes'], len(req))
                self.assertEqual(reservation['request_descriptor_sha256'], 'a' * 64)
                self.assertEqual(response['wire_response_sha256'], hashlib.sha256(res).hexdigest())
                self.assertTrue(response['response_capture_complete'])
                self.assertEqual(reservation['attempt_id'], response['attempt_id'])
                self.assertEqual(Path(d, reservation['request_body_file']).stat().st_mode & 0o777, 0o600)
                for secret in ('secret-header', 'secret-query', 'private-prompt'):
                    self.assertNotIn(secret, audit.ledger.read_text())
            finally:
                await sdk.close()

    async def test_stream_cancellation_and_cap_preserve_partial(self):
        import asyncio
        import httpx2
        class Broken(httpx2.AsyncByteStream):
            async def __aiter__(self):
                yield b'prefix'
                raise asyncio.CancelledError()
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0' * 64,
                                             max_response_bytes=100)
            async with audit.client_factory(None, transport=httpx2.MockTransport(
                    lambda _: httpx2.Response(200, stream=Broken()))) as client:
                with self.assertRaises(asyncio.CancelledError):
                    await client.post('https://example.test/', content=b'one')
            events = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
            self.assertFalse(events[1]['response_capture_complete'])
            self.assertEqual(Path(d, events[1]['response_body_file']).read_bytes(), b'prefix')

    async def test_request_stream_and_storage_failure_stop_before_dispatch(self):
        import httpx2
        from private_run_storage import PrivateRunStorage, StorageBudgetExceeded
        called = []
        async def body():
            yield b'body'
        with tempfile.TemporaryDirectory() as d:
            storage = PrivateRunStorage(d, 3000)
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0' * 64,
                                             storage_policy=storage, max_response_bytes=4000)
            async with audit.client_factory(None, transport=httpx2.MockTransport(
                    lambda req: called.append(req) or httpx2.Response(200))) as client:
                with self.assertRaisesRegex(ValueError, 'streaming request'):
                    await client.post('https://example.test/', content=body())
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.test/', content=b'data')
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.test/', content=b'data')
            self.assertEqual(called, [])
            self.assertEqual(audit.ledger.read_text(), '')

    async def test_response_overflow_and_pending_reuse(self):
        import httpx2
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0' * 64,
                                             max_response_bytes=3)
            async with audit.client_factory(None, transport=httpx2.MockTransport(
                    lambda _: httpx2.Response(200, stream=httpx2.ByteStream(b'abcdef')))) as client:
                with self.assertRaisesRegex(ValueError, 'response capture byte limit'):
                    await client.post('https://example.test/')
            events = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
            self.assertFalse(events[1]['response_capture_complete'])
            self.assertEqual(Path(d, events[1]['response_body_file']).read_bytes(), b'abc')

    async def test_interrupted_connection_blocks_reuse_and_policy_drift(self):
        import httpx2
        def fail(request):
            raise httpx2.ConnectError('offline', request=request)
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0' * 64,
                                             max_response_bytes=10)
            async with audit.client_factory(None, transport=httpx2.MockTransport(fail)) as client:
                with self.assertRaises(httpx2.ConnectError):
                    await client.post('https://example.test/')
                with self.assertRaisesRegex(ValueError, 'Incomplete response capture'):
                    await client.post('https://example.test/')
            with self.assertRaisesRegex(ValueError, 'capture policy changed'):
                ControlledModelTransport(d, max_requests=2, context_sha256='0' * 64,
                                         max_response_bytes=11)

    async def test_failed_request_capture_never_dispatches(self):
        import httpx2
        from unittest.mock import patch
        called = []
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256='0' * 64,
                                             max_response_bytes=10)
            async with audit.client_factory(None, transport=httpx2.MockTransport(
                    lambda req: called.append(req) or httpx2.Response(200))) as client:
                with patch.object(audit, '_put_raw_exclusive', side_effect=OSError('disk failure')):
                    with self.assertRaises(OSError):
                        await client.post('https://example.test/', content=b'x')
            self.assertEqual(called, [])
            self.assertEqual(audit.ledger.read_text(), '')

class ReservationAndBindingTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_calls_refuse_while_pending_and_bind_by_task(self):
        import asyncio
        import httpx2
        entered, release = asyncio.Event(), asyncio.Event()
        calls = []
        async def handler(request):
            calls.append(request)
            entered.set()
            await release.wait()
            return httpx2.Response(200, content=b'ok')
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=3, context_sha256='0'*64,
                                             max_response_bytes=10)
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                async def invoke(descriptor):
                    with audit.bind_request_descriptor(descriptor):
                        return await client.post('https://example.test/')
                first = asyncio.create_task(invoke('a'*64))
                await entered.wait()
                with self.assertRaisesRegex(ValueError, 'Incomplete response capture'):
                    await invoke('b'*64)
                release.set()
                await first
                await invoke('b'*64)
            events = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
            self.assertEqual([e['request_descriptor_sha256'] for e in events if e['state'] == 'reserved'], ['a'*64, 'b'*64])
            self.assertEqual(len(calls), 2)

    async def test_journal_reservation_exhaustion_and_reuse(self):
        import httpx2
        from private_run_storage import PrivateRunStorage, StorageBudgetExceeded
        calls = []
        with tempfile.TemporaryDirectory() as d:
            storage = PrivateRunStorage(d, 3500)
            audit = ControlledModelTransport(d, max_requests=3, context_sha256='0'*64,
                                             storage_policy=storage, max_response_bytes=900)
            handler = httpx2.MockTransport(lambda req: calls.append(req) or httpx2.Response(200, content=b'x'))
            async with audit.client_factory(None, transport=handler) as client:
                await client.post('https://example.test/', content=b'x')
                charged = storage._usage()
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.test/', content=b'x')
                self.assertEqual(storage._usage(), charged)
            again = ControlledModelTransport(d, max_requests=3, context_sha256='0'*64,
                                             storage_policy=storage, max_response_bytes=900)
            async with again.client_factory(None, transport=handler) as client:
                with self.assertRaises(StorageBudgetExceeded):
                    await client.post('https://example.test/', content=b'x')
            self.assertEqual(len(calls), 1)

    async def test_response_write_failure_stops_reuse(self):
        import httpx2
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0'*64,
                                             max_response_bytes=10)
            calls = []
            handler = httpx2.MockTransport(lambda req: calls.append(req) or httpx2.Response(200, content=b'ok'))
            original = audit._append_reserved
            def fail_response(stream, event, slot):
                if event['state'] == 'response':
                    raise OSError('journal failure')
                return original(stream, event, slot)
            async with audit.client_factory(None, transport=handler) as client:
                with patch.object(audit, '_append_reserved', side_effect=fail_response):
                    with self.assertRaisesRegex(OSError, 'journal failure'):
                        await client.post('https://example.test/')
                with self.assertRaisesRegex(ValueError, 'unresolved reservation'):
                    await client.post('https://example.test/')
            self.assertEqual(len(calls), 1)
            self.assertEqual(len(audit.ledger.read_text().splitlines()), 1)
            self.assertTrue(list(Path(d).glob('*-journal-reservation.private.bytes')))

    async def test_old_events_remain_old_and_count_toward_cap(self):
        import httpx2
        from bc_core.budget import BudgetExceeded
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=1, context_sha256='0'*64,
                                             max_response_bytes=10)
            old = {'state': 'reserved', 'attempt_id': 'old'}
            audit.ledger.write_text(json.dumps(old) + '\n')
            async with audit.client_factory(None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))) as client:
                with self.assertRaisesRegex(ValueError, 'unverified and charged'):
                    await client.post('https://example.test/')
            with self.assertRaisesRegex(ValueError, 'unverified and charged'):
                ControlledModelTransport(d, max_requests=1, context_sha256='0'*64, max_response_bytes=10)
            self.assertEqual(json.loads(audit.ledger.read_text()), old)

    async def test_binding_validation_restores_nested_scope(self):
        import httpx2
        with tempfile.TemporaryDirectory() as d:
            audit = ControlledModelTransport(d, max_requests=3, context_sha256='0'*64, max_response_bytes=10)
            with self.assertRaises(ValueError):
                with audit.bind_request_descriptor('bad'):
                    pass
            async with audit.client_factory(None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200))) as client:
                with audit.bind_request_descriptor('a'*64):
                    with audit.bind_request_descriptor('b'*64):
                        await client.post('https://example.test/')
                    await client.post('https://example.test/')
                await client.post('https://example.test/')
            rows = [json.loads(s) for s in audit.ledger.read_text().splitlines()]
            self.assertEqual([r['request_descriptor_sha256'] for r in rows if r['state'] == 'reserved'], ['b'*64, 'a'*64, None])

    async def test_response_body_io_failure_preserves_pending_and_charge(self):
        import httpx2
        import os
        from unittest.mock import patch
        from private_run_storage import PrivateRunStorage
        calls = []
        with tempfile.TemporaryDirectory() as d:
            storage = PrivateRunStorage(d, 10000)
            audit = ControlledModelTransport(d, max_requests=2, context_sha256='0'*64,
                                             storage_policy=storage, max_response_bytes=100)
            real_fsync = os.fsync
            def fail_pending(fd):
                if calls and 'response.pending.private.body' in os.readlink(f'/proc/self/fd/{fd}'):
                    raise OSError('response fsync failure')
                return real_fsync(fd)
            def handler(req):
                calls.append(req)
                return httpx2.Response(200, content=b'answer')
            async with audit.client_factory(None, transport=httpx2.MockTransport(handler)) as client:
                with patch('controlled_model_transport.os.fsync', side_effect=fail_pending):
                    with self.assertRaisesRegex(OSError, 'response fsync failure'):
                        await client.post('https://example.test/')
                charged = storage._usage()
                with self.assertRaisesRegex(ValueError, 'Incomplete response capture'):
                    await client.post('https://example.test/')
                self.assertEqual(storage._usage(), charged)
            self.assertEqual(len(calls), 1)
            self.assertTrue(list(Path(d).glob('*-response.pending.private.body')))

    def test_storage_root_must_contain_transport(self):
        from private_run_storage import PrivateRunStorage
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            storage = PrivateRunStorage(root, 10000)
            with self.assertRaisesRegex(ValueError, 'inside the storage root'):
                ControlledModelTransport(outside, max_requests=1, context_sha256='0'*64,
                                         storage_policy=storage, max_response_bytes=10)

class ReconciliationRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_completed_evidence_loss_and_tampering_stop_dispatch_and_reopen(self):
        import httpx2
        for target, change in [('request_body_file', 'delete'), ('response_body_file', 'delete'),
                               ('request_body_file', 'alter'), ('response_body_file', 'alter'),
                               ('journal_reservation_file', 'delete'), ('journal_reservation_file', 'truncate')]:
            with self.subTest(target=target, change=change), tempfile.TemporaryDirectory() as d:
                calls = []
                kwargs = dict(max_requests=3, context_sha256='0'*64, max_response_bytes=32)
                t = ControlledModelTransport(d, **kwargs)
                async with t.client_factory(None, transport=httpx2.MockTransport(
                        lambda req: calls.append(1) or httpx2.Response(200, content=b'answer'))) as c:
                    await c.post('https://example.test/', content=b'input')
                    rows = [json.loads(x) for x in t.ledger.read_text().splitlines()]
                    row = rows[1] if target == 'response_body_file' else rows[0]
                    path = Path(d, row[target])
                    if change == 'delete': path.unlink()
                    elif change == 'alter': path.write_bytes(b'X' * path.stat().st_size)
                    else: path.write_bytes(b'')
                    with self.assertRaises((ValueError, OSError)):
                        await c.post('https://example.test/')
                    with self.assertRaises((ValueError, OSError)):
                        ControlledModelTransport(d, **kwargs)
                    self.assertEqual(calls, [1])
                    self.assertEqual(len(t.ledger.read_text().splitlines()), 2)

    async def test_deleted_pending_sentinel_still_blocks_and_retains_reservation(self):
        import httpx2
        with tempfile.TemporaryDirectory() as d:
            kwargs = dict(max_requests=2, context_sha256='0'*64, max_response_bytes=8)
            t = ControlledModelTransport(d, **kwargs)
            calls = []
            def fail(req):
                calls.append(1)
                raise httpx2.ConnectError('mock', request=req)
            async with t.client_factory(None, transport=httpx2.MockTransport(fail)) as c:
                with self.assertRaises(httpx2.ConnectError): await c.post('https://example.test/')
                row = json.loads(t.ledger.read_text())
                Path(d, row['response_pending_file']).unlink()
                with self.assertRaisesRegex(ValueError, 'unresolved reservation'): await c.post('https://example.test/')
                with self.assertRaisesRegex(ValueError, 'unresolved reservation'): ControlledModelTransport(d, **kwargs)
            self.assertEqual(calls, [1])
            self.assertEqual(json.loads(t.ledger.read_text()), row)

    async def test_terminal_order_and_missing_metadata_fail_closed(self):
        import httpx2
        with tempfile.TemporaryDirectory() as d:
            kwargs = dict(max_requests=2, context_sha256='0'*64, max_response_bytes=8)
            t = ControlledModelTransport(d, **kwargs)
            async with t.client_factory(None, transport=httpx2.MockTransport(lambda _: httpx2.Response(200, content=b'x'))) as c:
                await c.post('https://example.test/')
            rows = t.ledger.read_text().splitlines()
            t.ledger.write_text('\n'.join(reversed(rows)) + '\n')
            with self.assertRaises(ValueError): ControlledModelTransport(d, **kwargs)
            t.ledger.write_text('\n'.join(rows) + '\n')
            Path(d, 'http-capture-policy.private.json').unlink()
            with self.assertRaisesRegex(ValueError, 'policy missing'): ControlledModelTransport(d, **kwargs)

    def test_private_modes_and_unsafe_existing_files(self):
        import os, stat
        with tempfile.TemporaryDirectory() as d:
            old = os.umask(0o022)
            try: t = ControlledModelTransport(d, max_requests=2, context_sha256='0'*64)
            finally: os.umask(old)
            for name in ('http-attempts.private.jsonl', 'http-policy.private.json', 'http-capture-policy.private.json'):
                self.assertEqual(stat.S_IMODE(Path(d, name).stat().st_mode), 0o600)
            Path(d, 'http-policy.private.json').chmod(0o644)
            with self.assertRaisesRegex(ValueError, 'unsafe private file'):
                ControlledModelTransport(d, max_requests=2, context_sha256='0'*64)
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'http-attempts.private.jsonl').symlink_to('/dev/null')
            with self.assertRaises(OSError): ControlledModelTransport(d, max_requests=1, context_sha256='0'*64)
        with tempfile.TemporaryDirectory() as d:
            Path(d).chmod(0o755)
            with self.assertRaisesRegex(ValueError, 'owned private directory'):
                ControlledModelTransport(d, max_requests=1, context_sha256='0'*64)

    def test_missing_ledger_hardlinks_and_storage_policy_drift(self):
        import os
        from private_run_storage import PrivateRunStorage
        with tempfile.TemporaryDirectory() as d:
            kwargs = dict(max_requests=2, context_sha256='0'*64)
            t = ControlledModelTransport(d, **kwargs)
            t.ledger.unlink()
            with self.assertRaisesRegex(ValueError, 'ledger missing'):
                ControlledModelTransport(d, **kwargs)
        with tempfile.TemporaryDirectory() as d:
            kwargs = dict(max_requests=2, context_sha256='0'*64)
            ControlledModelTransport(d, **kwargs)
            os.link(Path(d, 'http-policy.private.json'), Path(d, 'link'))
            with self.assertRaisesRegex(ValueError, 'unsafe private file'):
                ControlledModelTransport(d, **kwargs)
        with tempfile.TemporaryDirectory() as d:
            storage = PrivateRunStorage(d, 10000)
            kwargs = dict(max_requests=2, context_sha256='0'*64, storage_policy=storage)
            ControlledModelTransport(d, **kwargs)
            Path(d, '.storage-policy.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'storage policy drift'):
                ControlledModelTransport(d, **kwargs)
