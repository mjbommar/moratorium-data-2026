# Expanded identity registry

The authoritative identity history is `data/identities/expanded.jsonl`. It is
separate from the legacy CSV primary keys and the canonical domain tables
in `data/expanded/<table>.jsonl`. The registry does not change ballot facts,
certification, legal force, or legacy instrument counts. Canonical records include reviewed Eliot, Sabattus, Canterbury, Nottingham, Wiscasset, North Berwick, Wells, Peru and Brownfield questions and result
observations; identity decisions alone never promote their facts. Remaining candidate
review snapshots are research inputs, not canonical domain records.

`scripts/expanded_identity.py` applies explicit reviewer decisions. Names, titles,
election dates, question numbers and similar wording never trigger an automatic
match. A reviewer supplies an opaque UUID for each new entity and event. Preserve
legacy moratorium/project/state-action IDs exactly; this registry allocates only
expanded identities. The [domain publisher](expanded-promotion.md) must resolve candidate references
through these reviewed mappings and independently enforce field/evidence review.

An observation alias contains a namespace, its source record ID, and the SHA-256
of the record serialized as UTF-8 JSON with sorted keys, `ensure_ascii=False`, and
compact separators. Different record versions have distinct fingerprints and
require separate explicit identity decisions. A repeated fingerprint cannot be
silently assigned to another canonical identity. Two aliases sharing a name or
source ID are not automatically equivalent. Reference each immutable snapshot's
manifest when reviewing its aliases.

## Decision protocol 1.0.0

A plan contains exactly `schema_version`, `expected_sha256` and `events`. The
expected hash is SHA-256 of the entire previous registry file, or null for an
absent registry. Events contain exactly:

- `schema_version`: `1.0.0`.
- `event_id`: a new opaque UUID.
- `action`: `allocate`, `alias`, `merge` or `split`.
- `table`: one of the expanded contract's fifteen table names.
- `inputs` and `outputs`: canonical UUID lists.
- `aliases`: observation alias objects (`namespace`, `source_id`, `record_sha256`).
- `assignments`: split dispositions (`alias`, `canonical_id`).
- `reviewer`, timezone-bearing `reviewed_at`, and `rationale`.
- `evidence`: at least one URL, `body_sha256`, and document `locator`.

Allocation creates one unused ID with at least one pinned observation. Alias adds
observations to one active ID. Merge takes at least two active IDs from the same
table and retains one as survivor. Earlier IDs and events remain in history;
references to merged IDs resolve to the survivor. IDs are never reused.

Split retires one active ID and creates at least two unused IDs. Every alias
currently resolving solely to the old identity, including aliases inherited from
a prior merge, needs an explicit assignment. An assignment to a new ID resolves
that observation. A null assignment preserves ambiguity: lookup returns all
possible successors. Historical references to the split identity also return
multiple successors; callers must not arbitrarily select one. New entity facts
and rewritten foreign keys need their own subsequent review and import.

## Preview, apply and recovery

```sh
python3 scripts/expanded_identity.py \
  --registry data/identities/expanded.jsonl --plan REVIEWED_PLAN.json
python3 scripts/expanded_identity.py \
  --registry data/identities/expanded.jsonl --plan REVIEWED_PLAN.json --apply
```

`python3 scripts/expanded_identity.py --registry data/identities/expanded.jsonl
--check` validates the retained registry without a plan; `make check` includes it.

Dry-run is the default and writes no registry or lock. Apply locks a separate
stable lock file, validates all existing history and all new events, compares the
reviewed baseline hash, then appends events through an atomic file replacement
with file and directory fsync. Earlier bytes remain unchanged. A conflict anywhere
prevents partial registry writes. Writers using this interface serialize through
the same lock; a competing plan against an old baseline must be reviewed again.

Replaying an already-recorded identical plan is a no-op, even when later history
exists. This confirms historical application, not that an entity remains active.
Reusing an event ID with changed content fails. Retained plans, hashes and Git
history support review and recovery. Do not truncate history to undo a decision:
use a reviewed subsequent merge, split or alias decision as applicable.

These checks validate identity mechanics and explicit provenance references, not
source authenticity or reviewer judgment. They do not download evidence or verify
that a document supports the proposed identity. The coordinator must inspect the
pinned source bodies before preparing a plan. Eliot's initial plan uses the signed
special-referendum warrant and pins both reviewed candidate and combined snapshot
aliases. It accepts only identity, not every field in those candidate records.
