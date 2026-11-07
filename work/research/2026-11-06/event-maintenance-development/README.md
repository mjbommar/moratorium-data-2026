# Event maintenance development checkpoint

The isolated [maintenance contract](../../../../scripts/instrument_event_maintenance.py) and [22 regression tests](../../../../tests/test_instrument_event_maintenance.py) now exercise explicit event validity, withdrawal, reinstatement, typed one-to-many correction relationships, combined timelines, historical support and immutable predecessor retention.

**This is development code, not an active publication profile.** No real event was withdrawn, reaccepted or corrected. The five published events, canonical records, both existing schemas and CSV projections are unchanged. P7 remains open.

Two distributed `gpt-6.1-terra` CLI jobs provided the design and independent code review. The code review reproduced defects beyond the initial eleven fixtures: fabricated pre-publication history, hidden intermediate acceptance/support lapses, missing exact support at historical review time, correction chronology, Python Boolean/number equality, and missing correction-review evidence. Coordinator fixes and expanded regressions address those issues. [Review reconciliation](review-reconciliation.json) records one explicit migration-design difference and its still-required production trust boundary; it does not present the original review as an unchanged-code approval.

The contract permits an old-profile migration withdrawal only with an existing accepted predecessor baseline. It does not authenticate that baseline, verify source bodies, allocate identities or supply a publication-rights decision. The eventual adapter must bind it to the actual validated publication receipt and chronology. Newly introduced events cannot arrive withdrawn or contain a prior withdrawal/reinstatement story.

Full test suite: **299 passed, 44 subtests passed**. [Validation](validation.json) pins final implementation/test hashes. [Preservation](preservation.json) pins unchanged canonical CSVs, registry and schema bytes. Source/reviewer transcripts remain private; this increment made no provider calls or new acquisitions.

[Integration checklist](../../../../docs/event-maintenance-development.md) remains authoritative for the next step: versioned profile/plan, predecessor-bound historical field dispositions, source-proof/atomic promotion/offline-history checks, retained/current/status exports, consumer reconciliation, portable restore and substantive validity review of the existing cohort. Synthetic review relationships do not prove source entailment or current legal force.
