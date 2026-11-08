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

The current registry explicitly includes 48 observations, excludes three, leaves
two reviewed-unresolved, and leaves 394 unreviewed. The exploratory candidate
pool has 444 observations; only the 48 explicit inclusions belong to the reviewed
scope view. These are observations, not necessarily unique instruments.

The existing `md-hb0293-sb0056-2026` exclusion concerns secure student/workforce
research data. The new exclusions, PA HB 2153 and WY SF 76 (2026), concern revenue
distribution rather than infrastructure conditions; all raw rows remain intact.
CA AB 2170 and WY HB 155 (2026) remain unresolved pending authoritative
applicability and baseline cross-reference evidence respectively. The
[52-record review receipt](../work/research/2026-11-08/policy-52-scope-reconciliation/README.md)
describes the primary, independent and coordinator review.

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
