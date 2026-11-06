# Advisory mechanism and contest-scope evidence correction

Status: applied at `ec673e134a864672403f88538ad53e66c83cd738536c3143436ee05429496c76`;
exact replay returns `already_applied`. Complete source/evidence preflight and
application verified all 523 claim bindings. All 263 tests and 42 subtests pass;
`make data site check` passes with zero errors and 489 existing warnings. All 53
audited numeric claims match. [Validation](validation.json) pins the receipts.

This packet addresses the five field-specific tasks found by the
[semantic-use audit](../../../audit/ballot-semantic-use-audit-2026-11-06.json).
Publication state is established by `preflight.json`, `apply.json` and `replay.json`,
not by this description of the prepared changes.

The coordinator directly reviewed nine physical PDF pages from five retained,
hash-verified source versions. Two distributed `gpt-6.1-terra` CLI jobs independently
reviewed the supplied page images and initial candidate for their assigned
advisory and Monterey Park scopes. Their reports are private; hashes, session IDs,
qualifications and coordinator refinements appear in
[review reconciliation](review-reconciliation.json). They did not independently
review the final refinements or publish anything. CLI agreement is not legal truth.

Four advisory mechanism values remain unchanged. New source-specific claims and
field decisions replace indirect claim support for Wrightstown, Downe, Joliet
and Bloomington. Every earlier claim and decision remains retained.

- Wrightstown remains a classification of the reproduced proposed question about
  infrastructure and public-facing services associated with development within
  or affecting the village. Both pages are now explicitly reviewed and reproduced
  in the visual receipt. The final ballot remains unrecovered, and the question
  does not authorize contracts, expenditures, zoning approval or utility extension.
- Downe's sample question and interpretive statement support advisory development
  sentiment. Separate ordinance history and actual legal force remain unresolved.
- Joliet's notice addresses township voters and a separate city council. An
  affirmative answer supports construction; it is not council approval or a
  territorial identity assertion.
- Bloomington's specimen supports an advisory moratorium request. Restriction
  territory is now unresolved rather than filled with an electorate's name.
  A new `unresolved` geography decision supersedes the earlier accepted decision.

Monterey Park's physical page8 is a final official, city-labelled Measure NDC
canvass with precinct, vote-by-mail and grand-total rows. This supports completion
at city-total scope. Pages1,4,6 preserve reported adoption and the separate June26
county / June30 city-clerk certification phases. The immutable predecessor is
retained; a new result observation explicitly supersedes it. Five existing claims
are rebound to the successor with unchanged source versions and values, plus one
new completion/scope claim. Counts, certification, percentage-denominator limits,
unassigned ballot-vote differences and current-law qualifications remain unchanged.
No later-amendment search or fresh retrieval is implied.

The prepared delta is one result observation, eleven claims and thirty-five
decisions. Existing-row changes are limited to four provisions' claim references
and two geography fields, as pinned in the [preservation check](preservation-check.json).
All prior immutable records remain unchanged. Verified totals after application:
50 measures, 57 retained results, 50 current observations, five current certified
observations, 523 claims and 2,369 decisions. Local/state CSVs remain unchanged.

The initial preparation omitted a required identity-evidence hash. Subsequent
preflights caught a visual-receipt encoding mismatch and a non-schema disposition
literal. These failures occurred before identity or domain application; their
dispositions remain recorded. The final candidate uses existing schema enums,
explicit source hashes and reproducible multi-page visual receipts.

`scripts/prepare_ballot_semantic_lineage.py` prepared ephemeral candidate files.
`refine_after_review.py` records the source-review refinements; `schema-adjustment.json`
records the unapplied enum correction. The runner accepts an explicit retained
evidence-root configuration, performs complete evidence preflight, then separately
applies identities and publication. Existing source archives are required for
that verification. This is a bounded field-evidence correction, not a completed
inventory refresh, extraction evaluation, final release or deployment.
