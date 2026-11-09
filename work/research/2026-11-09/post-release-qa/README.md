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

## Recovered-source follow-up applied

Two targeted HTTP fetches recovered the missing full Lavon syndicated report and Ashland WSAZ report. Independent Terra reviews and coordinator source review support [seven additional guarded cells](followup-field-application.json), with [source hashes, locators and exact before/after guards](followup-evidence-ledger.json). These revise two records already corrected in the first batch; they are seven additional edits, not seven additional records.

[Lavon](lavon-followup-review.md) now records the August-metadata/mid-November-body chronology conflict explicitly. The full report supplies the conditional 90-day term and possible extension. It cannot establish a verified August vote, operative period or identity with the October proposal.

[Ashland](ashland-followup-review.md) now records February 26 as a news-based weekday/publication inference, with normalized date marked `unverified`. WSAZ describes both six months and 180 days; the discrepancy and absent effective-date anchor prevent an inferred endpoint. Early termination remains open. Counts and recorded stages are unchanged.

Both new bodies/texts are hash-checked and versioned in the existing private evidence archive; public receipts contain references and paraphrased findings. No broad discovery, paid search or model API trial was repeated. Immutable release assets remain unchanged.

## Oliver official compilation follow-up

The [independent follow-up](oliver-followup-review.md) verifies the county index → ordinance page → 122-page zoning compilation chain. The compilation has distinct cover-approval and internal effective-date statements and does not supply an executed Resolution 2025-02, recording or publication proof, or a defensible phase-two endpoint. The existing row already captures the actual May vote and conflicting term language, so **no canonical change** is warranted. The [bounded disposition](oliver-followup.json) preserves the precise remaining evidence needs; it does not infer termination from general zoning or absence of text matches.

[Native source continuity](native-source-continuity.json) verifies all five post-release source versions (Lavon, Ashland and three Oliver documents) against their original capture timestamps and native payload readback. Bodies and texts remain private. These checks do not renew legal-force acceptance.

## Held ballot authority follow-up

The [independent Morgan/Ottawa review](held-ballot-followup-review.md) retains both holds after eleven bounded source/index/script captures. Morgan’s official August 12 minutes concern a separate Cook County separation action; they do not establish the data-center advisory question. Ottawa’s actual AJAX search responses narrow the source search but do not identify the official question corresponding to the county return. No canonical measure, result, count or legal-effect assertion changes.

[Structured dispositions](held-ballot-followup.json), [source receipts](held-ballot-source-receipts.json) and [native readback verification](held-ballot-native-continuity.json) preserve exact capture versions and limits. [Portal retrieval notes](portal-retrieval-notes.md) record WordPress raw-JSON handling and CivicEngage AJAX/redirect differences for reuse. A successful transport, an empty readability extraction or an unhelpful site index does not settle the underlying election question. All source bodies remain private.

The [working-source Pages run](deployment-sync-timeout.json) built successfully but timed out in GitHub’s `syncing_files` phase after ten minutes. Latest hosted follow-up verification remains open; a green build is not a successful deployment. The completed receipt commit supplies the next deployment attempt. Qualified release assets remain immutable and available.
