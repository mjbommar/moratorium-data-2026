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

The first two finite Terra review jobs reused prior artifacts and exact source versions.
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

Working counts are now **1,328 local records**, **447 policy records**, **1,775 active raw IDs**, and **1,481 unresolved record dispositions**. Both retired observations are separately retained in the disposition ledger. The immutable v2026.11.9 release has 1,330 local records and its original 1,777-record review proof remains archived. No release tag or asset is replaced.

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

## Verified deployment and complete residual-question index

[Hosted verification](hosted-verification.json) records the successful retry and byte-for-byte matches for six selected deployed files at `c6e141a`: inventory CSV, summary, landing page, Kentucky/Texas pages and held-ballot receipt. This supersedes the earlier deployment timeout for those selected files; it is not a full link audit or new factual certification.

The [complete residual index](outstanding-record-questions.jsonl) covers every one of the current **1,480 unresolved raw records**: 1,219 local and 261 state-policy observations. Every entry has explicit recorded questions and an exact current-row fingerprint. The [verification](outstanding-queue-verification.json) requires exact agreement with the active disposition ledger, excluding the preserved retired alias. This reuses previously performed reviews; it is not a new 1,499-record research pass or proof that every question is resolved. [Three held ballot payloads](outstanding-held-ballot-questions.json) are separately retained and may overlap canonical records.

The index recovered nested residuals that a flat `unperformed_checks` reader missed. A [four-record Maine audit](maine-terminal-disposition-review.md) then identified actual party-field questions in three records and one blanket unresolved misclassification for LD 307. The [guarded accounting correction](maine-disposition-application.json) records LD 307 as confirmed-unchanged within its named, failed-bill scope. Its veto and proposed-only endpoint are supported; no successor-law inference or legislative-status edit is made. At that checkpoint, dispositions were 1,499 unresolved, 95 corrected-resolved, 181 confirmed-unchanged and one superseded duplicate. Canonical CSV values and ballot totals remain unchanged.

The [index builder](build-outstanding-queue.py) takes the retained private review ledger as an explicit input and publishes paraphrased review residuals with private locators removed. Post-release source questions supersede earlier Lavon/Ashland/Oliver/Renton precision and hearing questions, and the Maine audit supplies the three specific party questions. The source-ledger digest and overlay digest are pinned; missing questions fail the completeness review instead of becoming invented work. New capture admission must first check these retained questions, exact source versions and earlier attempts.

## Renton adoption and hearing confirmed from official minutes

The [four-case routing disposition](material-local-routing-dispositions.json) prioritizes actual missing final-action/instrument questions and rejects pre-meeting or invalid targets that cannot answer them. Covina, Brownsville and Cle Elum remain qualified; no new source fetch was admitted for their nonresponsive retained targets.

Renton’s official portal led to the August 17 and October 5 council minutes. [Independent review](renton-independent-review.md) confirms the all-aye roll-call adoption of Ordinance 6200 and the later data-center hearing/comments/closure. The [guarded two-cell application](renton-field-application.json) updates legal basis and current-status narrative; [evidence](renton-evidence-ledger.json) retains exact before/after values, source clocks and PDF locators. The October entry also refers to CDBG in its opening sentence, which is recorded as a source anomaly. Source capture/review occurred November 9; these are dated August/October events.

The full signed ordinance, operative anchor/end, exceptions and later force remain open. Recorded stage, typed duration/end, counts and all other rows remain unchanged. The Renton residual overlay removes the now-settled adoption/hearing questions while retaining the actual missing evidence. At the Renton checkpoint, unresolved raw records remained 1,499.

[Source continuity](renton-source-continuity.json) separates the two actual minutes from two HTTP200 error shells and seven portal/index/script captures, with body/text/native readback for all eleven. [Retrieval notes](portal-retrieval-notes.md#primegov-archived-minutes) preserve the successful route and the failed representation distinction. Weaker third-party proposed wording was superseded by the official minutes and was not applied.

## Terminal-bill residual audit: 55 records

The [55 guarded adjudications](terminal-residual-audit.json) audit actual named-record gaps rather than treating a generic successor-law disclaimer as a factual uncertainty. Three peer recommendations proposed closure; coordinator review retained Kentucky HB 372 because a 19-field guard and names-only bill page did not establish the recorded historical party values. The other 52 holds retain concrete party, text, scope, final-action or procedural questions. No hold was cleared by a text pattern or inactivity inference.

The [final South Dakota source confirmation](sd-terminal-confirmation.md) supports SB 177 (2025) and SB 239 (2026): recorded terminal actions and material proposal versions are supported, and four linked, session-specific official profiles establish the existing sponsor-party values. The [guarded accounting application](terminal-residual-application.json) changes only these two dispositions to confirmed-unchanged. No CSV value, legislative status, headline count or source event date changes. At that checkpoint, unresolved records totaled **1,497**, with 183 confirmed-unchanged, 95 corrected-resolved and one superseded duplicate across 1,776 active raw IDs.

[Source continuity](terminal-party-source-continuity.json) preserves four HTTP application shells and four actual rendered profiles separately. The new captures use the existing source reservation ledger and cap; the four browser renders are explicit, not misreported as HTTP profile evidence. [Retrieval notes](portal-retrieval-notes.md#session-specific-profile-rendering) record the method. The [residual index](outstanding-record-questions.jsonl) now carries the 53 specific remaining questions from this audit; other local, policy and held-ballot questions remain in scope.

[Renton hosted verification](renton-hosted-verification.json) separately records successful deployment and exact hosted-byte checks at `4fbea35`, including its corrected CSV/page and updated source-question ledger.


## South Dakota procedure and Hampden identity follow-up

[Independent procedural review](sd-procedure-independent-review.md) supports four guarded policy-cell corrections across SB 232, SB 234 and SB 235, with three append-only scope-review rebindings and no scope-membership or typed-stage changes. SB 232’s tabling is qualified because the official explanatory guide permits reconsideration; its whole-record question remains open. The recorded 41st-day deferrals support bounded failed-stage interpretations for SB 234 and SB 235. The guides are dated 2021 and are not presented as formal 2026 standing rules. See [application](sd-procedure-field-application.json), [disposition accounting](sd-procedure-disposition-application.json), and [source continuity](sd-procedure-source-continuity.json).

[Hampden provenance review](hampden-identity-review.md) links both September observations to the same ordinance PDF, with a September manifest body hash matching the retained source. Official May and June minutes identify Ordinance 18. The misleading OCR “13” does not establish a second instrument. The [guarded retirement](hampden-identity-application.json) preserves the alias and full original row; all 1,328 surviving rows are unchanged by this transaction. [Replay](hampden-identity-replay.json) confirms idempotence. This resolves identity, not current enforceability.

At that checkpoint, dispositions were **1,495 unresolved, 97 corrected-resolved, 183 confirmed-unchanged and zero active superseded duplicates**, covering all **1,775 active raw IDs**. Two post-release retired aliases remain in history. The frozen release remains unchanged.

[Combined validation](procedure-identity-validation.json) verifies exact four-cell policy changes, unchanged surviving local rows, scope-registry fingerprints, complete current disposition/index membership and nine focused build/data checks. Three affected maps were regenerated in PNG, PDF and SVG; historical legal-map editions remain dated.

## Further South Dakota source capture

The [next targeted source check](sd-howard-source-followup.json) recovers the exact linked 2026 Taffy Howard profile and verifies its Republican party field, matching existing CSV values. [Independent sponsor-and-party adjudication](sd-howard-independent-review.md) confirms the existing cells and clears that question. No whole-record QA disposition is promoted. The rendered session schedule lists upcoming meetings and does not prove a final bill outcome. Both source versions were archived and replayed through the existing native store with verified body/text readback. At that checkpoint the residual index retained only SB 232’s terminal-disposition questions and the whole-record unresolved count was unchanged. The final-session review below subsequently resolves them.

The [hosted verification](procedure-identity-hosted-verification.json) confirms successful deployment of `62eaca2` and exact bytes for five current data/site/QA files.

The [formal-session source continuity receipt](sd-session-source-continuity.json) retains five further versions: the official rendered 2026 General Information page and its directly linked Joint Rules, Senate Rules, calendar and final legislative index. The index states that the session concluded March 30. Formal committee recall exceptions remain explicit. The subsequent independent review and guarded application are linked below; retrieval alone did not clear them.

## Final-session review applied

[Independent review](sd-session-independent-review.md) and [exact adjudications](sd-session-adjudications.json) clear the named recorded-stage questions for HB 1005, HB 1301, SB 193 and SB 232. The final index supplies post-session history; its session-specific member listings establish the remaining sponsor/party values, alongside prior material proposal-text review. Committee recall exceptions and SB 193’s final notice of intent to reconsider remain explicit. One [guarded status-narrative correction](sd-session-field-application.json) replaces the unsupported “never brought back” assertion with the final index’s recorded observation. Typed stage values and headline record totals are unchanged; one scope review is rebound without changing analytical membership.

[Disposition accounting](sd-session-disposition-application.json) closes three records unchanged and one corrected-resolved. At that checkpoint, totals were **1,491 unresolved, 98 corrected-resolved and 186 confirmed-unchanged**, across 1,775 active raw IDs. These are bounded named-bill QA conclusions, not current-law or successor-law certification. The frozen release remains unchanged.

[Batch validation](sd-session-validation.json) confirms the exact one-cell diff, unchanged local inventory, unchanged typed categories, single scope rebind, all 1,775 current IDs and 1,491 residual guards/questions. Nine focused checks pass. Maps and expanded ballot data are unchanged.

## Remaining failed-bill review applied

[Independent review](sd-remaining-failed-independent-review.md) and [adjudications](sd-remaining-failed-adjudications.json) clear HB 1198, HB 1246, SB 127 and SB 128 within their named failed-bill scope. The final index supplies missing action histories and session-specific member affiliations; retained proposal texts and adopted committee amendment evidence resolve version questions. Two [guarded party-cell corrections](sd-remaining-failed-field-application.json) replace obsolete verification annotations with source-supported Republican-lead/bipartisan-cosponsor descriptions. Typed stages, dates, local inventory and ballot data are unchanged.

[Disposition accounting](sd-remaining-failed-disposition-application.json) records two unchanged and two corrected-resolved closures. At that checkpoint, totals were **1,487 unresolved, 100 corrected-resolved and 188 confirmed-unchanged**, across 1,775 active raw IDs. Formal committee recall exceptions and source-observation limits remain explicit.

## Enacted South Dakota laws clarified

[Independent review](sd-enacted-independent-review.md) of the complete official Chapters 185 and 190, final index, volume authentication and SDCL 2-14-16 supports [ten guarded cells](sd-enacted-field-application.json) across HB 1038 and SB 135. Both signatures are March 24, separately recorded in March 30 index entries. Primary links now point to actual enacted copies; sponsor and provision summaries are clarified. Both acts prescribe no effective date. July 1 is recorded as the inferred regular-session default, explicitly subject to constitutional, veto and referendum qualifications in each status narrative. It is not an express date in the acts or proof of current effect.

[Adjudications](sd-enacted-adjudications.json) retain both whole-record holds and both `legal_effect_status=unknown` values. The residual index now asks the narrower referendum/effective-date and later-amendment/current-force questions. [Five new source versions](sd-enacted-source-continuity.json) were archived with native body/text readback; existing final-index evidence was reused. Raw source bodies remain private. Counts and typed stages are unchanged.

[Combined policy follow-up validation](sd-policy-followup-validation.json) verifies the exact twelve-cell diff, unchanged local inventory and typed stages/legal effects, four scope rebindings, conditional-date qualifications, two retained enacted-law holds, all 1,775 active IDs and all 1,487 residual row guards/questions. Nine focused checks pass; expanded ballot data and maps are unchanged.

## Local material questions and queue reconciliation

[Independent reconciliation](local-residual-reconciliation.md) and [guarded findings](local-residual-reconciliation.json) remove two obsolete requests to apply Cromwell and Watertown corrections already present in the current CSV. Their actual source questions remain open: the distinct later Cromwell proposal and Tuscola/Clinton instrument identity, terms and subsequent actions. No record is closed by accounting cleanup.

The [metadata extraction correction](residual-metadata-cleanup.json) removes 200 non-question metadata values from 15 entries while preserving every active unresolved ID and substantive source follow-up. Search attempt IDs, providers, queries, timestamps, host diagnostics and mechanical checks remain in the original evidence ledger; they are not factual questions.

[North Port independent review](northport-independent-review.md), [coordinator adjudication](northport-adjudication.json) and [seven-cell application](northport-field-application.json) qualify chronology, term, project, final-text and vote claims. The linked first-reading minutes establish the amended second-reading date, eighteen-month term, processing-versus-approval condition and Petrow dissent, but lack a numeric roll call or meeting start. The legislation HTML header records Passed and final action September 22; the detailed September 22 meeting results remain unavailable. The coordinator retains that positive recorded-passage evidence and does not relabel the instrument proposed-only. The date remains as a portal observation with unverified adoption-date confidence. Active category, record totals and typed endpoint remain unchanged; whole-record QA remains open.

[Three newly retained official versions](northport-source-continuity.json) have verified native body/text readback; the retained second-reading draft was reused. Normalized text omitted the legislation status header, so the actual HTML was inspected. The [six-file hosted check](sd-policy-followup-hosted-verification.json) verifies successful deployment of the preceding policy batch at `1ee1b65`.

[Local batch validation](local-material-followup-validation.json) confirms the exact seven-cell North Port diff, 1,327 unchanged surviving local rows, unchanged policy CSV and typed stages, all 1,775 IDs and 1,487 residual guards/questions. A regression against the actual prior North Port review structure preserves its substantive follow-up while excluding search metadata. Nine focused checks pass; maps and expanded ballot data are unchanged.

## Colorado adopted terms clarified

[Three independent adjudications](colorado-term-adjudications.json) support [twelve guarded cells](colorado-term-field-applications.json) across Lochbuie, Loveland and Paonia. [Lochbuie](lochbuie-independent-review.md) now identifies signed Ordinance 2026-720 and its five-year term from effectiveness, with publication and thirty-day timing qualifications. [Loveland](loveland-independent-review.md) now identifies signed Resolution R-48-2026, effective September 15, with its amended twelve-month term and earlier-ending conditions. The coordinator withholds the proposed structured endpoint because current operative effect remains unchecked; its conditional anniversary stays in the narrative. [Paonia](paonia-independent-review.md) now gives the signed municipal copy greater weight for the December 31, 2027 original term, preserving the conflicting newspaper account and later-action hold. Its type becomes `until_date`; current operative endpoint remains blank.

[Source continuity](colorado-term-source-continuity.json) retains seventeen successful capture observations, one blocked discovery observation, the previously retained Paonia PDF and two separate OCR reading aids. One Loveland draft retrieval is byte-identical to the earlier version and supplies no new substantive facts. The Paonia signature/audit appendix was read from the retained scan, not inferred from missing normalized text or cryptographically authenticated. Three whole-record dispositions remain unresolved; status categories and headline totals are unchanged.

[Hosted verification](local-material-hosted-verification.json) confirms six exact files at the preceding `c0f9a95` deployment.

[Colorado batch validation](colorado-term-validation.json) verifies the exact twelve-cell diff, 1,325 unchanged local rows, unchanged policy CSV, stage/adoption-date/endpoint values and scope membership, and all 1,775 active IDs plus 1,487 residual fingerprints/questions. Nine focused checks pass. Map numeric inputs and expanded ballot data are unchanged.

## Historical party and California field gaps resolved

[Six adjudications](historical-party-adjudications.json) combine actual primary evidence with prior accepted material/status reviews. [Maine review](historical-maine-party-review.md) matches three sponsors to the correct historical session, chamber and residence: Sherman/125th Republican, Stanley/128th Democrat and Dill/125th Democrat. [California review](historical-california-party-review.md) confirms the three recorded provision summaries and scope, historical party from dated Senate floor analyses, and full author identity from official member pages. Older analyses supply party evidence only; the retained relevant bill versions supply material provision evidence.

[Guarded accounting](historical-party-disposition-application.json) records six confirmed-unchanged closures and no canonical CSV edits. Current totals are **1,481 unresolved, 100 corrected-resolved and 194 confirmed-unchanged**, across 1,775 active raw IDs. The [state activity classification](california-activity-context.json) is inherited aggregate context; consistency across CA rows is not a new statewide assessment and does not come from an individual bill text. No current-law or successor-law census is claimed.

[Source continuity](historical-party-source-continuity.json) separates twenty-four retained acquisition observations from the five new substantive party sources, preserves exact native body/text readbacks and records anonymous session/form techniques. Initial redirected/unrendered responses and operational failures supply no party evidence. The [preceding deployment check](colorado-term-hosted-verification.json) confirms six hosted files at `d83b417`.

[Historical-party batch validation](historical-party-validation.json) confirms six exact guarded disposition changes, unchanged canonical CSV and scope-registry bytes, reconciled earlier/remaining cohorts, all 1,775 current IDs and 1,481 residual row fingerprints/questions. Nine focused checks pass. Headline classifications, maps, ballot tables and frozen release assets are unchanged.

## Virginia and Wyoming followup applied

[Primary sources and findings](va-wy-followup.md) confirm Thomas’s Democratic affiliation and identify Kevin Campbell, Republican. Two Wyoming sponsor/party cells remove speculation and retain the unresolved bill-listed Pearson attribution. A guarded append-only scope supersession changes Wyoming from include to unresolved: 373 included, 19 excluded, 55 unresolved, zero unreviewed. Virginia remains unresolved. Raw records, legislative stages and disposition totals are unchanged; the outstanding-question index now reflects these narrower gaps.

The [hosted verification](va-wy-hosted-verification.json) confirms six named public artifacts match source `287444e` byte for byte, including the corrected policy CSV, append-only scope registry, scope receipt, summary, release metadata and scope guidance. The two preceding Pages failures were terminal; the successful build serves the reviewed correction. This verifies publication of this increment, not completion of outstanding QA.

## Arizona official final-disposition review applied

[The official index and seven rendered bill histories](arizona-final-review.md) support sixteen guarded edits across seven records and resolve HB 4009’s prior final-action question. Current dispositions are 1,480 unresolved, 101 corrected-resolved and 194 confirmed-unchanged. Six held-in-committee bills and HB 2452’s held-on-reconsideration observation retain unknown terminal categories. All IDs, local rows, scope partitions and ballot data remain unchanged. Earlier dated batch counts above are historical checkpoints.

[Arizona hosted verification](arizona-final-hosted-verification.json) confirms six named served artifacts match `2314e44`, including current policy, scope, metadata and unresolved accounting. [Wyoming Pearson followup](wy-pearson-followup.json) retains the actual handbook and former-member search-form captures without turning an unsubmitted form or an older procedural handbook into identity evidence. No additional canonical or disposition change follows from these captures.

## Alabama session followup applied

[Two status narratives](alabama-session-review.md) add the officially observed April 9 regular-session adjournment and re-observed history counts. The current status sheet is a different session, and the day-30 House PDF is only a first-readings report. These are not terminal evidence for HB403/SB265. Their exact procedural and inherited sponsor/companion/substitute questions remain indexed; 1,480 whole-record dispositions remain unresolved.

## Petersburg first-reading source followup

[Exact event/meeting/item observations](petersburg-followup.json) map the November 2 Assembly event 863 to meeting 851 and Ordinance 2026-24 item 707. Only agenda and packet are currently published; no primary vote/minutes follows from empty/default motion and vote metadata. The first-reading and later-action questions remain unresolved, now with exact retrieval targets. Three successful captures archive with native continuity; no canonical field, stage or disposition changes.

## Foley adopted-file corrections applied

[Four source-backed field corrections](foley-review.md) establish the displayed six-calendar-month term, corporate-limit scope and specified exemptions, while preserving executed-copy/number, actual publication/effectiveness and later-force questions. File 26-0439 is not silently treated as the assigned ordinance number. All headline, ballot and disposition totals remain unchanged.

## Wyoming retained-source followup applied

[Previously captured bill bodies and 2026 rosters](wy-retained-review.md) resolve all nine HB0155 sponsor identities/roster affiliations, qualify HB0325’s source abbreviation and party assertions, and supersede its broad conditional-coverage inclusion with unresolved. Four cells and two append-only scope observations change; no new network request or whole-record closure. Current scope: 372 included, 19 excluded, 56 unresolved.

## Nebraska retained sponsor-source followup applied

[LB1111’s introduced print and retained official history](nebraska-retained-review.md) establish Cavanaugh/McKinney and Spivey’s January 20 addition. Two guarded cells replace an obsolete sponsor-source note and qualify the unverified inherited PRB-minutes assertion. The underlying minutes and provision-transfer comparison remain open; zero new acquisitions and no whole-record closure.

## Nebraska LB613 marked-text assessment applied

[Visual review of six enacted-slip pages](nebraska-lb613-review.md) resolves the reproduced-incentive-versus-amendment uncertainty: municipal disclosure/access changes and a subsection renumbering are distinct from unchanged surrounding data-center investment/hiring terms. One guarded summary cell changes; full sponsor identity and provision-specific effectiveness/current-force questions remain open. No new acquisition, category change or whole-record closure.
