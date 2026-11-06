# Coordinator discovery accounting — November 6, 2026

This is a read-only reconciliation of the 185-candidate discovery ledger and its retained review packets. It is not an inventory-wide freshness audit or release approval. The [JSON report](discovery-coordinator-accounting-2026-11-06.json) pins the ledger, current inventory and all 30 referenced packet hashes.

| Candidate disposition | Count | Meaning |
|---|---:|---|
| Reviewed additions | 38 | Source-scoped additions, including pending and historical instruments; not 38 current enforceability findings |
| Covered by existing instrument | 1 | No additional record required for that candidate |
| Reviewed but withheld | 146 | Specific source, identity, date, final-action or later-history requirements remain |
| Awaiting coordinator review | 0 | Frozen coordinator queue fully dispositioned; evidence gaps remain |
| Total | 185 | Frozen discovery candidate denominator |

The 185 processed candidates are not 185 resolved legal histories. The full baseline comparison separately reports 40 new local records; Hayward and Dubuque were added earlier, and Hayward is subsequently covered by the discovery ledger. Same-name inventory IDs remain routing aids rather than one-to-one instrument assertions, notably the two Kent candidates.

The byte check verifies explicit candidate fingerprints and nonempty source-version references for 179 candidates. Six candidates use older alternate packet layouts: their packet presence and hashes are checked here, while their substantive/source checks remain in the original scoped receipts. The audit does not silently treat these layouts as newly reverified source proof.

The helper re-verifies 185 of 189 distinct source versions referenced by explicit candidate packets: 183 original discovery acquisitions and two Illinois followups. Four original Maine pilot body/review-text versions use explicit source-specific paths and are independently hash-verified in the [Maine packet](../research/2026-11-06/maine-discovery-review/review.json); they remain deferred to that receipt by this helper. Wells page-2 OCR stays separate from its original extraction; the Wiscasset results text hash pins original HTML. No complete extraction/native migration, renewed factual acceptance or current-force proof follows from these byte checks.

The original 333 collection jobs and 17 distributed `gpt-6.1-terra` review jobs remain terminal as recorded in their own audits; none was restarted for this accounting. Job completion, source acquisition, coordinator review, canonical addition and legal-force acceptance remain different stages.

Rebuild from the repository root on the admitted private workstation:

```sh
.venv/bin/python work/audit/discovery-coordinator-accounting-2026-11-06.py
```

The helper uses explicit original-discovery directories and the Illinois followup directory, fails on unknown dispositions or hash mismatches, and exports only hashes, scope and candidate metadata. Other acquisition roots require explicit routing; no directory is guessed from a source URL. A later ledger change requires regenerating this report and reconciling the table. The frozen coordinator queue is complete. Remaining work includes the 146 withheld cases' source/legal gaps, the separate Jay ballot lead, all other plan gates, consumer reconciliation and final release/deployment verification.
