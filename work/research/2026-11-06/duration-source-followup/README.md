# Original-term source follow-up

Three previously withheld cases were revisited using retained original documents. Two disjoint Codex CLI jobs were invoked with gpt-6.1-terra; coordinator inspection covers four PDF pages. [Review provenance](review.json) retains exact source body/text and render hashes. No new source acquisition or extraction-model calls occurred.

| Case | Source and disposition |
|---|---|
| Carroll County AR | Published adopted Emergency Ordinance 2026-17, physical page 9: twelve months from effectiveness unless repealed earlier. Correct calendar encoding and preserve that condition; replace obsolete news-only/365-day status wording. Published printed signature notations are distinct from a separately inspected county original. |
| South Fork CO | Published Ordinance 2026-03 notice, physical page 22: one year, with code-amendment alternatives. Correct calendar encoding only; preserve Town of Center/South Fork mismatch and the earlier-of/whichever-occurs-later wording without settling either. |
| Ormond Beach FL | Physical pages 8–9 of the second-reading attachment: proposed eighteen-month term, separate conditional ninety-day extension authority, blank signature lines. No row change; final adopted wording remains unverified. |

Six fields on two rows change; all other values and all 1,330 IDs are preserved. Ormond Beach remains byte-for-byte unchanged. No enactment classification or endpoint changes. Carroll’s inherited active classification is explicitly distinguished from later-action/current-force evidence; two verification requirements remain. The proposed Florida draft is not treated as final adopted text.

The frozen 474-case closure and original 223-withheld list remain historical. The [supplemental requirements](remaining-original-term-requirements.json) retain 222 outstanding source requirements: South Fork remains listed for its interpretation/identity issues despite corrected unit encoding. Closing Carroll’s original-term source question does not close its current-force history.

Use the explicitly named `ar-answers.json`, `co-answers.json` and `fl-answers.json` with `scripts/apply_research.py --no-candidates`. Exact expected prior values guard edits. The Florida decision is unresolvable and is skipped; replay reports six already-applied fields and zero touched rows. Two previously absent original source versions are imported into the private-backed archive; raw text/images remain ignored. Source observation dates remain unchanged.

Full validation is recorded in `validation.json` after the ongoing data/site/check completes. Headline local/state/ballot counts are unchanged. This does not complete all-record freshness, source recovery or the final release.
