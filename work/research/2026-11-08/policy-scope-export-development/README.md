# Policy-scope export integration

The canonical raw policy CSV remains 447 historical observations. The separate scope registry partitions these into zero reviewed includes, one reviewed exclusion, zero reviewed unresolved and 446 unreviewed observations. The excluded compound Maryland observation concerns secure research-data sharing. No ID or raw row was deleted or split.

The new [exports](../../../../data/policy-scope/receipt.json) preserve every raw row with scope status, supply a header-only reviewed-inclusion view and a separately labelled exploratory candidate pool. The 446 candidates are not accepted infrastructure census rows. The summary endpoint now exposes these distinct counts without changing legacy raw totals. The [contract](../../../../docs/policy-scope-exports.md) defines ordering, input/output hashes, missing-registry behavior and integrity checks.

Independent review initially required changes for stale release artifacts, a missing identity header on empty input, and redirected output ancestors. Those fixes are implemented. The coordinator inspected the corrections and reran 37 focused tests, all passing. A real current-tree scope check verified four outputs and the additive summary. Full `make check` passed with zero errors, 505 warnings and 68 matched numbers before those bounded fixes; focused export/release/handoff tests and live scope checks cover the later changes. Full restored release and handoff verification are separate delivery evidence, recorded when actually completed.

Published data guidance now links the exports. Generated state pages distinguish raw policy observations from scope inclusion. Stale data-page references were corrected to 61 retained result observations and validation profile 1.0.4; the exact-sector Python example now uses the typed sector array.

This increment does not establish current legal force, all-record freshness, reviewed inclusion of the remaining 446 rows, integration in all seven siblings or the final GitHub release. Raw inventory counts, classifications, ballot counts and vote totals are unchanged.
