# Typed domain extraction calibration: Peru

This packet tests the actual bc-evidence chunk pipeline with field-specific
electoral/proposal candidate types. It does not promote facts or establish legal
force. Both runs used the same complete registered OCR of the one-page official
proposal. Printed clauses were visually checked; the handwritten date/signature
area remains unreliable. The underlying source and text hashes are pinned in
each receipt.

## Implementation

`scripts/extract_domain_candidates.py` extends bc-evidence's claim/chunk models
with field candidates and explicit unresolved-field notes. The provider-facing
transport derives field-specific enums, scalar/list types, durations, thresholds
and date bounds from the expanded schema. The serialized transport is
`work/schemas/extraction/1.0.0.json`; it is an extraction schema, not a new
canonical table. Current targets are elections, ballot measures, provisions and
source-reported result fields. Local-restriction/event adapters and source-labelled
vote-category/total attachments remain future work.

The existing resumable adapter supplies actual bc-evidence map/reduce, durable
call/dollar reservations, schema-validated caches and chunk coverage. Domain
processing additionally checks canonical table/field pairs and property schemas,
preserves exact quote occurrences and source hashes, and flags ambiguous
locations, alternative field values and proposal-only assertions. Canonical IDs,
derived outcomes, supersession and review/claim references cannot be generated
through the extraction field allowlist. No candidate is automatically accepted.

## Live calibration results

| Run | Candidates | Field-schema valid | Located quotes | Estimated cost | Replay calls |
|---|---:|---:|---:|---:|---:|
| Initial broad value union | 8 | 5 | 8 | $0.045502 | 0 |
| Field-specific discriminated transport | 10 | 10 | 10 | $0.061662 | 0 |

Each live run made one backend call using explicitly pinned
`openai:gpt-6-sol`, low effort, native output and a 6,000-token output ceiling.
Each workspace allowed at most two calls, with $0.25 reserved per attempt and
$0.50 total allocations. The two calibration workspaces therefore had a combined
$1.00 allocation ceiling; actual local-table estimated spend was $0.107164.
These estimates are not provider invoices. Model output and API-call ledgers
remain private in the receipt-named workspaces. Source snapshots of both adapters
and the drivers are retained there so later code changes do not erase the
executed versions. Changed contexts reject ordinary cache reuse.

The initial run returned list fields as strings and a mechanism as prose. Those
three candidates were retained as invalid, without coercion or promotion. The
second transport fixed these response shapes, but exposed a substantive error:
the model inferred `yes_direction=restricts` from the restrictive proposal even
though voter-facing wording remains unavailable. That inference is withheld.
Canonical Peru polarity was rechecked and remains `unresolved`.

The final validator flags proposal-only election assertions as requiring
election-specific evidence. It was applied offline to the preserved second-run
outputs, with its own code hash and zero model calls; `review.json` records this
separate review step. Schema validity and quote location are explicitly
insufficient for acceptance.

The second run also nominated multiple representations of duration and covered
uses. These remain separate candidates. Their review flags identify a need to
resolve representation/scope, not proof of contradictory source facts. Conditional
180-day terms remain distinct from any actual passage or effective date.

Eleven domain contract tests cover actual-pipeline replay, field-specific shapes,
source hashes, strict counts, date formats, thresholds, unsupported field pairs,
ambiguous/unlocated quotes, alternative values, stale outputs and the proposal
polarity evidence gap. The full repository test result is recorded separately.
Broader ballot/result calibration, numerical/textual entailment, identity review,
current legal history and substantive promotion remain unfinished.
