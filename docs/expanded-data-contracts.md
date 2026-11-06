# Expanded candidate data contracts, version 1.0.0

These additive contracts describe research candidates and reviewed canonical expanded
records. They do not modify the legacy inventory or state-policy CSVs. The existing codebook's
moratorium grain and exclusion of permanent bans remain unchanged. A successful
validation is structural consistency, not proof of legal effect, source accuracy,
identity, completeness, or permission to publish. An initial [reviewed snapshot writer](expanded-promotion.md) now supplies separate
identity, evidence, field-review and atomic-publication gates; reviewed canonical
records include Eliot, Sabattus, Canterbury, Nottingham, Wiscasset, North Berwick, Wells, Peru, Brownfield and Freedom, with explicit result supersession. See the
[generated results view](ballot-results.md). Identity decisions have a separate
[append-only registry](expanded-identity-registry.md).

## Files and validation

[JSON Schema 2020-12](../work/schemas/expanded/1.0.0.json) contains a named
`$defs` schema for each JSONL table. Every record has `schema_version: "1.0.0"`.
Use UTF-8, one object per line, in files named `<table>.jsonl`. Missing tables are
allowed and mean no records supplied, not that the universe was searched. Unknown
JSONL filenames and duplicate IDs within a table fail. Examples in
[synthetic jurisdiction fixture](../work/schemas/expanded/fixtures/synthetic/jurisdictions.jsonl) are entirely
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
from a reviewed, collision-checked registry; the
[identity registry](expanded-identity-registry.md) now supplies explicit UUID allocation,
observation aliases and merge/split lineage. It performs no identity inference and
does not promote domain records. Names and titles
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
Optional `source_vote_categories` preserve original labels/counts such as VOIDS,
without mapping them to blanks, other votes, undervotes or overvotes. Optional
`source_vote_totals` preserve printed totals with their original label and an
explicit scope. Neither field supplies a denominator or changes standard counts.
Each item requires nonnegative count and supporting claim IDs. Every claim must
match the exact result, source document, predicate (`source_vote_category` or
`source_vote_total`) and complete label/count/scope value. Duplicate label/scope
entries and forced mapping keys are rejected. Absent fields remain compatible
with earlier snapshots. Public summaries display these observations separately.

`value_methods` identifies text, OCR, visual review, source reporting or derivation
per result field with supporting claim IDs. Optional provision/restriction
`duration` distinguishes enactment, adoption, effectiveness and applicability anchors;
no dates are equated without source/legal review. It retains calendar months/years
versus days, the legal anchor and its
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
Earlier pilot evidence is reusable only through its pinned input manifest and
fresh body/text hash checks. The audit explicitly records universal newline
decoding where required to reproduce the original pilot text hash; it does not
silently replace source bytes. Additional omission leads have their own frozen
registry and bounded recovery jobs, distinct from the initial 50-seed list.

`scripts/build_ballot_census.py` compiles terminal ballot packets into a separate
review snapshot. Every packet gets its own ID namespace, including claim subjects,
result revisions and value-method claim references; external legacy instrument IDs
and free-form source values remain unchanged. Explicit identity decisions pin both
measure records before grouping aliases. Grouping does not delete observations or
accept legal effect. A reviewed input overlay must match its review receipt's
output hashes. The builder refuses to overwrite snapshots and records input and
expanded-output hashes. Combined unreviewed claims remain private until excerpt
and evidence review; the public census manifest is not canonical ballot promotion.

Visual transcription reviews require a pinned claim, values, source PDF hash,
page and rendering parameters. `visual_claim_review.py` rehashes the retained PDF
and reproduces the approved page-image hash. This verifies the reviewed rendering
chain, not the reviewer judgement, election certification or legal effect. The
return audit reports visual verification separately from located text evidence.
Reviewed overlays are audited separately from unmodified worker returns. Each
overlay must match its receipt's output hashes; accepted claim decisions are
checked against verified evidence. An accepted result transcription does not
accept the measure's bindingness or legal implementation.

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

## Durable citations and acquisition identity

Source documents may carry an optional HTTP(S) `citation_url` for a reviewed,
durable public citation, such as the parent post of a CDN-hosted image. Public
summaries prefer it for navigation. The original `url` and body/text hashes still
identify the acquired version; a citation URL never supplies substitute evidence
or authenticates its publisher. Earlier snapshots without this field retain their
existing URLs and remain unchanged.
