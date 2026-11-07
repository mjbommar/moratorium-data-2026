# New Jersey policy review and identity split — November 6, 2026

Subsequent [wave2 review](../nj-policy-wave2/README.md) dispositions the three
remaining assigned worker returns and applies bounded corrections. The body below
records this earlier checkpoint. Signed Chapter75, S4293's final session
disposition and current implementation remain unresolved.

This reviews five actionable corrections in the distributed `gpt-6.1-terra` return `nj-state-policy-002`, plus the separate A4696 proposal. Retained November 5 evidence and fresh November 6 primary acquisitions were checked for body/text integrity. Two Exa searches and eight bounded fetches were used, including two successful bc-web/pydoll history acquisitions with 1,800 ms settle. This does not complete the state's current-force or implementation review.

## Identity correction

The old `S3379 / A4096 / A4696 (2026-2027)` row joined two independent legislative proposals. Fresh rendered histories identify A4096 as S3379's identical bill, while A4696 identifies S2274 and displays only introduction/referral. S3379's history explicitly records approval as P.L.2026, c.75 on August 27. A4696 must not inherit that enacted classification.

The existing `policy_action_id` **nj-s3379-a4096-a4696-2026-2027** is retained unchanged for S3379/A4096, despite its historical spelling. Its display becomes `S3379 / A4096 (2026-2027)`. A separate **nj-a4696-2026-2027** row records A4696's March 16 introduction/referral and quarterly-reporting proposal. S2274 is mentioned as its officially identified identical bill; its independent history was not reviewed or silently added to this row.

`identity-split.json` records the exact original row, retained row after display correction, whole-CSV hashes and one-to-many historical reference mapping. The mapping is a split, not an equivalence assertion. `baseline-before-split.json` preserves the 16 original New Jersey rows; `baseline.json` guards the standard application after the display migration. The display migration changed only `bill` under a complete-file preimage guard and atomic replacement; subsequent substantive edits and the new row use the normal apply audit. Historical worker keys remain interpretable through the explicit split mapping; no old stable ID is deleted or reassigned. Sponsor attribution inherited from the old compound row remains a separate review item.

## Accepted fields and limits

| Record | Accepted correction | Remaining work |
|---|---|---|
| A5466 / chapter 98 | Reporting/disclosure mechanism; state-agency scope; July 8, 2025 immediate effective date; expiration 30 days after BPU submits its report | Actual report submission and resulting expiration are unknown. The 15-month reporting deadline does not establish actual submission. |
| A796/S731 / chapter 32 | BPU sets a minimum size designation no greater than 50 MW; July 7, 2026 effective date from signing evidence and immediate-effect clause | This is a ceiling on the threshold, not a fixed 50 MW trigger or a confirmed BPU decision. Tariff implementation remains unverified. |
| S3379/A4096 | August 27 enactment; reporting/disclosure mechanism, state-agency scope and semiannual-reporting summary | Authenticated signed chapter/effective date and current implementation remain unresolved; legal_effect_status is unknown. |
| S4928 / chapter 335 | April 1, 2026 effective date, computed from January 20 approval and the first-day-of-third-month rule | Applies only to construction commencing on/after that date. No complete current-force review is asserted. |
| SR18 | Legal-effect status unknown, reflecting adopted nonbinding urging rather than proposed binding law | Legacy instrument-type enum has no resolution category; its classification within the legacy bill-row denominator remains a documented modeling limitation. |
| A4696 — separated row | In-committee proposal; quarterly reporting after initial three/six-month deadlines, depending on existing operation | Latest displayed action is not a completed later-action census; it is not chapter 75. |

Chapter 32's amendment text uses brackets and underlining. The obsolete 100 MW language is bracketed; the surviving BPU designation clause says no greater than 50 MW. This field review does not claim that an automated markup parser has reconstructed the entire enacted statute.

The guessed chapter-75 HTML path returned 404. The official history instead links the second reprint PDF, which was acquired and extracted separately with `pdftotext -layout`. Page 5 was visually reviewed: its three-year clock runs from each facility's first submission, with a possible continuation decision, and it contains an immediate-effect clause. Those are retained as reprint-version evidence; they are not promoted as authenticated signed-chapter terms. The old summary's unsupported universal three-year clock is removed. No expiry or operative date is invented.

## Provenance, counts and pending scope

`answers.json` contains five reviewed existing corrections and one separated proposal; `review.json` pins extraction integrity, page-5 rendering and open review items. Source manifests retain exact primary acquisition versions, with raw bodies/provider exchanges private. Exa's first result was a derivative policy summary, which is not used as independent primary evidence. The bounded official chapter search did not recover chapter 75; no absence finding follows from those results. Two Exa searches report $0.014 total known search cost.

The tracker increases from 441 to **442 state-policy records**, from 439 to **440 legacy bill rows**, and from 93 to **94 enacted bill records**. The additional row corrects an existing compound identity, not the discovery of a new enactment. The local inventory remains **1,293 instruments / 1,071 classified in force**; ballot tables are unchanged. Public count copy, codebook, state page and index are rebuilt. Inventory-wide state-page dates retain the November 5 cohort cutoff.

S3611, S4293 and S680/A1170 worker returns remain unpromoted pending disposition/current-force review. Chapter 98's event-driven expiration, BPU implementation, chapter 75 final text and the resolution-type gap remain required work; this batch does not claim complete New Jersey freshness.

Validation: `make data site check` passed (zero errors, 282 existing data warnings; all 49 documented numbers match). Exact pre/post comparison verifies 21 existing-field changes across five rows, one separated proposal, and zero removed stable IDs. Replay proposes zero additional field edits and skips the existing new proposal. `validation.json` pins the completed build log.
