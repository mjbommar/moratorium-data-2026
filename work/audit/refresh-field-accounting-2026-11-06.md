# Applied-field lineage accounting — November 6, 2026

The selected November5and6applyreceipts cover the current CSV inputs by hash. This extends the earlier November5-only editorial snapshot; original historical reports remain unchanged. It is not completed substantive record review, renewed legal-force verification or the final freshness funnel. The collection observation time comes from the separately pinned return audit.

| Dataset | Current records | Records with applied changes | Last applied field values tracked | Match current CSV |
|---|---:|---:|---:|---:|
| inventory | 1326 | 481 | 1729 | 1729 |
| state_policy | 442 | 32 | 116 | 116 |

Every record changed since the September baseline, including newly added records, has at least one selected apply receipt. This is row-level edit coverage, not proof that each field or legal interval was reviewed. Last-value equality means no later value drift from those applied events; it is not source reacceptance. Derived `has_verify_tags` and `verify_count` changes remain separate from explicit field events.

The New Jersey display split is documented separately in [identity-split.json](../research/2026-11-06/nj-policy-wave1/identity-split.json), outside these apply-receipt formats. Its `bill` field is not included in the 116 policy-field count. The optional explicit-rename resolver is tested but finds no such rename events in these selected receipts; it does not merge the separate A4696 identity. The JSON pins receipt, queue, answer and packet hashes and lists field fingerprints per current ID. Unchanged confirmations and unresolved source/current-force reviews are not counted as applied changes.

Reproduce:

```sh
python3 scripts/build_refresh_accounting.py \
  --queue work/jobs/2026-11-05-recovery/complete-queue-v3.json \
  --audit work/audit/return-review-summary-2026-11-06.json \
  --receipt-date 20261105 --receipt-date 20261106 --include-fields \
  --output work/audit/refresh-field-accounting-2026-11-06.json
```
