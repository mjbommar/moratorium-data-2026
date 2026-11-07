# Event validity publication profile 1.0.2

Profile 1.0.2 connects the tested maintenance contract to validation, publication, offline history checks and CSV export. The [compound-clause follow-up](compound-condition-development.md) selected **1.0.3**; current [policy-succession profile 1.0.4](policy-succession-contract.md) preserves this event-validity contract. Profile 1.0.2 was introduced by the [source-reviewed five-event migration](../work/research/2026-11-06/event-validity-migration/README.md). Five unchanged historical events have explicit validity acceptance; no real event was withdrawn or corrected. A schema and synthetic source-byte test do not establish source entailment or current legal force.

## Version and review contract

Record `schema_version` remains `1.0.0`; the new validation profile is [1.0.2](../work/schemas/expanded/1.0.2.json). Publication plans use version `1.0.2`, with the exact schema hash and `event-validity-v1` semantics. Profiles 1.0.0 and 1.0.1 and their schema bytes remain retained. Historical plans keep their original semantics, including originally unrestricted review scope strings. New maintenance publications require the applicable pinned profile: 1.0.2, its 1.0.3 successor, or current 1.0.4. A 1.0.3 publication cannot downgrade to 1.0.2, and a 1.0.4 publication cannot downgrade to an earlier profile.

Each event requires one explicit `event_validity` decision chain. Accepted events retain exact instrument/action/occurrence evidence and field acceptance. Withdrawn events retain their immutable original rows and source claims, rejected factual-field decisions and accepted, event-scoped withdrawal-basis evidence. A missing decision is an error. The [maintenance contract](event-maintenance-development.md) explains time-specific support, combined timelines, correction relationships and reinstatement.

Every new-profile record review contains `historical_fields`, including an empty list on ordinary/current records. It is disjoint from `accepted_fields` and `unresolved_fields`; the three lists cover every record field except its ID and schema version. A withdrawn event must put all retained fields in `historical_fields`, including its original claim list and unknown publication-time field. This disposition is permitted only for an unchanged, previously published withdrawn event. It cannot introduce a new already-withdrawn row, conceal a current assertion or exempt another table.

## Source proof and predecessor binding

Profile 1.0.2 uses a sealed 64-hex generation ID: the canonical hash of the table fingerprint together with the exact public receipt-byte hash. The plan and receipt retain the table fingerprint in `snapshot_sha256` / `sha256`; the directory name also binds the selected profile, review time, plan and evidence seal. The atomic symlink selects that complete generation. Promotion responses distinguish `generation_id` and `publication_sha256` from the table-only `sha256`. Receipt-only successors are permitted with a newer review and exact predecessor receipt pin; they do not renew unchanged source observations or event decisions. Successor plans pin `expected_publication_sha256`, so a recomputed predecessor plan hash cannot hide a replaced receipt. Older generation names remain their original table hashes. External trust still comes from a pinned Git revision or verified release manifest, which must also bind the tip pointer; internal content addressing does not authenticate a reviewer or prevent replacement of an entire untrusted root.

All retained claims still need independently verified text or visual evidence and a public-rights disposition. This includes rejected exact claims, withdrawal bases and correction relationships. No model confidence or review status supplies missing source bytes.

The plan also pins `evidence_sha256`, calculated by `expanded_promotion.evidence_fingerprint(proofs)` after source preflight. This hashes the canonical claim-sorted **public** proof set; private extraction-artifact paths are removed before hashing and publication. Promotion recomputes it after source verification, and offline traversal checks the retained proof set against the same pin. A plan pin cannot make an unlocated quote pass the independent verification gate.

New-profile promotion authenticates the actual predecessor's retained history and registry prefix before maintenance review. Publication review time must follow the predecessor's review time. Appended reviews concerning retained events must fall after that predecessor review and no later than the new publication review. These bounds supplement the contract's strictly ordered per-scope decision chains and same-instant atomic batches.

A legacy-profile event can migrate directly to a rejected validity root only when its actual published predecessor establishes accepted exact evidence and fields. This records withdrawal of the earlier published assertion without fabricating a new current acceptance or a predecessor-era validity decision. The actual predecessor receipt, profile, evidence proofs and chronology supply this bridge; a supplied dictionary alone cannot authenticate it.

Exact replay rechecks retained receipt proofs and predecessor history without reacquiring private sources. Older receipts retain their original proof format; their evidence arrays were not retrospectively sealed with the new proof-set hash. Profile 1.0.2 adds that explicit seal rather than claiming it existed historically.

## CSV and restore behavior

Export validates the selected generation's publication receipt, registry and predecessor chain before using its profile. A changed or removed pin cannot silently select an older export path.

For profile 1.0.2, these views are added to the existing projections:

| File | Meaning |
|---|---|
| `instrument_events.csv` | Every retained immutable event, including withdrawn history. |
| `instrument_events_current.csv` | Only currently accepted events in that reviewed snapshot. |
| `instrument_event_status.csv` | Event ID, review state, decision ID/time and accepted correction references. |

The manifest pins the selected profile and distinguishes retained/current/status views. Its `source_snapshot` is the actual sealed generation ID; `source_table_snapshot_sha256` separately identifies its JSONL table fingerprint. Current acceptance is a review state, not current instrument enforceability. Older-profile exports retain their existing view set and rendering schema; immutable historical CSV generations are not rewritten. A changed exporter creates a new projection identity.

The release builder requires every profile declared by the selected validator and the event-maintenance runtime. The synthetic restore test copies actual checker/export scripts, all three schema files, publication history, identity history and CSV projections into another root, deletes source bodies, and runs the restored commands without Git. Missing runtime/schema and changed schema bytes fail. This exercises the new-profile checker path; it is separate from a published final release or hosted deployment.

## Remaining rollout gates

- The existing five-event validity cohort has been substantively reviewed and promoted. Broader instrument-event migration and complete later legal histories remain open; synthetic withdrawal cases remain clearly labeled and no fake real-data withdrawal was created.
- Reconcile any consumer that counts retained events as currently accepted; the new views are available only when the source publication actually selects profile 1.0.2 or 1.0.3.
- Verify the final committed public bundle and downloaded release assets, final copy and required sibling/hosted delivery.

See the [integration evidence packet](../work/research/2026-11-06/event-validity-integration/README.md). P7 and the overall refresh remain open until their remaining real-data and delivery evidence exists.
