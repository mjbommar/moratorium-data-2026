# Integrated full-inventory correction batch

Applied **2,063 factual field changes and 428 derived verification changes across
787 records**. The remaining 1,552-record population has primary, independent and
coordinator review; together with the earlier 225-record cohort, actual primary and
independent artifacts cover all 1,777 raw IDs. The 119 targeted follow-ups and their
supplemental adjudications are additional evidence, not additional records.

[Application](application.json) records exact before/after values and row transitions.
The merged queue resolved 37 overlapping fields; 38 supplemental fields were new.
Sixty-five proposed verification-field edits were replaced by recomputation from
final row text, avoiding stale derived values. All 371 pinned integration inputs
were checked before application. A pre-write scope-registry guard caught a changed
Minnesota companion-bill label; the superseding scope observation now binds the
reviewed label while preserving its permanent ID and prior analytical membership.
No raw IDs were merged or removed.

The status contract now represents genuinely disputed recorded stages as `unknown`,
separately from pending, past, rejected and recorded active/extended. Supported
historical approval does not require exhaustive proof of current legal force.
Reported approvals, original terms, proposed texts and subsequent instruments retain
separate qualifications. The focused status/term/filter suite passes eight tests.

Current classifications after this application are 893 active, 199 extended, 64
pending, 82 replaced, 74 expired, 12 rescinded, two rejected and four unknown.
Verification-marked rows are 979; absence of a flag does not certify current force.
Policy scope remains 374 included, 19 excluded and 54 unresolved across all 447 raw
observations. Ballot totals remain 57 measures and 64 retained result versions.

Summary, scope exports, GeoJSON, inventory table, timeline, landing page and state
pages are regenerated. Legacy validation has zero errors and 619 warnings, retaining
source-specific unknowns and computed-date cautions. All 79 documented-number checks
pass. Five endpoint/category consistency decisions are still being reconciled; final
historical replay, consumer handoff, original quality-gate completion and verified
release remain open. This is applied working data, not a completed release.

## Final endpoint consistency application

A subsequent [ten-cell application](endpoint-application.json) covers five rows.
Rockdale, Saugatuck and Swancreek now record elapsed supported historical terms;
later instruments and legal force remain unresolved. Covington's signed renewal
uses the fixed November 7 event cutoff and clears the obsolete October endpoint.
Waynesville's unsupported fixed endpoint and day count are cleared; its documented
adoption retains recorded active, since uncertainty about a term alone does not
make the recorded adoption stage unknown.

The final raw totals are **1,089 recorded active/extended, 64 pending, 171 past,
two rejected and four unknown**, across the same 1,330 local IDs. There are still
447 policy observations and 57 measures. [Coverage](review-coverage.json) records
all 1,777 primary and independent artifact mappings, zero missing reviews and zero
pending cells in the compiled remaining-cohort queue. The complete release and
quality/consumer gates remain open.

The complete `make check` now passes at this applied state; [validation](validation.json) pins the command and log hash. This covers the full retained expanded publication history, derived ballot/CSV outputs, source tracking and all 79 documented-number assertions. No private source text is tracked. Original P4 acceptance and final consumer/release delivery remain separate and open.
