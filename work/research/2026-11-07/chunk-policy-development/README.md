# Explicit extraction chunk policy: development checkpoint

The resumable adapter now accepts explicit `chunk_size` and `chunk_overlap`, pins
resolved values in the cache context, and forwards them to a compatible native
bc-evidence extractor. Changed policies reject cache reuse. Unsupported overrides
fail before requests; ordinary calls retain the installed runtime's defaults.
The new native API is isolated at commit
`9eeb6bfbb3496a471236177f1676a9d72d39a26e`, in
[draft bc-modules PR6](https://github.com/bommarito-consulting/bc-modules/pull/6).
No original checkout or installed package was modified. No new chunking algorithm
was implemented: both paths call the existing `bc_content.chunk_text`.

A separate preservation fix introduces `PreflightRejected` for input validation
before extraction state/provider work. The domain wrapper preserves an existing
candidate packet on that exception. Invalid chunk policy, request cap and model
identity regressions exercise byte-identical retained packets/state and unchanged
backend counts. Failed execution under the same context still clears stale output.

## Source measurement and corrected hypothesis

[Analysis](support-windows.json) pins the selected clause review and exact retained
source hashes. [Reproducer](analyze_support_windows.py) checks the real native
chunk boundaries and selected primary/additional support spans, without a model.

| Known development source | Default chunks, 7000/400 | Large chunks, 42000/400 | Primary quotes jointly in a default window | Full selected support jointly in a default window | Full selected support jointly in a large window |
|---|---:|---:|---:|---:|---:|
| Mandan legal pages 4–8 | 2 | 1 | 7/7 | 2/7 | 7/7 |
| Harwood proposed Article X | 6 | 1 | 5/5 | 0/5 | 5/5 |

The initial claim that the moderate six-item list was split was wrong and was
corrected before any extraction-provider execution. Its primary quote,
characters 7983–8726, fits default window 6563–13528. Indeed, all twelve selected
primary quotes fit a default window. The observed difference is availability of
the selected **joint support set**, including definitions, applicability and
aggregation, within one extraction prompt.

Both policies can process all source text across their calls. A selected support
set is not a proven minimal necessary evidence set. Repeated contextual language
may allow correct extraction with default windows. A larger window does not
establish better model performance, full legal understanding or source completeness.
It also changes the number of calls and the document-wide opportunity under the
native twelve-claim-per-chunk prompt limit. Any comparison must report those factors.

## Verification and review

The native member passes **92 tests**, Ruff lint/format and ty. The application
passes **343 tests** in the installed environment. Its compatible-runtime focused
checks also verify actual explicit-window extraction, cached replay and changed
policy rejection. The isolated full-suite result is recorded in [validation](validation.json).

Three Codex CLI jobs requested `gpt-6.1-terra`: native implementation,
[initial review](initial-review.md), and [final review](final-review.md).
Requested model identity is not independently provider-attested. Initial findings
corrected the source hypothesis and clarified retry/accounting language. Final
review found no correctness issues within its inspected changes. The coordinator
subsequently extended the same preservation handling to all pre-state input checks
and tested invalid request cap and missing model identity as well as chunk policy.
Reports describe their actual checkpoints; final file/test hashes are separate.

The prospective private comparison root passes the existing host-specific
[storage guard](storage-preflight.json) using the retained task layout. That
read-only admission check has not created or executed a provider run. Concrete
subdirectories, private-size limits, driver, runtime/settings, routing/pricing,
source/slot manifests and HTTP/accounting caps still need the final frozen protocol.
Do not reuse old evaluation caps or substitute this document for that protocol.

`max_attempts=1` means one backend attempt, not one additional retry. SDK retries
and agent retries must be zero and model requests limited to one. Native chunk
retries are additional adapter invocations and consume persistent reservations.
Dollar reservations attach to backend attempts; observed HTTP reservations are a
separate ledger. Estimated metering is not a hard provider-invoice ceiling.
The four-run/16-request/$12 estimated allocation discussed in the initial review
is **proposed, not frozen or executed**.

No research-source acquisition, extraction-provider call, canonical data change,
new quality result or final release was made in this checkpoint. CLI review work
is separately unpriced; zero extraction-provider calls does not mean zero model
work. The original 32/36 supported result remains failed, and these two known
sources cannot establish unseen-holdout performance. The full refresh and release
objective remains active.
