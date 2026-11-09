# Policy-scope exports

`scripts/build_policy_scope_exports.py` reads `data/state_legislation.csv` and
`data/state_policy_scope_reviews.jsonl` and produces deterministic files in
`data/policy-scope/`. Run the script to regenerate and add `--check` to verify
all bytes and the exact file set. Unexpected files cause an error and are not
removed. The receipt hashes inputs and each CSV, records each partition's IDs,
and has no generation timestamp. A missing registry has a null hash and means
all observations are unreviewed. Invalid IDs, metadata collisions, invalid
review history, stale identity guards, and incompatible active scope fail closed.
Output replacement is atomic per file, not as a multi-file transaction; run
`--check` after an interrupted write.

- `all-annotated.csv` preserves every raw row and its order, adding
  `scope_review_status` and `scope_decision_id` (blank without a decision).
- `reviewed-included.csv` contains only explicit active include decisions for
  `data-center infrastructure policy analytical census`. This is the only
  output suitable as reviewed scope inclusion; a header-only file is valid.
- `not-explicitly-excluded-candidates.csv` excludes explicit reviewed excludes,
  but retains unresolved and unreviewed observations and their statuses. It is
  an exploratory candidate pool, not a reviewed or eligible infrastructure census.
- `receipt.json` gives input fingerprints, partition counts and IDs, and hashes
  of the three CSVs. The receipt cannot contain its own hash.

The current registry explicitly includes 377 observations, excludes 19, leaves
52 reviewed-unresolved, and leaves zero unreviewed. The exploratory candidate
pool has 429 observations; only the 377 explicit inclusions belong to the reviewed
scope view. These are observations, not necessarily unique instruments.

The existing `md-hb0293-sb0056-2026` exclusion concerns secure student/workforce
research data. The new exclusions, PA HB 2153 and WY SF 76 (2026), concern revenue
distribution rather than infrastructure conditions; all raw rows remain intact.
CA AB 2170 and WY HB 155 (2026) remain unresolved pending authoritative
applicability and baseline cross-reference evidence respectively. The
[52-record review receipt](../work/research/2026-11-08/policy-52-scope-reconciliation/README.md)
describes the first primary, independent and coordinator review. The
[90-record follow-up](../work/research/2026-11-08/policy-scope-wave2-reconciliation/README.md)
adds 77 includes, two excludes and 11 unresolved decisions. Explicit official
legislative summaries can establish a proposal’s infrastructure topic without
settling operative terms or current law. Composite observations may contain
several instruments or both related and unrelated provisions; inclusion does
not accept every component or resolve instrument deduplication.

Scope review does not establish current law, legal force, or all-record freshness.

The selector and exports are prerequisites for the full refresh, not evidence
that existing consumers use them. The seven sibling consumers and other affected
publication and analysis surfaces still require their own integration, review,
validation and explicit disposition under the research plan.

The output boundary is the checkout root (the resolved target of a symlinked
checkout is allowed). Every output path component beneath that boundary, the
output directory, and existing output entries must not be symlinks. Callers
using another output location must supply its existing trusted boundary. This
check assumes no concurrent adversarial filesystem mutation.

A new-format release candidate verifies the complete scope output and the
`policy_scope_review` summary against the selected committed inputs before
writing a candidate. Offline verification repeats the check in the restored
tree; historical candidates without the exporter retain their prior behavior.

The [next 90-record wave](../work/research/2026-11-08/policy-scope-wave3-reconciliation/README.md) adds 76 includes, two excludes and 12 unresolved decisions. Its source routing includes the previously retained Indiana bill and signed Maryland order; neither required a new source to establish scope.

The [third 90-record follow-up](../work/research/2026-11-08/policy-scope-wave4-reconciliation/README.md) adds 73 includes, three excludes and 14 unresolved decisions, retaining all raw observations and remaining applicability gaps.

The [final 124-record wave](../work/research/2026-11-08/policy-scope-wave5-reconciliation/README.md) adds 100 includes, nine excludes and 15 unresolved decisions. Every raw observation now has a scope disposition; freshness and current-force review remain separate and incomplete.

The [A5462 second-reprint review](../work/research/2026-11-09/post-release-qa/new-jersey-a5462-adjudication.json) includes a versioned infrastructure-policy observation whose explicit data-center definition was replaced by a broader commercial-load definition. Inclusion preserves the supported legislative history; deleted wording is not treated as operative final text, and the pocket-vetoed proposal is not current law.
