# Refresh collection and edit accounting

Snapshot: 2026-11-06T01:11:56.217393+00:00. All 333 distributed jobs have finished; substantive review remains incomplete.

This is mechanical collection and edit accounting, not the completed release freshness funnel. Schema-valid decisions, located quotes and edits do not establish source authority, complete field coverage or current legal force. Each collection column sums independently to its dataset total.

| Collection stage | Local inventory | State policy |
|---|---:|---:|
| Schema-valid unresolved return | 782 | 65 |
| Schema-valid other worker outcome | 501 | 369 |
| In running jobs | 0 | 0 |
| Queued | 0 | 0 |
| Excluded as completed pilot | 8 | 6 |
| Outside this queue | 2 | 0 |
| Terminal without complete valid return | 0 | 0 |
| **Total** | **1293** | **440** |

| Edit-ledger observation | Local inventory | State policy |
|---|---:|---:|
| Has a November 5 apply-ledger change | 430 | 6 |
| No matching November 5 apply-ledger change | 863 | 434 |

The edit dimension counts records with at least one logged change. It does not count completed reviews or confirm that every field is current. Both inventory and legislation ledger formats are included; older receipts are excluded.

The two local records outside this queue were added after its baseline. They require their own research evidence, rather than being treated as missing queue jobs:

- `ca-hayward-2026`
- `ia-dubuque-county-2026-2`

Ballot census, state/local discovery, expanded canonical promotion, project/disclosure sources, sibling consumers and publication remain separate required workstreams. This report does not close them or assert record-level source availability.

Reproduce from the retained live-return audit with:

```bash
BCPY=/home/mjbommar/projects/bc/bc-modules/.venv/bin/python
$BCPY scripts/audit_refresh_returns.py --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json --runs /data0/moratorium-refresh-2026/job-runs --output /data0/moratorium-refresh-2026/return-audit-current.private.json
$BCPY scripts/build_refresh_accounting.py --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json --audit /data0/moratorium-refresh-2026/return-audit-current.private.json --output work/audit/refresh-record-accounting-2026-11-05.json
```

The JSON pins input hashes and lists every canonical ID. Re-running against live jobs produces a later snapshot; it does not reproduce the earlier job state.
