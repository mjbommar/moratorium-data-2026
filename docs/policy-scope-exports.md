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

The current registry has one exclusion: `md-hb0293-sb0056-2026` is a compound
historical observation of secure student/workforce research data, not an
infrastructure action. Its raw row and identity remain intact; the export does
not split it into instruments. The raw 447 observations are not necessarily
447 unique instruments. The current partition is 0 included, 1 excluded,
0 unresolved, and 446 unreviewed; the 446 candidates are not reviewed in-scope.
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
