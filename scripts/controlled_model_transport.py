"""Persistent, credential-free HTTP request caps for explicit OpenAI extraction runs.

The caller admits/creates the private workspace under its storage policy first.
No prompts, headers, bodies or URL queries are written to this ledger.
"""

import fcntl
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4


class ControlledModelTransport:
    def __init__(self, directory, *, max_requests, context_sha256, storage_policy=None):
        self.directory = Path(directory)
        self.storage_policy = storage_policy
        if not self.directory.is_dir():
            raise ValueError(
                "Create an admitted private workspace before configuring HTTP transport"
            )
        if type(max_requests) is not int or max_requests < 1:
            raise ValueError("HTTP request cap must be a positive integer")
        if (
            not isinstance(context_sha256, str)
            or len(context_sha256) != 64
            or any(c not in "0123456789abcdef" for c in context_sha256)
        ):
            raise ValueError("Frozen context SHA256 required")
        self.policy = {
            "schema_version": "controlled-model-http-1",
            "max_requests": max_requests,
            "context_sha256": context_sha256,
        }
        self.ledger = self.directory / "http-attempts.private.jsonl"
        self.clients = []
        # The policy and reservations share one lock so concurrent constructors
        # cannot silently replace an earlier cap or refill a retained workspace.
        with self.ledger.open("a+") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            policy_path = self.directory / "http-policy.private.json"
            if policy_path.exists():
                if json.loads(policy_path.read_text()) != self.policy:
                    raise ValueError(
                        "HTTP workspace policy changed; inspect retained reservations"
                    )
            else:
                stream.seek(0)
                if stream.read():
                    raise ValueError("HTTP ledger has no retained policy")
                if self.storage_policy is not None:
                    self.storage_policy.save_json(policy_path.absolute(), self.policy, exclusive=True)
                else:
                    with policy_path.open("x") as target:
                        json.dump(self.policy, target, sort_keys=True)
                        target.write("\n")
                        target.flush()
                        os.fsync(target.fileno())

    @staticmethod
    def events(stream):
        stream.seek(0)
        raw = stream.read()
        if raw and not raw.endswith("\n"):
            raise ValueError("Incomplete HTTP ledger; reconcile before continuing")
        rows = [json.loads(s) for s in raw.splitlines()]
        reserved = {r["attempt_id"] for r in rows if r["state"] == "reserved"}
        responded = [r["attempt_id"] for r in rows if r["state"] == "response"]
        if (
            len(reserved) != sum(r["state"] == "reserved" for r in rows)
            or len(responded) != len(set(responded))
            or not set(responded) <= reserved
            or any(r["state"] not in ("reserved", "response") for r in rows)
        ):
            raise ValueError("Invalid HTTP ledger history")
        return rows

    def append(self, stream, event):
        if self.storage_policy is not None:
            self.storage_policy.append_jsonl_stream(stream, event)
            return
        stream.seek(0, 2)
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

    async def before_request(self, request):
        from bc_core.budget import BudgetExceeded

        with self.ledger.open("a+") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            rows = self.events(stream)
            if (
                json.loads((self.directory / "http-policy.private.json").read_text())
                != self.policy
            ):
                raise ValueError("HTTP policy drift; stop and reconcile the workspace")
            if (
                sum(r["state"] == "reserved" for r in rows)
                >= self.policy["max_requests"]
            ):
                raise BudgetExceeded(
                    "Persistent provider HTTP request cap reached", "llm"
                )
            ident = uuid4().hex
            self.append(
                stream,
                {
                    "state": "reserved",
                    "attempt_id": ident,
                    "method": request.method,
                    "scheme": request.url.scheme,
                    "host": request.url.host,
                    "port": request.url.port,
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            request.extensions["controlled_model_attempt_id"] = ident

    async def after_response(self, response):
        ident = response.request.extensions.get("controlled_model_attempt_id")
        with self.ledger.open("a+") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            rows = self.events(stream)
            if not ident or not any(
                r["state"] == "reserved" and r["attempt_id"] == ident for r in rows
            ):
                raise ValueError("Provider response lacks a prior HTTP reservation")
            if any(r["state"] == "response" and r["attempt_id"] == ident for r in rows):
                raise ValueError("Repeated provider response event")
            self.append(
                stream,
                {
                    "state": "response",
                    "attempt_id": ident,
                    "status": response.status_code,
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                },
            )

    def client_factory(self, proxy, *, transport=None):
        import httpx2

        client = httpx2.AsyncClient(
            proxy=proxy,
            transport=transport,
            follow_redirects=False,
            event_hooks={
                "request": [self.before_request],
                "response": [self.after_response],
            },
        )
        self.clients.append(client)
        return client

    def require_model(self, model):
        sdk = getattr(model, "client", None)
        if getattr(sdk, "max_retries", None) != 0:
            raise ValueError(
                "Provider SDK retries must be explicitly zero before extraction; update bc-llm"
            )
        # A pinned SDK integration check: reject opaque/unobserved transports,
        # rather than assuming that a backend-level limit observes HTTP retries.
        if not any(getattr(sdk, "_client", None) is client for client in self.clients):
            raise ValueError(
                "Provider model does not use this controlled HTTP transport"
            )
        return model
