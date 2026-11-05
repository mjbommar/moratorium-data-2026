# Expanded-table publication protocol

`scripts/expanded_promotion.py` supplies the first implementation of explicit
reviewed snapshot publication. The first real canonical batch now contains Eliot Question 5, its proposed
mechanism and the signed result return. It includes one jurisdiction, election,
measure, provision and result observation, four sources, fifteen verified claims
and fifty-five scoped review decisions. Operative dates and the measure/instrument
link remain unresolved. Other census records remain candidates. Broader behavioral
calibration, additional ballot reviews, public exports and release work remain open;
this batch does not close P3 or P6.

The canonical path is `data/expanded`, a relative symlink to a complete immutable
generation in `data/expanded-snapshots/<snapshot-sha256>/`. Every generation contains
all fifteen `<table>.jsonl` files and `publication.json`. This preserves the planned
`data/expanded/<table>.jsonl` interface while allowing a single atomic pointer swap
instead of fifteen independently visible table replacements. Git must retain both
the relative symlink and its referenced generation. Old generations remain available.
Readers must resolve the directory once before opening multiple tables;
`expanded_data.validate` and `read_snapshot` do this. Consumers that independently
resolve each filename during a publication can mix generations and need adaptation.

A plan is one explicit JSON file with exactly:

- `schema_version`: `1.0.0`.
- `expected_sha256`: fingerprint of the previous canonical snapshot, or null.
- `registry_sha256`: SHA-256 of the complete reviewed identity registry.
- `snapshot_sha256`: fingerprint of the complete proposed snapshot.
- `reviewer`, timezone-bearing `reviewed_at`, and `rationale`.
- `record_reviews`: exactly one publication review for every supplied record.

Each record review contains exactly `table`, `id`, `record_sha256`,
`previous_sha256`, `accepted_fields`, `unresolved_fields` and `publication`.
Record fingerprints use sorted-key compact UTF-8 JSON, with `ensure_ascii=False`.
The baseline fingerprint is null for a new record. Both field lists must be unique,
disjoint and together cover every field except the primary ID and schema version.
Unresolved fields must contain null, `unknown`, `unresolved`, an empty list or an
empty object; populated factual assertions cannot hide behind an unresolved label.
Publication requires an explicit rights disposition of `public_record`,
`reviewed_excerpt` or `reviewed_metadata`. These are human review decisions, not an
automatic licensing determination. Never mark a publisher's full article as an
approved excerpt.

Every record ID must be allocated for its table in the identity registry. Retired
or ambiguous IDs cannot receive new facts. An unchanged historical record may
retain its earlier ID; no merge silently rewrites its facts. All existing records
must remain present. Historical observations, claims and review decisions cannot
be rewritten; corrections use new records and explicit supersession. Mutable
entity records require the exact previous-record fingerprint.

Every accepted field of a jurisdiction, election, measure, provision, result,
restriction, instrument event or measure/instrument link needs one current scoped
accepted review decision. The supporting claims may transcribe source wording used in a reviewed
interpretation, such as classifying bindingness. The structural validator requires
acceptance of each supporting claim at its own predicate and checks its subject
against the exact decision target. A field decision never automatically accepts
a supporting claim or a different field. `claim_ids` is a mechanically checked reference
list and does not need a separate factual field decision. Record publication reviews
pin source/claim/review/search metadata separately; they never establish legal force.

All source versions and all claim quotations must independently match retained
bounded-client evidence or a verified visual-review receipt. Evidence directories
are explicit CLI inputs, not recursively discovered. Integrity errors fail the whole
batch. Visual receipts must use canonical claim fingerprints; candidate receipts
cannot be reused after changing IDs without a separately verified mapping/review.

```sh
~/projects/bc/bc-modules/.venv/bin/python scripts/expanded_promotion.py \
  --candidate REVIEWED_TABLE_DIRECTORY --plan REVIEWED_PLAN.json \
  --evidence-directory PRIVATE_RETAINED_JOB_DIRECTORY
# Add --apply only for the reviewed batch intended for canonical publication.
```

Dry-run is the default and writes no publication, staging directory or lock. Apply
locks the stable publication lock and takes a shared lock on the identity registry's
stable lock while rechecking all gates. It writes/fsyncs a complete generation,
renames/fsyncs that generation, then atomically replaces the relative pointer and
fsyncs its parent. The publication receipt retains the exact plan and verified
quote/source hashes without private text paths. No API calls or automatic retries
occur. A retained exact snapshot and identical plan replay as a no-op; altered
acceptance text is not an identical replay.

An interruption before the pointer swap leaves the previous publication intact
(or absent during initialization). A completed but unreferenced generation is
retained for inspection; automatic retry refuses to overwrite it. Compare its
fifteen table hashes, publication plan and receipt against the intended plan before
recovering. Do not delete the active generation or silently redirect the pointer.
Failures before publication can leave ignored lock files or private staging debris;
they do not justify claiming a partial batch was accepted.

This is local canonical publication. It does not create a Git commit, GitHub release,
public export or website deployment. Those retain the separate P6 gates.
