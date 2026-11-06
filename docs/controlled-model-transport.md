# Controlled extraction HTTP transport

The frozen extraction trial exposed implicit OpenAI SDK retries. Its original
provider-attempt count remains unknown; subsequent controls do not change that
historical result or its four unresolved semantic ambiguities.

The shared-library fix is bc-modules commit `d5acda10` on
`fix/openai-sdk-retry-controls`. It disables SDK retries for the default OpenAI
resolver. Caller-owned resolvers remain responsible for their SDK configuration.
The original shared checkout and installed environment have not been replaced.

`scripts/controlled_model_transport.py` adds a persistent HTTP reservation ledger.
Use an existing private workspace admitted under the applicable storage policy.
The helper does not create that directory. Bind its policy to the frozen context
SHA256 and a positive request limit. Reservations are flushed before dispatch;
failed connections and interruptions consume their reserved allowance. Reopening
the workspace cannot refill its budget or change the context. Torn histories
stop execution. Redirects are disabled.

For a patched default resolver, compose the controls as follows (the application
must supply its admitted directory, context hash and model specification):

```python
controller = ControlledModelTransport(
    private_directory, max_requests=13, context_sha256=context_sha256
)
async with PydanticAIBackend(
    registry=registry,
    max_attempts=1,
    agent_retries=0,
    max_model_requests=1,
    flex_fallback=False,
    http_client_factory=controller.client_factory,
) as backend:
    controller.require_model(backend.model_resolver(spec))
    # Run the explicitly frozen extraction workload with this backend.
```

Run `require_model` for each distinct model before extraction. It rejects SDK
retry settings other than zero and models whose HTTP client is not observed by
this controller. The check intentionally depends on the pinned SDK's client
layout and must be revalidated on upgrades. A caller-owned resolver can instead
construct `AsyncOpenAI(max_retries=0, http_client=...)` explicitly; that caller
also owns closing its clients.

The private ledger retains method, host, scheme, port, timestamps, reservation
IDs and response status. It excludes paths, queries, headers and source/model
bodies. This is a request ceiling, not complete invoice accounting. Existing
backend dollar reservations, model-request limits and review gates still apply.

Verification uses the real OpenAI SDK with a mock HTTP transport: a retryable
503 consumes one request, a subsequent invocation stops at the retained cap,
and connection failures cannot refund allowance. Policy drift, reopening,
unobserved clients and torn ledgers have separate tests. No paid request or
canonical data promotion is needed for these checks.
