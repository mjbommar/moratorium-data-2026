# Applied-field and collection accounting — November 7, 2026

Canonical-file inspection: `2026-11-07T08:51:42.191818+00:00`. Frozen collection-audit observation: `2026-11-06T12:12:45.614763+00:00`. Neither clock is a source-publication or legal-force verification date.

| Dataset | Current rows | Rows with logged edits | Latest field values tracked | Match current CSV |
|---|---:|---:|---:|---:|
| inventory | 1330 | 706 | 2204 | 2204 |
| state_policy | 442 | 113 | 324 | 324 |

Mechanical lineage is not substantive review or the completed freshness funnel. Unchanged confirmations, source authority, complete field coverage and current force are not inferred from edits, worker outcomes or matching last values. Only November 5–7 receipts are selected. Historical reports remain unchanged; the separate NJ identity/display split remains outside these receipt formats.

| Current ID assignment in frozen queue | Inventory | State policy |
|---|---:|---:|
| returned_unresolved | 781 | 65 |
| returned_other_outcome | 501 | 369 |
| excluded_completed_pilot | 8 | 6 |
| not_assigned_in_this_queue | 40 | 2 |

The 40 local IDs outside the original queue include later discoveries, not automatically unattempted research. Seattle retirement removes one original assigned duplicate from the current-row denominator while retaining aliases. The two unassigned policy IDs are later CA AB2469 and NJ A4696 records. Each current ID appears once.

[Ledger/input hashes](refresh-field-accounting-2026-11-07.json). [Scoped substantive source review](../research/2026-11-07/executive-force-review/README.md). Broader confirmed/changed/unresolved/not-attempted source freshness remains open.

Reproduce in the retained research workspace (queue/specs and terminal answers are required):

```sh
python3 scripts/build_refresh_accounting.py \
  --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json \
  --audit work/audit/return-review-summary-2026-11-06.json \
  --receipt-date 20261105 --receipt-date 20261106 --receipt-date 20261107 --include-fields \
  --canonical-observed-at '2026-11-07T08:51:42.191818+00:00' \
  --output work/audit/refresh-field-accounting-2026-11-07.json
```
