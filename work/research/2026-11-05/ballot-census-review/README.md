# Combined ballot census review snapshot

`current-snapshot.json` points to v2. Its manifest is `v2-manifest.json`; the
original `manifest.json` remains the v1 receipt. V2 adds six scoped source reviews
for Eliot and Sabattus result counts, signed certification dates and reported
approval. The complete v2 payload is private at the path in the pointer. These
reviews accept source assertions/transcriptions, not operative moratorium dates
or measure-to-instrument links. Logical groups are unchanged.

This combines all 22 terminal ballot jobs: the original 50 discovery seeds plus
eight omission leads. It preserves 58 measure-observation records in 56 logical
seed groups. Two Illinois recovery observations describe the same township
questions already in the original list; explicit identity decisions link them.
The six other recovery leads add candidate groups. This is not a complete census
of all electoral measures or acceptance of their legal effect.

Each job has a separate ID namespace. Duplicate observations, conflicting sources,
different result snapshots and unresolved legal relationships remain distinct.
The reviewed Ohio outcome-basis overlay replaces that job's original input for
this compilation; its receipt pins the overlay hashes. Other source-quality and
visual/OCR review gaps remain open, even though the combined structural validator
reports zero errors. Candidate fields are source assertions awaiting review.

`manifest.json` pins the inputs and records coverage and validation results.
`measure-groups.json` explains grouping; `candidate-dispositions.jsonl` preserves
each worker disposition with its namespace. `expanded/` contains the combined
candidate tables. Source field values remain verbatim; only declared ID references
are remapped. No canonical inventory, review decision or public count is generated.
The combined `expanded/` and candidate-disposition payloads remain ignored locally
pending evidence, excerpt and publication-rights review. Their output hashes are
public in the manifest; the complete snapshot is also retained under
`/data0/moratorium-refresh-2026/census-review-v1`. Only reviewed public projections
may be published. Preserving private source claims is not permission to republish
every worker excerpt.

Rebuild into a new directory with `scripts/build_ballot_census.py`, the v3 frozen
queue and retained terminal job outputs. Never overwrite a review snapshot. Review
the manifest's source paths and hashes before reuse; schema success is not evidence
or legal acceptance. Election-result observations must not be added to moratorium
counts. Census additions, identity review, evidence validation and legal promotion
remain separate operations.
