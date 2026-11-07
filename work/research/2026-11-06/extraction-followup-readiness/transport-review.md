The isolated backend can be used without installing or modifying `bc-modules`. Its OpenAI resolver constructs `AsyncOpenAI(max_retries=0)` and accepts the controlled HTTP client factory. The safe integration must also wrap the resolver with `require_model`: passing the factory alone does **not** make that check automatic.

I verified that exact factory-and-resolver path offline with a mock HTTP transport: the isolated backend loaded, the SDK reported zero retries, the SDK held the controlled client, a mocked 503 produced one reservation and one response, and a second request stopped at the cap before reaching the mock transport. The existing transport tests passed **6/6**, and resumable extraction tests passed **12/12**. No paid API calls or repository edits were made.

### Runtime integration

Use an isolated process with the desired `bc-llm` source first on its import path; keep the existing environment for its dependencies. Confirm the actual imported paths and hashes before a run:

```bash
PYTHONPATH=/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python:scripts \
  /home/mjbommar/projects/bc/bc-modules/.venv/bin/python -B your_runner.py
```

The tested isolated checkout is commit `d5acda100a0999267eaa150e0017130666cb28d4`; its backend file SHA-256 is `0f274573a86a1539317b51d9be1d93a012ce5395987ce113341aca88964c4690`. Pin and verify the dependencies as well: `require_model` intentionally depends on the SDK’s private `_client` attribute.

A runner can use this construction:

```python
from bc_llm import ModelSpec, RoleRegistry, PydanticAIBackend
from controlled_model_transport import ControlledModelTransport

# Created and admitted under the private storage policy before construction.
audit = ControlledModelTransport(
    private_http_directory,
    max_requests=HTTP_CAP,
    context_sha256=FROZEN_RUN_MANIFEST_SHA256,
)

spec = ModelSpec(
    model="openai:gpt-6-sol",
    reasoning_effort="low",
    max_tokens=6000,
    timeout_s=90.0,
    output_mode="native",
)
registry = RoleRegistry(roles={"extractor": spec})

backend = PydanticAIBackend(
    registry,
    http_client_factory=audit.client_factory,
    max_attempts=1,
    agent_retries=0,
    max_model_requests=1,
    flex_fallback=False,
    # Supply the run's retained accounting ledger and pricing as appropriate.
)

resolve = backend._resolve_model

def checked_resolver(requested_spec):
    if requested_spec != spec:
        raise ValueError("Unexpected model specification")
    return audit.require_model(resolve(requested_spec))

backend.model_resolver = checked_resolver

# Preflight before extraction; requires configured credentials but sends no request.
checked_resolver(spec)

try:
    # await extract_document_resumable.run(..., backend=backend, ...)
    ...
finally:
    await backend.aclose()
```

`_resolve_model` is a private backend method, so this is a pinned integration, not a stable public API. The wrapper must remain the resolver used by the backend; a custom resolver takes responsibility for its own SDK settings. The factory receives the backend’s resolved proxy setting. Freeze and inspect that setting too.

Pass `run()` a complete `model_identity`, explicit `today`, `max_calls`, and a positive `budget_policy` with `max_usd` and `reservation_usd`. Its context binds the document, cells, configuration, schema and relevant source/template hashes. Its call reservations persist across restarts, including failures; successful cache entries are validated on reuse. See [extract_document_resumable.py](/home/mjbommar/projects/personal/moratorium-data-2026/scripts/extract_document_resumable.py:45).

### Blockers and limits before a new evaluation

- **A new frozen run manifest and cohort are needed.** Bind the HTTP ledger to a SHA-256 of that immutable manifest, including the transport and backend hashes, dependency versions, model settings, proxy policy and caps. Do not reuse the old evaluation as a fresh independent holdout. The old protocol’s adapter hash also differs from the current file.
- **Decide cap scope explicitly.** One shared admitted HTTP directory gives a persistent cap across all clients/cases using it; separate directories give per-directory caps and do not enforce a campaign-wide total. Keep the manifest-to-ledger mapping and reconcile reservations and responses afterward. An interrupted or connection-failed reservation still consumes the cap.
- **The dollar reservation is not a hard provider spending ceiling.** The adapter stops and retains actual cost when a successful call exceeds its reservation; failed or interrupted calls retain the reservation but can have unknown provider cost. Select a conservative reservation and reconcile provider records. The backend’s successful-call ledger is not an HTTP-attempt ledger, and its ledger callback failures are logged rather than fatal.
- **Verify the full production path offline before spending.** The existing real-SDK test constructs its own SDK and custom resolver; my additional mock check exercised the isolated backend factory path, but did not run a complete domain extraction with the actual new runner. Test that runner end-to-end with mock transport, including restart, cap exhaustion, failure, cache replay, and the extractor’s retry behavior. Confirm every provider request travels through the checked client and that no alternate provider or tool path is enabled.
- **Protect and retain the workspaces.** The extraction workspace contains source text and outputs. The transport ledger omits prompts, credentials, bodies and URL queries, but records host, method, timestamps and status. Create private directories with suitable ownership and permissions before use; `mkdir(..., mode=0o700)` does not repair permissions on an existing directory.

The old [SDK retry audit](/home/mjbommar/projects/personal/moratorium-data-2026/work/research/2026-11-06/frozen-domain-evaluation/sdk-retry-audit.json) observed the earlier default SDK retry count of two. Its provider-attempt count remains unknown; the new mechanism cannot retroactively establish that the old thirteen-request HTTP cap was met.