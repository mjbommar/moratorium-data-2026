# Controlled extraction HTTP transport

The frozen extraction trial exposed implicit OpenAI SDK retries. Its original
provider-attempt count remains unknown; subsequent controls leave that historical
result and its unresolved semantic findings intact.

The shared-library retry fix is available at bc-modules commit `d5acda10` on
`fix/openai-sdk-retry-controls`. Its default OpenAI resolver disables SDK retries.
The original shared checkout and installed environment were preserved. Explicit
caller-owned resolvers must configure their SDK and pass the controller checks.

`scripts/controlled_model_transport.py` retains private HTTP evidence and a
persistent reservation ledger. Create an owned, non-symlink directory with mode
0700 under the admitted storage policy before constructing the controller.
Retained metadata and artifacts require restrictive ownership and permissions.
Bind the request limit and context hash to the prospectively frozen workload;
reopening cannot refill capacity or change those values.

For a patched default resolver, compose the controls as follows. The caller
supplies its admitted directory, frozen context hash and model specification.

```python
controller = ControlledModelTransport(
    private_directory, max_requests=13, context_sha256=context_sha256,
    storage_policy=storage_policy,
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
    # Pass request_binding=controller.bind_request_descriptor to
    # extract_rule_units.run(...) for each logical invocation's scoped hash.
    # Execute only the separately admitted, frozen workload.
```

The example's ceiling is illustrative. Actual call and dollar limits, source
cohort, model/settings, storage limits and evaluation protocol must be frozen
before dispatch. `require_model` checks each distinct model's SDK retries are
zero and its HTTP client is observed by this controller. Revalidate that check
when changing the pinned SDK. A caller-owned resolver can construct
`AsyncOpenAI(max_retries=0, http_client=...)` explicitly and owns client closure.

Capture format `controlled-model-capture-2` writes the serialized request body
before dispatch and the response body before SDK validation. Separate private
body files retain the original bytes and hashes. Journal metadata contains the
method, host, scheme, port, timestamps, UUID attempt, status, lengths, hashes and
capture completeness; HTTP headers and URL paths/queries are excluded from that
metadata. Raw bodies remain private under the applicable Data0 storage policy.
The scoped logical request-descriptor hash remains distinct from the wire-body
hash. Binding scopes propagate through asyncio context variables; keep the scope
around the awaited logical call.

Request and response byte limits are positive and persistent. Unsupported
streaming requests are rejected. Responses are buffered before validation;
partial, interrupted or oversized responses remain incomplete. Reservations
cover response and journal capacity before dispatch under the cooperative storage
lock. Failed or uncertain attempts retain their charges. Logical quota reservation
does not guarantee physical allocation or writes after dispatch; post-dispatch
I/O failures require explicit reconciliation.

On reopening and before another dispatch, the controller checks current-format
event ordering, terminal linkage, required artifacts, sizes, hashes and retained
capacity. Missing or changed bodies, deleted pending sentinels, orphaned files,
torn histories and unresolved reservations stop reuse. Older histories remain
unverified and charged until explicitly reconciled. Redirects are disabled.
Preserve all original ledgers and caps; never synthesize captures or reset a
namespace to bypass an exhausted allowance.

The extractor and prospective audit both separate
`boundary_output_accounting_complete` from `response_accounting_complete`.
End-to-end completeness remains false pending a verified journal adapter and
raw-to-boundary provenance. Known generated clauses, unknown cardinalities,
failed/interrupted attempts and unattempted planned units remain visible. The
blocked audit prints JSON evidence and exits nonzero; quality remains
`not_scored`. Invoice reconciliation, semantic review, a frozen prospective
protocol and fresh calibration/unexposed holdout remain required.

The [development packet](../work/research/2026-11-07/controlled-capture-development/README.md)
records exact code hashes and bounded offline verification. Independent follow-up
passed 70 tests and 54 subtests, including corruption, privacy and native SDK
mock cases, and found the extractor packet's boundary-accounting naming issue.
Root corrected that issue; 61 focused tests and 54 subtests pass afterward, with
no provider calls. The final small packet-field change has not received a second
independent review. These checks establish local development behavior; P4 quality
acceptance and automatic extraction remain open.
