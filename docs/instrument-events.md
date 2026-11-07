# Source-supported instrument events

An event records one supported action concerning one identified instrument. It
does not establish the instrument's current legal force. Legacy moratorium IDs,
restriction IDs and state-action IDs retain separate namespaces. A ballot result
is not an adoption or effectiveness event without independent source support.

## Validation profile and evidence binding

[Profile 1.0.1](../work/schemas/expanded/1.0.1.json) preserves the record format
`schema_version: "1.0.0"` and adds a controlled action vocabulary. The original
[1.0.0 schema](../work/schemas/expanded/1.0.0.json) remains unchanged for historical
fixtures and receipts. This is a validation-profile revision, not a rewrite of
historical records. CSV manifests pin the exact selected profile bytes. Portable
bundles retain both profiles, including the one needed by the active validator.

Historical 1.0.0 publication plans and the unmodified retrospective pilot select
the 1.0.0 semantic rules explicitly. New event publication requires plan version
1.0.1 with a `validation_profile` pin containing its name, exact schema hash and
`event-exact-accepted-v1` semantics. Publication and offline-history checks select
that profile per plan; they do not reinterpret old event examples under the new
rules. The standalone validator accepts `--profile 1.0.0` for explicit historical
checks and defaults to 1.0.1. Future rule changes require another profile rather
than silently changing these event semantics.

The validator additionally requires a claim scoped to the exact event ID with
predicate `instrument_event` and value containing exactly the event's
`instrument`, `action` and `occurrence`. A nearby date, another instrument or an
adoption claim cannot supply a different effectiveness event. Source entailment,
legal conditions and identity still need substantive review. Publication requires
source-byte/visual verification, accepted claim review and separate field decisions.
The exact matching claim must itself have a current scoped acceptance and be
cited by the current accepted instrument, action and occurrence field decisions.
An unrelated accepted claim cannot bridge an unaccepted exact claim into publication.

| Action | Meaning and boundary |
|---|---|
| `proposed` | A source documents a proposal; it does not establish adoption. |
| `adopted` | Supported adoption/passage, separate from effectiveness. |
| `effective` | Supported effectiveness event; source clauses and their conditions must be reviewed. |
| `applicability_started` | Supported applicability start, including qualified retroactivity where separately established. |
| `published` | Documented legal publication, not retrieval or repository observation. |
| `amended` | A supported amendment, with the affected instrument identified. |
| `extended` | A supported extension, not an unexercised power to extend. |
| `repealed` | Supported repeal, separate from a proposal or reported intention. |
| `expired` | Supported actual expiry; an original expected endpoint alone is insufficient. |
| `suspended` / `resumed` | Supported interruption/resumption; no automatic inference from litigation. |
| `terminated` | Supported termination distinct from assumed expiry. |
| `litigation_filed` | A documented filing, not a judicial disposition. |
| `judicial_order` | A source-supported order; its precise reach must remain in evidence. |

Keep occurrence bounds, observation time and publication time separate. A
day-only occurrence gets no invented midnight or timezone. Unknown legal
publication time remains null. Later amendment, extension, termination and
current-law searches remain explicit gaps rather than silently supplied events.

## Initial migration cohort

The [applied three-instrument cohort](../work/research/2026-11-06/instrument-event-migration/README.md)
records five source-supported events: Stephenson's signed August20 adoption;
Whitman's May5 adoption and expressly immediate-effect clause; and Spokane
Valley's February3 adoption and expressly immediate emergency effect. These are
distinct legacy instruments already present in the local inventory.

Stephenson's effectiveness depends on passage/approval in accordance with
applicable law; it remains unresolved here. Whitman's July7 original endpoint
and Spokane Valley's 365-day original term do not independently prove actual
expiry or absence of later action. Whitman's May instrument must not be merged
with the separately recited January wind pause. No legacy status or ballot count
is automatically changed. Its event identities, reviewed source bindings and
publication/replay receipts are retained separately. Broader event migration
remains incomplete.

## Correction and withdrawal development

The [isolated maintenance contract](event-maintenance-development.md) now tests explicit validity decisions, historical support, correction relationships and predecessor preservation. At that development checkpoint it was not yet connected to publication. Profile 1.0.1 still cannot publish event withdrawal; the production integration, source review, consumer/export and restore gates remain open. The existing five events and their accepted evidence are unchanged.

## Versioned maintenance integration

[Profile 1.0.2](event-validity-publication.md) now integrates explicit event validity, predecessor-bound historical field review, sealed public evidence proofs, atomic maintenance and retained/current/status CSV views. Source-byte synthetic transactions and offline restore exercise this path. At that integration checkpoint the five-event generation still selected 1.0.1; the subsequent source-reviewed migration below now selects 1.0.2, without a real withdrawal. Original 1.0.0/1.0.1 schemas and historical semantics remain retained.

## Current five-event validity migration

The [source-reviewed migration](../work/research/2026-11-06/event-validity-migration/README.md) now selects profile 1.0.2. All five event records and exact claims remain unchanged; five explicit validity decisions were added after renewed retained-source review. There are five current accepted historical events, with no real withdrawal or inferred current force. Bound ballot-summary and CSV readers select the authenticated source profile; standalone candidate validation still requires an explicit profile selection. Earlier development paragraphs describe their historical checkpoints.
