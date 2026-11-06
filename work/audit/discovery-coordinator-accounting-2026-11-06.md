# Coordinator discovery accounting — November 6, 2026

This is a read-only reconciliation of the 185-candidate discovery ledger and its retained review packets. It is not an inventory-wide freshness audit or release approval. The [JSON report](discovery-coordinator-accounting-2026-11-06.json) pins the ledger, current inventory and all 25 referenced packet hashes.

| Candidate disposition | Count | Meaning |
|---|---:|---|
| Reviewed additions | 26 | Source-scoped additions, including pending and historical instruments; not 26 current enforceability findings |
| Covered by existing instrument | 1 | No additional record required for that candidate |
| Reviewed but withheld | 99 | Specific source, identity, date, final-action or later-history requirements remain |
| Awaiting coordinator review | 59 | Completed worker recommendations still need substantive coordinator processing |
| Total | 185 | Frozen discovery candidate denominator |

The 126 processed candidates are not 126 resolved legal histories. The full baseline comparison separately reports 28 new local records; Hayward and Dubuque were added earlier, and Hayward is subsequently covered by the discovery ledger. Same-name inventory IDs remain routing aids rather than one-to-one instrument assertions, notably the two Kent candidates.

The byte check verifies explicit candidate fingerprints and nonempty source-version references for 120 candidates. Six candidates use older alternate packet layouts: their packet presence and hashes are checked here, while their substantive/source checks remain in the original scoped receipts. The audit does not silently treat these layouts as newly reverified source proof.

All 127 distinct source versions referenced by those explicit candidate packets were read back and hash-verified: 125 original discovery acquisitions and two Illinois followups. Exact review-text bytes include separately retained derivations where applicable; original extraction and review text are not conflated. This check does not re-read every rationale, re-inspect PDF images, renew factual acceptance, or establish current force. It does not prove complete native-store migration or extraction coverage.

The original 333 collection jobs and 17 distributed `gpt-6.1-terra` review jobs remain terminal as recorded in their own audits; none was restarted for this accounting. Job completion, source acquisition, coordinator review, canonical addition and legal-force acceptance remain different stages.

Rebuild from the repository root on the admitted private workstation:

```sh
.venv/bin/python work/audit/discovery-coordinator-accounting-2026-11-06.py
```

The helper uses explicit original-discovery directories and the Illinois followup directory, fails on unknown dispositions or hash mismatches, and exports only hashes, scope and candidate metadata. Other acquisition roots require explicit routing; no directory is guessed from a source URL. A later ledger change requires regenerating this report and reconciling the table. Remaining work includes all 59 reviews, the 99 withheld cases' evidence dispositions, other plan gates, consumers and final release/deployment verification.
