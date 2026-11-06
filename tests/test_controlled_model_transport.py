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
                with self.assertRaises(BudgetExceeded):
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
