# Instrument-event maintenance development

Historical development checkpoint: the live dataset remains on **1.0.1**. The subsequent [profile 1.0.2 integration](event-validity-publication.md) now connects this contract to publication and exports; real-data migration and consumer/delivery gates remain open. The five published events, both existing schema files, canonical snapshots and CSV projections are unchanged. This development contract does **not** make withdrawal publishable yet and does not close P7.

`scripts/instrument_event_maintenance.py` now exercises review-state transitions independently of the publication adapter. The [synthetic tests](../tests/test_instrument_event_maintenance.py) establish internal history invariants; they do not establish source entailment, publication rights, identity correctness or current legal force. A passed contract is not authorization to publish its input.

## Tested contract

An event has one linear, connected `event_validity` review chain. `accepted` means accepted as an event in the reviewed snapshot; `rejected` means withdrawn from that accepted set. Missing, ambiguous or unresolved validity is an error rather than implicit acceptance. Every decision carries explicit reviewer, method, rationale and timezone-aware time. Equal instants are allowed across scopes in one atomic batch; a successor in one scope must be strictly later.

A current accepted event needs a currently accepted exact instrument/action/occurrence claim, field decisions citing that exact support, and supporting claim acceptance both at the review time and now. A withdrawal needs accepted event-scoped basis evidence and rejected factual-field decisions. The old event and all claims and decisions remain retained. Unknown publication time is not turned into a known factual date.

The combined timeline is checked at every relevant claim, field and validity review instant. A field cannot become accepted while its event is withdrawn, even if a later rejection hides it at the final head. A supporting claim cannot lapse while the event remains accepted, even if it is reaccepted before the next validity decision. Historical acceptances must have support at their own time; later evidence does not retroactively justify them. Canonical serialized equality distinguishes retained Boolean values from numbers, unlike Python dictionary equality.

Correction claims use predicate `event_correction`, subject equal to the withdrawn original event, and value `{"replacement_event_ids": ["existing-event-id", "another-existing-event-id"]}`. One-to-many corrections are permitted. Accepted correction claims require their own scoped, self-citing source-claim acceptance. The original must have been withdrawn and every replacement accepted at correction-review time. Self-links, dangling endpoints and cycles fail. Corrected replacements can subsequently be withdrawn through their own history. Reinstating an original requires retiring any conflicting current correction claim explicitly; the relationship history is preserved.

New events cannot arrive already withdrawn, or currently accepted with an invented pre-publication withdrawal/reinstatement history. Existing event, claim and decision records cannot disappear or change. The contract returns separate retained-status and current-accepted views, including correction references. These are development return values, not new canonical exports.

## Migration choice and trust boundary

The design review proposed appending a new validity acceptance before withdrawing an event during migration. The development contract instead permits a rejected root **only for an event retained in a supplied, previously accepted baseline**, with exact claim and field acceptance checked in that predecessor. This avoids recording a new current acceptance of an event already known to be wrong, and avoids inventing a predecessor-era validity decision.

This bridge is not self-authenticating. `transition(rows, previous)` assumes the caller has independently validated and pinned the actual predecessor publication using its original profile, identity registry, evidence proofs and receipt. An arbitrary dictionary or two aliases of one mutable object cannot prove that prior publication occurred. The subsequent profile 1.0.2 promotion adapter now enforces that boundary against pinned predecessor receipts and rejects backdated maintenance; the isolated function still does not authenticate a supplied dictionary. The module alone must not be installed as a publication gate.

## Required integration before P7 closure

1. Add a new, explicitly pinned validation profile and publication-plan version. Preserve 1.0.0/1.0.1 schema bytes, dispatch, frozen fixtures and old receipts. Keep current record format immutable unless a separately reviewed format migration requires otherwise.
2. Connect structural validation, exact-claim/validity/correction checks and the narrow historical-support exception. Do not globally waive source acceptance for superseded decisions on unrelated records.
3. Add predecessor-bound `historical_fields` to the new plan contract for retained withdrawn events only. Require an exhaustive, disjoint field partition, exact fingerprints and the appropriate withdrawal chain; forbid use on new/current rows or unrelated tables. Verify appended transition chronology against the actual predecessor receipt. Ordinary source-byte/visual verification and public-rights review remain required for every retained claim, including rejected history and withdrawal bases.
4. Integrate the same transition checks into atomic promotion and offline predecessor traversal. Verify stale baselines, conflicting decisions, interruption/recovery, exact replay and profile downgrade rejection. The development bridge above requires explicit review in this real publication context.
5. Add retained/current/status CSV views with selected-profile pins, correction references and fail-closed handling of invalid histories. Preserve all old projection generations and source publication receipts. Audit consumers that might otherwise count a withdrawn row as currently accepted. “Current accepted event” does not mean currently enforceable instrument.
6. Include new profile/module dependencies in deterministic portable bundles and exercise clean restore without Git/private bodies. Verify missing/tampered profiles, receipts, history and status projections fail. Reconcile download documentation and manifests.
7. Substantively review explicit validity decisions for the existing five events before any real new-profile migration. Do not create fake withdrawals or reaccept facts merely to demonstrate the machinery.

The [development receipt](../work/research/2026-11-06/event-maintenance-development/README.md) retains two distributed terra review references, coordinator reconciliation, code hashes and test evidence. These requirements remain open until their production and source-review evidence exists.
