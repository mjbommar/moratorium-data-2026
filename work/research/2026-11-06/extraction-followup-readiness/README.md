# Extraction follow-up readiness

Two terminal Codex CLI jobs requested `gpt-6.1-terra`: a [contract audit](contract-review.md) and a [transport audit](transport-review.md). Their event-stream/report hashes are retained in [validation.json](validation.json). Requested model identity is recorded, not independently provider-attested. These are development reviews, not independent ground truth or a passing extraction evaluation.

## Verified transport progress

The coordinator independently exercised the isolated patched bc-llm backend's actual default OpenAI resolver with its HTTP client factory and the mandatory `require_model` wrapper. [Preflight](preflight.json) records zero SDK retries, one mocked 503 request, and a second generation invocation stopped by the persistent request cap before transport. All six existing controlled-transport tests passed. No extraction-provider requests were sent. The distributed Codex reviews are separate model work, not included in that zero-request statement.

Reproduce from the repository root with the existing bc-modules environment and the pinned isolated retry-fix checkout:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/extraction-followup-readiness/preflight.py
```

The script uses only `httpx2.MockTransport`, a dummy credential, and a temporary ledger. It imports the isolated bc-llm source without installation. Compare the reported module path and SHA-256 with the receipt; changed dependencies require renewed verification. Neither bc-modules checkout was edited. This checks backend integration, not a complete domain-runner failure/restart/replay cycle. HTTP attempt caps and estimated dollar reservations are different controls; this test establishes no provider invoice ceiling. The previous evaluation's missing HTTP-attempt accounting remains unresolved historically.

## Fidelity blocker identified

The canonical threshold array and extraction target represent individual numbers but have no typed compound-clause operator or cardinality. Source-reviewed Mandan distinguishes capacity OR demand for a proposed prohibition from capacity AND demand each below the threshold for a separate provision. Harwood distinguishes any one major trigger from at least two moderate triggers, subject to discretionary approval, and preserves a compound water comparison. Prose can retain those meanings; flat numeric arrays alone cannot establish complete structured extraction.

The historical evaluator's scalar threshold-slot matcher also cannot prove complete-group recall. Thus merely testing the improved prompt on another numeric source would not address this blocker. The next development increment must version the condition/group contract, preserve clause purpose and source support, and score complete groups with AND/OR/cardinality and contradictory-member checks. Existing flat records must remain semantically unspecified rather than silently assigned a conjunction. Mandan and Harwood are known development cases, not unseen holdout material.

Before new extraction calls, complete the full runner's offline transport tests, then freeze code/schema/source hashes, cohort provenance, required semantic slots, adjudication rules and persistent campaign-wide caps. Do not refill the previous evaluation or source-job budgets. No new paid extraction protocol or workspace has been admitted by this packet.

The historical quality result remains **32/36 supported (88.9%), below 95%; 0/3 documents review-ready**. Canonical data, headline counts, publication generations and release status are unchanged.
