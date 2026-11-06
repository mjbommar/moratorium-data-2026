# Current collection and edit accounting — November 6, 2026

This replaces partial-run denominators for current collection diagnostics, while preserving the November 5 report as history. It is **not** the completed legal-status freshness funnel.

All 333 original distributed CLI jobs are finished; none remain unstarted. Of these, 174 pass the current mechanical review-readiness gate, and the audit found no reusable-evidence integrity issues. A terminal return or located quote is not substantive acceptance.

| Dataset | Current records | Returned unresolved | Returned other outcome | Completed pilot excluded from queue | Not assigned in this queue |
|---|---:|---:|---:|---:|---:|
| inventory | 1,293 | 782 | 501 | 8 | 2 |
| state_policy | 442 | 65 | 369 | 6 | 2 |

Collection categories are disjoint within each dataset. Pilot exclusion and unassigned new records describe this queue, not an absence of coordinator research. Every current ID appears exactly once; counts and CSV byte hashes are pinned in the [record ledger](refresh-record-accounting-2026-11-06.json). The [return audit](return-review-summary-2026-11-06.json) retains job-level evidence/schema diagnostics.

The editorial dimension only counts the historical November 5 apply receipts selected by `scripts/build_refresh_accounting.py`; it does not cover all later coordinator edits and must not be used as a total changed-record or reviewed-record count. Neither dimension assigns a new legal-force observation date.

Remaining freshness work: reconcile substantive review decisions and source dates per current local/state ID; distinguish confirmed unchanged, corrected, unresolved, not attempted and source unavailable under the release definition; independently review source authority, exact field support and later legal events. Records with unresolved older support must retain that older date rather than being relabeled current because a job finished.

Reproduce with the current frozen queue and retained run directory:

```bash
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python scripts/audit_refresh_returns.py --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json --runs /data0/moratorium-refresh-2026/job-runs --output work/audit/return-review-summary-2026-11-06.json
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python scripts/build_refresh_accounting.py --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json --audit work/audit/return-review-summary-2026-11-06.json --output work/audit/refresh-record-accounting-2026-11-06.json
```
