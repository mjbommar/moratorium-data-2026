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
    # extract_rule_units.run(...) for each logical invocation's scoped hash and persisted invocation ID.
    # Execute only the separately admitted, frozen workload.
```

The example's ceiling is illustrative. Actual call and dollar limits, source
cohort, model/settings, storage limits and evaluation protocol must be frozen
before dispatch. `require_model` checks each distinct model's SDK retries are
zero and its HTTP client is observed by this controller. Revalidate that check
when changing the pinned SDK. A caller-owned resolver can construct
`AsyncOpenAI(max_retries=0, http_client=...)` explicitly and owns client closure.

Capture format `controlled-model-capture-3` writes the serialized request body
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
In the earlier normalized bundle, end-to-end completeness remains false; the
prospective native path below separately verifies journal and raw-to-boundary
provenance. Known generated clauses, unknown cardinalities,
failed/interrupted attempts and unattempted planned units remain visible. The
blocked audit prints JSON evidence and exits nonzero; quality remains
`not_scored`. Invoice reconciliation, semantic review, a frozen prospective
protocol and fresh calibration/unexposed holdout remain required.

The preceding [capture development packet](../work/research/2026-11-07/controlled-capture-development/README.md) remains historical. The [native reader increment](../work/research/2026-11-07/native-journal-reader-development/README.md) adds durable logical invocation IDs, strict raw/boundary comparison and read-only journal reconciliation. State format `rule-unit-state-2` rejects incompatible retained state; no migration or namespace reset is implied.

Independent verification accepted the bounded reader fixes after nine fresh synthetic replay scenarios. Seven offline suites passed 88 tests and 60 subtests; the coordinator reran those suites successfully. Retained-file consistency is deliberately separate from complete historical dispatch/output accounting. Unobserved work and unknown cardinality remain incomplete, observed counts are lower bounds, and CLI incompleteness exits nonzero. The workspace threat model is cooperative, not protection against a hostile owner rewriting history.

At that reader increment, endpoint/wire verification and prospective audit integration remained open. The prospective path below addresses those accounting checks for newly witnessed runs. Source/role semantics and fresh frozen calibration/holdout remain required. These offline checks do not establish model quality or P4 acceptance.

The bounded endpoint/wire increment records `openai-official-responses-https-1`
only when the observed, normalized `httpx2.Request` is POST over HTTPS to
`api.openai.com`, with the normalized default port, raw path exactly
`/v1/responses` (including no query delimiter), and empty normalized userinfo.
The library normalizes host case and explicit port 443; it also erases an empty
userinfo delimiter, so an original `https://@api.openai.com/v1/responses` is
indistinguishable at this boundary from the spelling without `@`. The original
URL spelling cannot be reconstructed here; rejecting even an empty `@` would
require validation of the original input at an earlier trusted boundary. This
identifier observes the requested address; it does not authenticate the
provider, TLS peer, DNS, proxy, or dispatch history. Other addresses, including
nonempty userinfo or query, alternate ports, and other paths, remain unverified
by this contract. No arbitrary path, query, userinfo or header is journaled.
Unknown endpoints get no identifier. Old capture-3 reservations remain readable and
charged but cannot acquire an endpoint identifier retrospectively. The reader
exposes the observed identifier without treating it as an independently trusted
pre-dispatch witness or declaring complete history.

`native_rule_unit_wire_contract.compare_frozen_request` is an offline, async,
per-request comparison helper, not prospective audit integration. It requires
an independently frozen context whose model identity contains both `model` and
`native_wire_profile: native-rule-unit-default-spec-offline-1`. This profile
fixes native output, the default `ModelSpec`, empty extractor settings, no tools,
no attachments, no retries and the source-pinned local SDK serialization path.
It checks source bytes and rebuilds the context from the extractor, then invokes
the real backend and SDK through an explicit dummy key and `MockTransport`.
The entire emitted JSON is compared with strict type-sensitive JSON parsing;
no fields are dropped, and SDK schema transformations are included. A mismatch
returns false; malformed JSON, missing profile, changed source/context or SDK
pins fail closed. The caller must independently anchor and supply the original
frozen context and observed request bytes; the helper cannot authenticate either
or establish that the profile was obeyed before dispatch. Existing contexts that
only identify the model lack a frozen model specification and SDK profile and
cannot be retroactively verified. No complete historical or P4 claim follows.

The [endpoint/wire development receipt](../work/research/2026-11-07/native-wire-contract-development/README.md) records independent acceptance of this bounded component and storage-test reconciliation. Ten selected offline suites passed 108 tests, with no failures, errors or reported skips. This supersedes the two obsolete storage-fixture failures as a current test result, while preserving their historical logs. The subsequent prospective integration is described below; semantic and holdout gates remain open.

## Prospective native trial witness

For a new, unspent run, build the exact context with `extract_rule_units.prepare`
using an explicit identity such as
`{'model': 'openai:gpt-6.1-terra', 'native_wire_profile': 'native-rule-unit-default-spec-offline-1'}`
and empty settings. `native_rule_unit_wire_contract.workload(context)` commits to
that entire context and the ordered logical request hashes, one dispatch per
unit. Independently retain and pin `extract_rule_units.digest(workload)` before
dispatch; supply both the frozen workload and this independently held hash to
`run(..., prospective_workload=workload, workload_sha256=hash, request_binding=controller.bind_request_descriptor)`.
The caller must establish the independent pin before execution. A hash created
only from a post-dispatch journal is not a prospective witness.

The controller policy must use the context digest and a request cap equal to the
number of planned units; `max_calls` must equal that count. The extractor checks
the pinned SDKs, default native model spec, backend retries and request limit,
resolved model and controlled client before touching the run state. It retains
the witness before reserving a logical attempt, refuses to attach it to an
existing history, requires it again on resume and does not retry a failed unit.
The ordinary non-prospective interface remains available for historical work but
cannot acquire a prospective witness after the fact. Failed and uncertain
reservations remain charged. This profile's offline compatibility with
`gpt-6.1-terra` is not a semantic evaluation or authorization to spend.

For a quiescent run, invoke `audit_rule_unit_trial.py --run-dir RUN --http-dir
HTTP --source-body BODY --witness WITNESS --anchor INDEPENDENT_SHA256
--http-policy POLICY --capture-policy CAPTURE_POLICY`. The three JSON inputs and
source body are owner-private files. The witness is the independently retained
pre-dispatch object, not a reconstruction from the run. The native audit uses the
read-only reader, matches the exact committed dispatch sequence and descriptor
bindings, checks requested endpoint observations, compares each captured wire
request with the existing pinned offline SDK serializer, and compares complete
raw responses to boundary outputs. It reports observed lower bounds even when a
check fails. The reader's historical-cardinality fields remain conservative;
completion of this prospective trace is conditioned on the cooperative operator
and independent pre-dispatch pin, not protection against a workspace owner
rewriting all evidence. Audit a stopped/quiescent run; this is not a cross-file
snapshot against concurrent mutation.

The endpoint identifier observes a normalized requested address; it does not
authenticate a provider, TLS peer, DNS or proxy. A successful accounting trace
still returns quality `not_scored` and a nonzero CLI exit: source/role/condition
semantics, independent review, the original frozen protocol and thresholds,
fresh calibration and an unseen holdout remain required. The old failed and
exposed VA work remains failed, exposed and spent; neither these offline checks
nor a new profile establish P4 acceptance.
