# Real five-event validity migration

Status: applied to sealed generation `9f2c9b4d29e31a5434bb38f071724c38b59b926e114ad4b75acba854aa080287`, selecting validation profile **1.0.2**. The table fingerprint is `7b1743642dc6b8bffe86c8f13af84fc60198e26b2724c440f01afae74be372f2`; the receipt hash and exact generation appear in [application](apply.json). No new event, instrument, claim or source was created.

Exactly five scoped `event_validity` decisions accept the unchanged historical events: three original adoptions and two source-declared immediate-effect events. Every prior expanded record is retained unchanged. No real withdrawal or correction relationship was invented for demonstration. Broader historical-event migration and current legal-force research remain incomplete.

| Existing instrument | Accepted historical events | Withheld |
|---|---|---|
| Stephenson County 26-08-94 | August 20, 2026 adoption | Effectiveness under applicable law, operative endpoint, later actions/current force |
| Whitman County May 2025 interim controls, posted 089101 | May 5 adoption and source-declared immediate effect | Distinct January wind pause; later extensions/termination, actual expiry/current force |
| Spokane Valley 26-002 | February 3, 2026 adoption and source-declared immediate emergency effect | Later hearing/actions, actual expiry/current force; source MW/energy-unit anomaly remains qualified |

The coordinator re-reviewed eight of eleven physical PDF pages for identity, dates, signature context and immediate-effect clauses. Separate terra CLI source reviews addressed adoption and effectiveness, including Stephenson as a negative control. A third read-only candidate review verified the five additions, predecessor/profile/registry/proof pins, field partition and unchanged prior records. Source agreement is review evidence, not legal truth. Reports and coordinator reconciliation are recorded separately from the actual publication receipts.

[Source preflight](source-preflight.json) reverified all **528 retained claims** across **144 source-document records** using 51 existing acquisition directories. Three old selection-ledger copies failed path-ownership checks and were excluded; valid owned acquisitions cover every source version without relaxing those checks. This is retained-byte/visual verification, not 144 new acquisitions or independent institutions. Original bodies, text and images remain private; source observation times and the November 5 working cohort are unchanged.

## Whitman typed endpoint correction

The source review exposed an unsupported typed current endpoint. July 7, 2025 remains in the original-term description, conditional on extension or earlier termination. The codebook defines `current_end_date_iso` as a current operative endpoint after accounting for extensions; that field is now blank. Status prose explicitly qualifies the retained legacy expired bucket as original-term classification rather than renewed acceptance of actual expiry. No classification, original term, identity, coordinates or headline count changes. [Answers](whitman-endpoint-answers.json) retain both original values.

## Publication and verification

[Preparation](prepare.py) never promotes. It preserves old values and allocates only five review-decision IDs in a scratch registry. [Identity plan](identity-plan.json), [publication plan](publication-plan.json), [preflight](preflight.json) and [application](apply.json) pin the transaction. The sealed receipt binds the tables and review/proof metadata; the predecessor receipt is independently pinned. [Runner](run_publication.py) uses explicit phases. Exact replay needs no source directory or visual-artifact access; initial preview/application still independently verify all retained sources.

The current projection now has 18 CSV views, including five retained events, five current accepted historical events and five status rows. Exact replay is `already_applied`. All 316 tests and 44 subtests pass; data/site/check reports zero errors, 489 warnings and all 53 documented numbers matching. [Preservation](preservation-check.json) pins unchanged prior tables and the two qualified legacy fields. Committed-bundle restore verification is the next pinned-revision step. Preparation or application alone is not a final release. Consumer reconciliation, remaining freshness/quality gates and final GitHub/hosted delivery remain open. No search, fetch or extraction-model API call was made; three CLI review jobs have separately unpriced spend.
