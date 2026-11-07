# Compound-condition development and verification

This increment implements the representation/scoring blocker identified by the
[readiness review](../extraction-followup-readiness/README.md). The
[contract documentation](../../../../docs/compound-condition-development.md)
describes optional profile 1.0.3, native extraction transport 1.2.0, semantics,
versioning, source-location checks and continuing scope limits.

Three distributed Codex CLI jobs requested `gpt-6.1-terra`: implementation,
in-progress review and final review. [Validation](validation.json) pins their
terminal event/report hashes and distinguishes requested model from independent
provider attestation. The [initial review](initial-review.md) identified schema,
unknown-text scoring, invalid-neighbor retention and mutable replay issues. The
coordinator fixed those issues; the [final review](final-review.md) reported no
remaining actual bug in its inspected scope and passed 144 tests/26 subtests.
Those reports describe their observed checkpoints; coordinator validation below
includes the final code and additional full-runner preflight.

The coordinator's complete suite passes **340 tests**. `make data site check`
finishes with **zero errors, 491 warnings and 53 matching documented numbers**.
Exact byte comparisons confirm both legacy CSVs, the identity registry, canonical
pointer, old schemas and all eighteen CSV table views are unchanged. The derived
CSV generation changes because its manifest pins the changed generator code.
The new profile and schema are available, but the authoritative publication still
selects profile **1.0.2**. No record or interpretation was silently migrated.

The [full-runner preflight](full-runner-preflight.py) uses the real isolated
retry-fix bc-llm backend, OpenAI SDK, controlled HTTP ledger and bc-evidence
pipeline against synthetic data and `httpx2.MockTransport`. It verifies:

- a compound candidate survives the full native parsing/extraction path;
- successful cache replay after rebuilding backend/client sends no extra request;
- a separate extraction workspace cannot refill the shared HTTP cap;
- a mocked failure retains both the extraction and HTTP reservations;
- restarting a failed run cannot refill its adapter request cap.

[Results](full-runner-preflight.json) contain no source/model payloads. The
script's inputs and returned content are explicitly synthetic. Dummy credentials,
mock HTTP and temporary directories ensure no provider requests. Its fixture
pricing is for control-flow testing, not current provider pricing or spending
estimates. The isolated backend checkout remains pinned as documented in the
preceding readiness packet; no global installation was performed.

Reproduce from the repository root:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/compound-condition-development/full-runner-preflight.py
```

The next work is source-adjudicated development clauses followed by a separately
frozen evaluation driver, source cohort, group-level slots, model/pricing and
persistent caps. The historic quality gate remains failed: 32/36 supported,
11/12 scalar slots and zero review-ready documents. This increment measures
software/control behavior, not extraction accuracy, discovery recall, legal
force, final ballot qualification or overall refresh completion.
