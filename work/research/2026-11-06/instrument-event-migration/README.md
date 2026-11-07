# Initial legacy instrument-event migration

Status: applied at `aa1d4ebc9fb15a1b78c22ad44cb9ca71cb622d6b64be0ee884b3320656b732f8`;
exact replay is `already_applied`. Full preflight/application verifies all 528
claim bindings. All prior canonical records and both legacy CSVs are unchanged.
All 272 tests and 44 subtests pass; the full build/check has zero errors and 489
existing warnings. [Validation](validation.json) pins the completed checks.

This packet migrates source-supported actions for three existing legacy IDs,
without creating new local instruments or changing their status classifications.
`preflight.json`, `apply.json` and `replay.json` establish publication state.

| Instrument | Published events | Important unresolved facts |
|---|---|---|
| Stephenson County 26-08-94 | August20,2026 adoption | Effectiveness in accordance with applicable law, exact operative end, later action/current force |
| Whitman County May2025 interim controls, posted 089101 | May5,2025 adoption and source-declared immediate effect | Distinct January wind pause; later extensions/termination and actual expiry |
| Spokane Valley 26-002 | February3,2026 adoption and source-declared immediate emergency effect | Later hearing/actions, actual expiry and current force |

The coordinator directly reviewed eight of eleven physical PDF pages for the
bounded identity/date/clause questions. The source CLI reviewer received seven
of those pages; neither review is full present-law history. Explicit visual
receipts reproduce each claim's signed-date page and instrument-title page.
Legal publication times remain unknown. Occurrences are day-precision bounds,
separate from original acquisition times and current observation/review time.

Two separate `gpt-6.1-terra` CLI jobs reviewed the source images and initial
contract/code changes. Their hashes and session IDs are retained in
[reconciliation](review-reconciliation.json). Source judgments support the five
events while withholding inferred expiry/current force. The code review exposed
historical-profile incompatibility and an accepted-evidence gap; coordinator
fixes explicitly select old/new profiles and require acceptance/citation of the
exact matching event claim. Tests cover both fixes. The reviewers did not
independently re-review those subsequent changes; their agreement is not legal truth.

[Validation profile1.0.1](../../../schemas/expanded/1.0.1.json) preserves the
1.0.0 record format. Plan version1.0.1 pins its exact bytes and the versioned
event-claim semantics. Historical plans and frozen fixtures retain profile1.0.0
rules. The original schema and all old records are unchanged. New source-event
publication cannot opt into the older permissive profile.

The applied candidate adds three existing-source versions to the expanded source table,
five events, five scoped claims and twenty-five decisions. Those versions were
already retained privately; no new acquisition, Exa call, browser request or
extraction-model call was needed. CLI review spending is separately unpriced.
The [preservation check](preservation-check.json) pins every event, the original
snapshot and both unchanged legacy CSV hashes. Full source-byte/visual and field
gates passed before application; preparation alone was not acceptance.

This closes a first real event cohort, not the full historical event migration,
freshness review, extraction quality gate, final release or hosted deployment.
