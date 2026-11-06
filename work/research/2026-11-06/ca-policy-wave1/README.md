# California chaptered-policy review — November 6, 2026

Two distributed `gpt-6.1-terra` returns (`ca-state-policy-001` and `ca-state-policy-002`) were reviewed against retained primary histories and chaptered text. Six histories were independently fetched again on November 6; each still lists September 21, 2026 chaptering and Governor approval. A bounded Exa search found the Governor’s September 21 seven-bill announcement. Retrieval through bc-web/pydoll (visible browser, 1,800 ms settle) succeeded and revealed the missing AB 2469 record; its chaptered text was then independently fetched.

| Record | Accepted substantive correction | Chapter |
|---|---|---:|
| AB 1577 | CEC reporting upon energization/substantive change and at least annually; monthly-disaggregated energy data; local permitting energy/sound estimates and specified exclusions | 434 |
| AB 2383 | Transmission/distribution and generation tariff requirements; generation cost-recovery mechanisms of at least ten years; CCA/ESP generation tariffs by 2028 | 435 |
| AB 2469 — new | Local permit conditions covering water supply, use, workforce and applicant-funded water infrastructure; water scarcity plans start January 1, 2028 | 436 |
| AB 2619 | Water-use disclosures to suppliers and local government; annual prior-year reporting on renewals; shortage assessments include data center demand | 437 |
| SB 886 | New/updated CPUC tariffs and rules by 2028; transmission-level provisions for specified new agreements from January 1, 2027; demand response is optional | 438 |
| SB 887 | Categorical CEQA exemption restriction with specified facility exclusions, alongside conditional environmental leadership project/judicial streamlining eligibility | 439 |
| SB 1168 | Requires assessment of rate-structure opportunities, rather than directly establishing the rates described in the old summary | 440 |
| SB 57 | Existing Chapter 647 (2025): assessment is authorized, not mandatory; an assessment completed under the section must be submitted and posted by January 1, 2027; section repeals January 1, 2031 | 647 (2025) |

Six existing records change from passed_one_chamber to enacted. AB 2469 adds one enacted bill. The state-policy tracker increases from 440 to **441 actions**, including **439 bills and two non-bill actions**; enacted bills increase from **84 to 91**. Local totals remain **1,293 instruments / 1,071 classified in force**. Ballot tables are unchanged.

The seven September chaptered laws have ordinary January 1, 2027 effective dates under California Constitution Article IV section 8(c)(1). Their chaptered text has no urgency clause; the rule’s immediate-effect categories were considered separately from delayed implementation clauses. These are bill-level ordinary dates, not claims that a tariff, disclosure process or permit implementation is currently operating. `legal_effect_status` remains unknown for those bills because the current vocabulary lacks enacted-but-not-yet-effective. Later intervening amendments, referendum activity and implementation remain separate review work.

The original client extraction omitted substantial portions of AB 1577, AB 2619 and SB 887. Separately registered complete HTML text derivations restore their headings and operative sections while retaining original bytes and hashes. The coordinator read the relevant operative clauses and final sections; machine integrity and quote checks do not stand in for that substantive judgment. `verification.json` pins evidence versions and exact quote checks. Public source manifests and retained primary text carry acquisition/derivation lineage; raw bodies and provider exchange artifacts remain in the durable private archive.

The baseline contains all 13 prior California rows. Only seven existing corrections plus AB 2469 are applied. Six other worker returns (AB 1095, AB 2170, AB 222, AB 93, SB 1298 and SB 978) remain unpromoted for separate disposition/current-force review; no statewide census or complete California freshness claim is made. Ordinary source observation dates are November 5 for retained text and November 6 for recovered histories and the new sources. Inventory-wide state-page dates retain the November 5 cohort cutoff.

Collection used eight of eight bounded fetches and one of two Exa searches ($0.007 reported search cost); no API extraction or new distributed queue was launched. The original 333-job Terra queue remains terminal. `answers.json`, exact baseline, apply audit and verification receipt make this increment reviewable and idempotent.

Validation: `make data site check` passed with zero errors and 282 data warnings; all 49 documented numbers match. Exact diff review confirms 46 existing-field edits across seven rows plus one new bill, with no local-inventory or expanded-table changes. Replaying the reviewed answers proposes zero field edits and safely skips the already-added bill. `validation.json` pins the completed check log and six fresh history observations.
