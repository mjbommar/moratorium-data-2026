# Continuing QA after v2026.11.9

The release is frozen and public with pending-QA qualifications. The complete
[record-disposition ledger](../../2026-11-08/full-record-dispositions/README.md)
remains in scope; the first batch below prioritizes material local identity/stage
conflicts and does not discard the other outstanding questions.

| Record | First question | State |
|---|---|---|
| ky-boone-county-2026 | Is the Kentucky observation a proven misattribution of the existing Indiana instrument? | Independently reviewed; see disposition below |
| tx-lavon-2026 | Does the August adoption attribution concern Lavon, another city, or another action? | Independently reviewed; see disposition below |
| ky-ashland-2026 | Does the source explicitly terminate the pause, or merely adopt later zoning? | Independently reviewed; see disposition below |
| nd-oliver-county-2025-p2 | Which motion/resolution and recording/publication provisions establish this phase's term? | Independently reviewed; see disposition below |

The two finite Terra review jobs reuse prior artifacts and exact source versions.
No nationwide discovery or previously completed full-row review is repeated.
Material changes require independent evidence adjudication and current row/value
guards; identity retirement uses the existing separate registry protocol. Missing
source evidence remains explicit. No unreviewed proposal changes canonical data.

A post-publication website check also caught the old April release footer and
an outdated historical-chart caption. The generator now derives publication and
source-cutoff dates separately from metadata and accurately labels recorded dates
and the first stored sector. Numeric chart data is unchanged. Generator and timeline
checks pass; this presentation correction leaves frozen release assets unchanged.

## Applied corrections

Independent adjudication accepted four proposed cells, modified two, rejected four, and added two dependent date-precision corrections. The resulting [eight-cell application](field-application.json) changes Lavon and Ashland without changing their recorded stages. Lavon’s proposed 90-day term is attributed to a resident rather than an enacted instrument; the August date and final action remain unresolved. Ashland’s supported February month replaces an unsupported exact day; the original term and termination remain open.

The [guarded identity retirement](identity-plan.json) removes `ky-boone-county-2026` as a source-proven duplicate of `in-boone-county-2026`. Official Indiana June 15 minutes identify Lebanon, Tim Beyer and Ordinance 2026-08, matching the cited report and existing Indiana observation. This clears this observation’s jurisdiction/identity question, not the existence of any separate Kentucky measure. The append-only registry retains its original row and permanent ID; every Indiana survivor field remains unchanged. [Application](identity-application.json), [idempotent replay](identity-replay.json) and [alias lookup](lookup.json) are retained.

Working counts are now **1,329 local records**, **447 policy records**, **1,776 active raw IDs**, and **1,500 unresolved record dispositions**. The retired observation is separately retained in the disposition ledger. The immutable v2026.11.9 release has 1,330 local records and its original 1,777-record review proof remains archived. No release tag or asset is replaced.

| Question | Disposition / next evidence needed |
|---|---|
| Boone wrong-jurisdiction duplicate | Cleared for this observation by matching official Indiana minutes and report; alias preserved. |
| Lavon August attribution and October/November ordinance identity | The full original syndicated report is now recovered and explicitly reports approval; the body also conditions official approval on a mid-November second reading, so independent follow-up is reconciling its conflicting chronology. Official earlier minutes/final ordinance still needed. November 17 is scheduled, not an observed vote. |
| Ashland original moratorium and termination | Exact-day overstatement corrected; obtain original February ordinance or explicit later termination. Later zoning alone does not prove termination. |
| Oliver phase-two term | Open: executed resolution and recording/publication evidence needed to reconcile the 90-day motion with the standards-dependent resolution. Proposed unknown-to-active recategorization was rejected. |

All three data-dependent maps and current tables/site are regenerated from the revised CSV. The four legal maps retain their explicitly historical edition. Validation receipts are recorded with this batch. Outstanding source gaps remain in scope; this increment is not universal current-force certification.

The [targeted source recovery](lavon-source-recovery.json) succeeded on November 9 after this batch applied. It supplies the missing conditional second-reading context and exposes a publication/body chronology conflict; its independent follow-up is separate from the first batch and no further canonical edit is automatic.
