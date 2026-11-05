# Expanded candidate data contracts, version 1.0.0

These additive contracts describe research candidates, not accepted facts, and do
not modify the legacy inventory or state-policy CSVs. The existing codebook's
moratorium grain and exclusion of permanent bans remain unchanged. A successful
validation is structural consistency, not proof of legal effect, source accuracy,
identity, completeness, or permission to publish. There is no promotion or writer.

## Files and validation

[JSON Schema 2020-12](../work/schemas/expanded/1.0.0.json) contains a named
`$defs` schema for each JSONL table. Every record has `schema_version: "1.0.0"`.
Use UTF-8, one object per line, in files named `<table>.jsonl`. Missing tables are
allowed and mean no records supplied, not that the universe was searched. Unknown
JSONL filenames and duplicate IDs within a table fail. Examples in
[fixtures/synthetic](../work/schemas/expanded/fixtures/synthetic/) are entirely
invented; `ZZ` and `example.invalid` are deliberately fictitious.

```sh
~/projects/bc/bc-modules/.venv/bin/python scripts/expanded_data.py \
  work/schemas/expanded/fixtures/synthetic
~/projects/bc/bc-modules/.venv/bin/python -m unittest discover -s tests -p test_expanded_data.py -v
```

Use `--moratoria data/moratorium_inventory.csv` and/or `--state-actions
 data/state_legislation.csv` when tagged references use those legacy types. The
validator reads these CSVs only to resolve their ID columns; missing files,
columns, or IDs fail. Restrictions resolve to the supplied JSONL records. The CLI
is read-only and returns 0 for valid input and 1 for invalid input. Its certified
count is **current explicitly certified result observations**, not measures or
legal instruments; independent observations may describe the same measure. Only
explicit supersession removes an observation from that count. It is a diagnostic,
not a public tally. Missing rows and unresolved references cannot establish absence.

## Grains and semantics

The table definitions are `jurisdictions`, `elections`, `ballot_measures`,
`measure_provisions`, `measure_results`, `local_restrictions`, `instrument_events`,
`measure_instrument_links`, `source_documents`, `claims`, `review_decisions`,
`search_runs`, `search_attempts`, `search_sightings`, and `coverage_observations`.
Each table's singular ID field is its key. IDs are opaque and must be allocated
from a reviewed, collision-checked registry; this increment checks duplicates but
provides no allocator, merge/split workflow, or identity inference. Names and titles
are not keys. Distinct same-name governments must have distinct IDs. This first
validator requires a measure and its election to use the same jurisdiction ID;
overlapping administrative and electoral jurisdictions need a future explicit
relationship contract rather than a guessed equivalence.

A measure has independent lifecycle, bindingness, yes-direction and referendum
polarity. Provisions capture mechanisms, covered uses, exemptions, and thresholds
with original unit, measurement basis, aggregation and scope. An election result
is an observation with separate reported and calculated outcomes and explicit
certification. A complete precinct count does not certify a result. For a
mechanically calculated outcome this version uses the stated denominator, threshold
and strict or inclusive comparison. It reverses restricts/facilitates for a defeated
question; mixed, neutral and unresolved remain as stated. A direction is not a
legal-effect assertion. Unspecified totals stay null, never zero. The validator
allows optional `outcome_direction_basis` to distinguish `calculated` (the default
for legacy candidates), `reported`, and `unresolved`. A reported basis requires a
`source_reported` value method for `reported_outcome` and a matching claim scoped
to that exact result observation. It does not invent a passage rule, certify the
result, establish legal effect, or override contradictory calculable arithmetic.
The validator
checks arithmetic only when inputs are available, and compares reported percentages
to the chosen denominator with 0.11 percentage point rounding tolerance.
Optional `yes_no_votes` records the arithmetic sum without inventing total valid
votes or turnout; `blank_votes` remains distinct from overvotes and undervotes.
`value_methods` identifies text, OCR, visual review, source reporting or derivation
per result field with supporting claim IDs. Optional provision/restriction
`duration` retains calendar months/years versus days, the legal anchor and its
uncertain date; it does not automatically calculate an operative expiration.
Complicated passage rules should remain `unknown` and be described in evidence;
they cannot be represented or calculated completely by this first increment.

`instrument` is a tagged reference (`moratorium`, `restriction`, or `state_action`)
so legacy identifiers do not collide. Accepted measure-to-instrument relations
require a current accepted decision scoped to that exact relation, and each
supporting claim needs its own current accepted decision scoped to its predicate.
Claims identify the document version and their subject. Accepted decisions require
supporting claim IDs, and those claims must address the target. A claim decision
uses that claim itself as its supporting ID; this records review of the source
assertion, not independent corroboration. Superseded decisions do not count as
current; competing successors fail. An advisory measure cannot itself enact or
uphold an instrument through an accepted link. Independent subsequent adoption
requires its own event and evidence. An advisory result never creates an active
moratorium: this validator generates no instrument or status at all.

Source records distinguish payload and extracted-text hashes and retain retrieval,
access and publication classification. Create a new document ID when bytes change;
old claims keep their original document reference. Search ledgers retain attempts,
errors, retries, sightings, run scope and spend; null spend means unknown, not free.
Coverage observations describe a bounded search, not proof of absence. These
contracts do not check URL bodies, quote spans, rights, reviewer competence or
whether the cited source actually supports a claim.

`scripts/audit_refresh_returns.py` adds a separate pre-review check against retained
bounded-client artifacts: declared source hashes, independently located excerpts,
and candidate seed coverage against the frozen discovery list. A payload-only
document with null text hash can pass payload accounting but cannot prove a text
claim. Visual claims require their own reviewed source/page/render provenance;
an unlocated text quote is not automatically a visual claim. The audit does not
promote candidates or establish legal effect, and its success cannot substitute
for substantive review. Frozen seeds describe that source list, not a full census.

## Dates and limitations

`date_bounds` has inclusive earliest/latest possible **dates**, precision and
original text. `day` requires equal non-null bounds; unknown precision requires
null bounds. Jurisdiction validity and coverage periods use `[start, end)`;
convert source-inclusive end dates only with evidence and retain original wording.
Full timestamps require a UTC offset and are kept distinct from date-only facts.
Adoption, effective date and applicability start are separate. When known bounds
establish retroactivity, require an explanation and an applicability-start claim;
validation does not adjudicate that claim. Null or overlapping bounds do not imply
chronology. Duration remains source text; calendar months and years are not
converted into 30/365-day terms, and expiry is not calculated. The legacy
`duration_days` field has historical conversion assumptions described in the
codebook and is not reinterpreted here.

This is a first contract increment, not the P1 pilot exit: it does not validate
all legal chronology or certification evidence, infer external instrument status,
verify accepted claims, reconcile independent result revisions, model all legal
passage rules, or implement authoritative IDs, migrations, CSV exports, review
application, atomic promotion, source capture, or release. A source-backed pilot,
identity registry, broader review gates and transaction design remain required
before canonical use. Certification and active-status counts must be derived from
reviewed, scoped evidence and a declared cutoff, never from these diagnostic counts.
