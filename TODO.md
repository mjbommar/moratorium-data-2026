# Implementation TODO

Plan: [Research modernization and ballot-measure expansion](docs/research-and-ballot-expansion-plan.md).

Closeout execution order: [November refresh closeout](docs/release-closeout.md). This preserves the full requirement scope and sequences remaining review, final data freeze, copy/consumer reconciliation, publication and deployment verification.

Created: 2026-11-05. Execution began under the user’s subsequent active-goal instruction.
Checked tasks have local evidence; unchecked tasks remain required. No release has been published.
Complete phases in dependency order; retain evidence and unresolved dispositions.

## P0 — Baseline and ownership

- [x] Record Git revisions, dirty state, canonical CSV hashes, counts and generated-artifact baseline.
- [x] Pin the inspected bc-modules revision, package versions and runtime/dependency configuration.
- [x] Confirm dataset ownership and exact consumer paths across public, research, site and integration repositories.
- [x] Establish admitted durable archive and local NVMe database paths; run storage preflight before bulk writes.
- [x] Map 6,645 current legacy manifest entries to native observations or explicit path gaps; import 3,202 verified-body versions after private CAS link recovery, retaining 3,443 listed-path gaps (initial mapping and subsequent migration/recovery deltas). Of those gaps, 119 are failed acquisitions without a recorded body hash. Other private stores remain incompletely searched; this does not close the full P3 archive gate.
- [x] Record the November 5 working-cohort cutoff, record-specific source/legal-force limits and historical 348-extraction/211-jurisdiction pre-April-28 cohort in README, methodology and known gaps; no inventory-wide legal-force renewal is claimed.

Exit: reproducible baseline manifest with unrelated work preserved.

## P1 — Data contracts

- [x] Define schemas and fixtures for jurisdictions, elections, ballot measures and provisions.
- [x] Define versioned result observations, vote denominators, passage rules and certification states.
- [x] Define non-moratorium local restrictions without widening the legacy inventory denominator.
- [x] Define typed measure–instrument links, instrument events, claims and scoped review decisions.
- [x] Define and test explicit UUID allocation, pinned observation aliases, collision checks and append-only merge/split lineage (`docs/expanded-identity-registry.md`). Domain-fact import remains separate.
- [x] Preserve existing moratorium/project/state-action IDs and document tagged references.
- [x] Separate lifecycle, result, certification, bindingness, mechanism and yes-vote direction.
- [x] Define date bounds, precision, local timestamps, retroactivity, calendar durations and end conditions.
- [x] Define threshold units, operators, aggregation, exemptions and measurement basis.
- [x] Define search/coverage provenance and independently tracked stage-completeness states.
- [ ] Decide exact authoritative JSONL paths and documented public CSV projections.
- [ ] Review schema examples against all pilot cases before implementing import/apply logic.

Exit: ballot cases fit without conflating votes, legal force or legacy counts.

## P2 — Search and acquisition adapters

- [ ] Build a closed jurisdiction/official-source registry with aliases and election-portal hosts.
- [ ] Build sparse bc-spec worklists for inventory refresh, election census and gap discovery.
- [ ] Add deterministic plan preview, seeded sampling and call/cost estimates.
- [ ] Configure provider-specific Exa/Google query variants through `Searcher.search_many`.
- [ ] Retain rank fusion provenance, original sightings, response hashes and backend errors.
- [ ] Add Google News RSS/GDELT and bounded paid-news escalation with index-window decline handling.
- [ ] Add intent-specific query expansion, primary-host discovery, historical time walks and undated-source recovery.
- [ ] Add exact-identifier/reference chasing, feedback queries and bounded relaxation.
- [ ] Calibrate ResearchSearch tiers without excluding primary sources or reverse-polarity measures.
- [ ] Reserve bounded deep_research/source-agent use for difficult cases; retain skipped stages and conversations.
- [ ] Configure current SerpAPI pricing and whole-run/per-stage budgets, including unpriced-call policy.
- [ ] Pin model roles/settings and cache fingerprints; redact secrets from retained responses.
- [x] Implement HTTP/browser escalation and bounded PDF/office-document collection.
- [ ] Configure source/provider pacing, Retry-After, explicit retries and verified routing as applicable.
- [ ] Make partial backend failure and zero-result cells distinguishable in coverage reports.

Exit: read-only dry-run and bounded acquisition produce auditable plans and attempts.

## P3 — Evidence, review and deterministic promotion

- [ ] Bridge legacy archives to bc-store without losing original hashes, URLs or access classification.
- [ ] Parse payloads and preserve PDF pages/OCR provenance; detect empty/challenge/login payloads.
- [ ] Adapt bc-evidence full-document extraction to electoral/legal candidate schemas.
- [x] Inspect pinned bc-evidence extraction behavior and pilot readiness; verify missing cell associations and failed-document retry exclusion in an isolated database (`work/research/2026-11-05/extraction-readiness/`). This is an integration audit, not completed extraction.
- [ ] Record all chunk coverage, extraction ceilings, failures and resumable status.
- [x] Add and test a resumable wrapper around actual bc-evidence `extract_document()` with pinned contexts, per-chunk coverage, durable call reservations and validated caches (`scripts/extract_document_resumable.py`). Dollar controls and a real pilot are recorded below; domain-typed extraction remains open.
- [x] Add durable dollar reservations/settlement with persistent stops for unpriced or over-reservation results; run a real one-page Peru proposal extraction and cached replay (five located claims, one backend call; `work/research/2026-11-05/full-document-peru-pilot/`). Domain-typed extraction and broader cohorts remain open.
- [x] Implement field-specific electoral/proposal extraction transport and review-only candidate validation; calibrate two actual Peru model passes, reject invalid field shapes and withhold inferred voter polarity without ballot wording (`work/research/2026-11-05/domain-peru-pilot/`). Broader document/result cohorts, restriction/event adapters and substantive acceptance remain open.
- [ ] Preserve exact quotes, offsets, date/value support and raw-versus-text hashes.
- [ ] Build review packets for identity, wording, vote totals, polarity, bindingness and legal effect separately.
- [ ] Group syndication/common upstream result feeds before assessing independent support.
- [ ] Add contradiction/support alerts without using model/NLI confidence as legal acceptance.
- [ ] Require reviewed candidates for instrument/entity/event merges; protect distinct acts and questions.
- [ ] Extend decision schemas with record fingerprints, scope, supersession and evidence claim references.
- [x] Implement explicit-file, dry-run, conflict-safe, atomic and idempotent ballot promotion; exercise the first real Eliot batch and exact replay (`scripts/expanded_promotion.py`, `work/research/2026-11-05/eliot-promotion/`).
- [x] Exercise a second real ballot cohort and explicit result supersession, preserving unknown totals and separating reported approval from legal force; generate a checked public results view (Sabattus/Eliot batch).
- [x] Promote Canterbury’s earlier March Article 4 question, proposed permanent prohibition and town-posted counts, preserving unresolved certification, outcome and legal force.
- [x] Review Nottingham’s September ballot counts and proposed clauses against official sources; distinguish Planning Board signatures from enactment and preserve unresolved certification (`work/research/2026-11-05/nottingham-ballot-review/`).
- [x] Promote Nottingham’s reviewed September question, proposed clauses and marked-ballot counts with unresolved certification, outcome and legal force (`work/research/2026-11-05/nottingham-promotion/`).
- [x] Reconcile all 56 frozen ballot groups with four scoped canonical publications; retain 52 pending groups and explicit pinned correspondences (`ballot-census-review/canonical-projection-status.json`).
- [x] Review Wiscasset’s unofficial counts and voter-guide terms; reject the broader election total as a question-specific denominator (`work/research/2026-11-05/wiscasset-ballot-review/`).
- [x] Recover Wiscasset’s official sample ballot, signed warrant and final-text ordinance with Exa/bc-web; reacquire results using pydoll and verify retained evidence (`wiscasset-ballot-review/recovery-review.json`).
- [x] Publish Wiscasset’s reviewed question, proposed clauses and unofficial counts; add an enactment duration anchor, retain unknown denominators and reconcile five published / 51 pending candidate groups.
- [x] Review North Berwick’s certified Question 2 counts, ballot placement and proposed permanent prohibition; preserve aggregate-area/impervious-surface threshold and accessory exclusion (`north-berwick-ballot-review/`).
- [x] Publish North Berwick’s reviewed Question 2, proposed area-qualified prohibition and certified counts; reconcile six published / 50 pending ballot groups (`north-berwick-promotion/`).
- [x] Review Wells Article 5 certified counts and retroactive terms; distinguish the warrant’s 100,000-square-foot proposal from the separate blank-threshold agenda draft (`wells-ballot-review/`).
- [x] Publish Wells Article 5 submitted terms and certified yes/no/blank counts; retain June16duration anchor and reconcile seven published / 49 pending ballot groups (`wells-promotion/`).
- [x] Recover Peru’s official native-image Article 2 results through bc-web/SerpAPI; verify 578yes/182no, separate 774 total voters, and review proposed 180-day/effectiveness terms (`peru-ballot-review/`).
- [x] Support original native-PNG visual evidence, rejecting transforms/dimension/body drift; exercise the real Peru results image through the evidence audit (`peru-native-image-review/`).
- [x] Publish Peru’s official Article 2 counts/proposed provisions using native-PNG evidence; preserve unknown ballot wording/polarity and reconcile eight published / 48 pending groups (`peru-promotion/`).
- [x] Review Brownfield’s official tally, warrant and unusual draft power limits; distinguish Freedom’s preamble/hearing study period from its missing operative end date (`maine-remaining-ballot-review/`).
- [x] Recover Freedom’s source-qualified Article 3 tally photograph, preserving 24 VOIDS and 470 source total; correct tracker-count versus news-approval provenance (`maine-remaining-ballot-review/freedom-recovery-review.json`).
- [x] Add evidence-scoped source vote categories/totals without automatic mapping or denominator inference; exercise Freedom VOIDS24/circled470 and separate public summary rendering.
- [x] Support strict original-JPEG visual evidence with EXIF orientation and stored dimensions; exercise Brownfield/Freedom counts and Freedom source categories through the evidence audit (`maine-native-jpeg-review/`).
- [x] Publish Brownfield’s Article 1 question, proposed terms and original-JPEG tally, retaining its scoped source total and unresolved power-clause interpretation; reconcile nine published / 47 pending groups (`brownfield-promotion/`).
- [x] Publish Freedom’s source-qualified Article 3/photo observations and draft terms, keeping VOIDS/circled total separate and account/certification/legal gaps explicit; reconcile ten published / 46 pending groups (`freedom-promotion/`).
- [x] Review Clarksville’s two financing-referendum calls and register scoped OCR; preserve the conditional December date and reject an inaccessible article’s URL slug as date evidence (`clarksville-ballot-review/`).
- [x] Review California DB/NDC primary evidence; refresh Alhambra counts with pydoll, recover council adoption/referral minutes with Exa/bc-web, and distinguish Monterey Park county/clerk/council/ordinance dates (`california-ballot-review/`). Canonical publication is recorded below; current legal histories remain open.
- [x] Publish Alhambra DB with explicit old/new county-result supersession and Monterey Park NDC with certified counts/provisions; preserve distinct certification/execution phases and reconcile twelve scoped publications / 44 pending groups (`california-promotion/`). No legacy moratorium count changes or current legal-force acceptance.
- [x] Retain hash-verified original extraction versions alongside later registered OCR in the evidence index; test historical-publication survival, untracked originals and corrupt derivations (`tests/test_refresh_evidence_audit.py`).
- [x] Review four Madison County township advisory questions against the official sheet and fresh linked CSV export; preserve affirmative permission polarity, distinct township identities and uncertified counts; repair two worker ZIP-member derivation lineages without changing payloads (`illinois-township-ballot-review/`). Canonical publication is recorded below.
- [x] Publish the four Illinois township advisory measures with explicit prior/current source supersession; show bindingness and yes-vote direction in public results and reconcile sixteen scoped publications / 40 pending frozen groups (`illinois-township-promotion/`). Additional sector leads and legal review remain separate.
- [x] Publish Bloomington township’s advisory wording and source-qualified counts with primary township identity, unresolved placement/certification/legal effect, and 17 published / 39 pending frozen groups (`work/research/2026-11-06/bloomington-promotion/README.md`).
- [x] Recover Bloomington's official advisory specimen and Joliet Township's official CSV; distinguish specimen certification from result certification, city actor from township electorate, and source areas from precincts (`illinois-remaining-ballot-review/`). Preserve Joliet's five-ballot accounting difference and the failed wording refresh.
- [x] Recover Bloomington's primary special-town agenda and government portal naming; distinguish township electorate/body terms from city actor and election-board administration, without treating an agenda as an adopted placement motion (`bloomington-township-identity-review/`).
- [ ] Obtain Bloomington's original township placement/qualification disposition and boundary reference; obtain Joliet's original referral/advisory authority and clarify its source accounting before completing those publication reviews (`illinois-remaining-ballot-review/`).
- [ ] Verify electorate/qualification and policy direction for the additional Madison-report wind/solar zoning-control question; reconcile it beyond the frozen v3 seed set without treating it as a development ban or silently changing census counts (`illinois-township-ballot-review/additional-leads.json`).
- [ ] Complete broader promotion/recovery calibration and the remaining ballot identity/fact reviews; the initial Eliot batch does not close P3.
- [ ] Extend evidence archive/publication gates to new records and source payload types.
- [ ] Add behavioral regression checks from plan section 11 (initial subset includes offline publication/receipt drift, historical identity baselines and portable-pointer checks; full gate coverage pending).

Exit: every accepted pilot assertion traces to reviewed evidence; unresolved cases stay unresolved.

## P4 — Pilot and calibration gate

- [ ] Freeze a source-backed pilot and holdout set before prompt tuning.
- [ ] Review Peru, Wells, Bloomington, Piqua, Grove City, Harwood, Wilmington and El Dorado.
- [ ] Include earlier/December elections, failed qualification, changed results, mixed polarity and portal failure cases.
- [ ] Include a council-only adoption/extension and predecessor-pause/replacement-ban history.
- [ ] Measure discovery recall, false exclusions, primary-source recovery and identity/quote/date/unit accuracy.
- [ ] Report reviewer disagreement, unresolved facts, extraction completeness and spend per review-ready record.
- [ ] Set and assess documented quality thresholds; resolve silent high-impact errors before scaling.
- [ ] Present exact batch scope, call count, model/effort and budget for authorization before bulk execution.

Exit: accepted pilot report and separately authorized bounded collection scope.

## P5 — Reviewed collection and migration

- [ ] Freeze the full-refresh scope matrix, execution-time cutoff and required sibling/consumer dispositions (plan section 9.1).
- [x] Add a hashed per-record collection/edit accounting snapshot for both canonical inventories, keeping unresolved worker returns, queued jobs, pilot exclusions and apply-ledger changes separate (`scripts/build_refresh_accounting.py`, `work/audit/refresh-record-accounting-2026-11-05.md`). This is not the completed source/current-force freshness funnel.
- [x] Finish and mechanically audit all 333 distributed `gpt-6.1-terra` queue jobs, with zero running/queued jobs and hashed terminal execution receipt (`work/audit/distributed-queue-terminal-2026-11-05.json`). This records returns for 1,283 assigned local and 434 assigned state-policy IDs; it does not complete substantive review or legal-force verification.
- [ ] Re-research every existing local inventory ID and publish confirmed/changed/unresolved/not-attempted freshness accounting.
- [ ] Re-research every state-policy ID and discover new state actions across all 50 states and existing sectors.
- [x] Separate the New Jersey S3379/A4096 and A4696 identities and apply five bounded corrections (`work/research/2026-11-06/nj-policy-wave1/README.md`); signed chapter 75/effective date, report-triggered expiration, implementation and remaining dispositions remain open.
- [x] Review all three assigned Delaware records against retained and freshly recovered official sources; confirm two enactments/current codification and bound the failed SB 205 disposition (`work/research/2026-11-06/de-policy-wave1/README.md`). Rulemaking/tariff implementation and SB 205 amendment details remain open.
- [x] Review remaining California history returns and correct SB 978 using deletion-aware amended text (`work/research/2026-11-06/ca-policy-wave2/README.md`); AB 2170, AB 222 and SB 978 ultimate dispositions and full current-force review remain open.
- [x] Review six California enactments and SB 57’s final wording, and add missing AB 2469 using Exa, pydoll and chaptered text (`work/research/2026-11-06/ca-policy-wave1/README.md`); six other assigned California rows and current implementation remain open.
- [x] Apply three bounded Missouri policy corrections with independently recovered primary sources (`work/research/2026-11-06/mo-policy-wave1/README.md`); all seven assigned disposition/current-force reviews remain open.
- [ ] Search new local instruments across all 50 states/sectors and document actual jurisdiction/time coverage.
- [x] Receive and mechanically audit all 50 state-discovery returns: five sector labels and schema-valid answers per state, 185 local proposals pending substantive review (`work/audit/state-discovery-returns-2026-11-05.json`). This does not close the preceding coverage task.
- [ ] Review site-operator search scope diagnostics and repair deficient official-record searches before accepting any negative coverage finding (`work/audit/search-scope-diagnostics-2026-11-05.json`).
- [ ] Define and budget the project/disclosure refresh scope separately; retain dated snapshots where full recollection is outside scope.
- [ ] Seed candidate lists from Ballotpedia, Duane Morris, Redbud and independently found official sources.
- [x] Compile all 22 terminal ballot jobs into a candidate review snapshot: 58 observations, 56 logical seed groups, pinned inputs and explicit Illinois duplicate identities (`work/research/2026-11-05/ballot-census-review/`). Evidence, census completeness and legal promotion remain open.
- [ ] Reconcile 41/44/45 November tallies by record-level set differences and explicit inclusion rules.
- [ ] Acquire ballot/warrant text, qualification/referral records and official return/certification evidence.
- [x] Review Oregon, Pataskala, Perry village and Piqua against nine primary versions, recover three printed questions and official Oregon totals, and retain precise Piqua ballot/accounting provenance (`work/research/2026-11-06/ohio-ballot-wave3-review/README.md`). Canonical publication, Piqua full wording, Perry full ordinance and all current-force histories remain open.
- [x] Prepare four Ohio wave-3 canonical candidates and pass full publication preflight with 38 scoped claims and preservation of every prior row (`work/research/2026-11-06/ohio-wave3-promotion/README.md`). Canonical publication and census correspondence are applied: 33 published / 23 pending. Final canvasses, operative histories and remaining refresh/release work remain open.
- [x] Independently review Sunbury official printed charter question and Sunbury/Upper Sandusky unofficial returns, including source-labelled totals and Upper Sandusky under/overvotes (`work/research/2026-11-06/ohio-ballot-wave4-review/README.md`). Publication, Upper Sandusky primary wording/placement, Trenton review, Sprigg full plan and operative histories remain open.
- [x] Use two Exa searches and six bounded bc-web fetches (including pydoll) to review Trenton listed Issue17/result and clarify Upper Sandusky petition origin versus council placement (`work/research/2026-11-06/ohio-wave4-primary-recovery/README.md`). Failed portal/404 and unrelated notice excluded; full ballot texts, underlying qualification instruments and all operative histories remain open.
- [x] Publish Sunbury, Upper Sandusky and Trenton scoped ballot/result records, preserving unknown certification/polarity/full text where unreviewed; reconcile36 published/20 pending census groups (`work/research/2026-11-06/ohio-wave4-promotion/README.md`). All missing primary texts, final canvasses and operative histories remain open.
- [x] Review Urbana return, all four Wilmington primary questions/returns and separate excluded Chapter1161 initiative court history; retain Urbana secondary exception and pre-election code cutoff (`work/research/2026-11-06/ohio-ballot-wave5-review/README.md`). Publication, infrastructure association, primary Urbana text, certification, underlying instruments and operative histories remain open.
- [x] Review Wilmington source-qualified Ardent/AWS context and resolve news/ballot parcel-description conflict using official wording (`work/research/2026-11-06/wilmington-association-review/README.md`). Five-case publication and census correspondence are applied (41 published/15 pending); project identities/coverage, original ordinances and legal-force histories remain open.
- [x] Publish Urbana contest and four distinct Wilmington referendums with shared municipal/election identities, explicit referendum polarity and source-qualified infrastructure context (`work/research/2026-11-06/ohio-wave5-promotion/README.md`). Excluded initiative lifecycle publication, missing primary texts, final canvasses, project links and operative histories remain open.
- [x] Review three Wisconsin candidates against seven source versions/17 scoped claims; reconcile Wrightstown county slices with pydoll-recovered Outagamie summary while preserving mixed certification/vintages and proposal threshold ambiguities (`work/research/2026-11-06/wisconsin-ballot-primary-review/README.md`). Publication, original final ballots/adopted texts, full village certification and operative histories remain open.
- [x] OCR the28-page Outagamie county-contest canvass and inspect its opening/certificate pages; retain August18 document certification without assigning it to Wrightstown referendum (`work/research/2026-11-06/wisconsin-canvass-scope-followup/README.md`). Named municipal certification, full final ballot and operative histories remain open.
- [x] Add optional explicit result reporting_scope, visible summary labels and supersession guards preventing one county part from replacing another/full electorate;143tests and full build pass (`docs/expanded-data-contracts.md`, `work/research/2026-11-06/reporting-scope-validation.json`). Wisconsin partial-result publication and complete certification remain open.
- [x] Review Janesville advocacy-source and Port Washington WPR development context without importing unverified moratoria/current effects or flattened threshold wording (`work/research/2026-11-06/wisconsin-ballot-context/README.md`). Original final ballots, adopted laws and legal histories remain open.
- [x] Publish three Wisconsin measures/four scoped observations with separate Wrightstown county portions and exact source totals; reconcile44published/12pending groups (`work/research/2026-11-06/wisconsin-ballot-promotion/README.md`). Final ballots/adopted texts, complete village certification, litigation and legal-force histories remain open.
- [x] Review Mandan future election/approved summary and normative petition, Harwood full proposed ArticleX and unofficial result:19claims/five source versions (`work/research/2026-11-06/north-dakota-ballot-primary-review/README.md`). Future-measure publication, compound-threshold normalization, final ballots/qualification/canvasses and operative histories remain open.
- [x] Publish Mandan scheduled measure without a result and Harwood unofficial charter result, preserving compound trigger groups and unknown legal effects;46published/10pending census groups (`work/research/2026-11-06/north-dakota-ballot-promotion/README.md`). Final ballots/qualification/canvasses, complete normalization and operative histories remain open.
- [x] Publish Downe advisory ballot with secondary 62/425 result and separately scoped October19 ordinance history; official canvass and operative ordinance text/effect remain open (`work/research/2026-11-06/downe-ballot-promotion/README.md`).
- [x] Publish BoulderCityQuestion1with official wording/digest and unofficial2064/4947result; transfer-area approval gate, council discretion and futureNovember13canvass remain distinct from legal force (`work/research/2026-11-06/nevada-ballot-promotion/README.md`). Independent charter/current force and certification remain open.
- [x] Publish EdgewaterAmendment4withcountywordingandunofficial7884/2328DOM/JSONresult; proposed charter mechanism and certification gate remain separate from actual current legal force (`work/research/2026-11-06/florida-ballot-promotion/README.md`). Certification, final charter and operative history remain open.
- [x] Independently verify Perry village (Lake County OH) against the official village site and Census2025GEOID3961882; correct coordinates only and add declared override (`perry-geography-review/`). No applicability inference.
- [x] Resolve the erroneous Sprigg worker count conflict by direct source review (330 for / 297 against / total627), and retain Monroe/Sprigg plan-recovery gaps and unverified notice reproductions (`work/research/2026-11-06/adams-zoning-followup/README.md`). Full plans and operative histories remain open.
- [x] Publish Grove City, Hubbard city and Monroeville advisory ballot/result records with metric-specific aggregation limits and source-count provenance; reconcile 29 published / 27 pending groups (`work/research/2026-11-06/ohio-wave2-promotion/README.md`). Monroe plan classification and all final canvass/operative histories remain open.
- [x] Review the next four Ohio candidates against eleven primary source versions, including all thirteen Grove City proposal pages, explicit 10% boundary differences, and unofficial county returns (`work/research/2026-11-06/ohio-ballot-wave2-review/README.md`). Three scoped publications are recorded above; Monroe plan/data-center scope, exact remaining ballots and current force remain open.
- [x] Publish four Ohio municipal ballot/result records with official Ashville term-summary wording, Conneaut Article XVI/25 MW definition, and explicit Defiance/Granville wording/placement limits; reconcile 26 published / 30 pending frozen groups (`work/research/2026-11-06/ohio-wave1-promotion/README.md`). All four results remain unofficial; adopted text, certification and current force remain open.
- [x] Publish four scoped Kansas proposal/count records with shared Emporia city/election, exact source totals and alternative data-center threshold clauses; reconcile 22 published / 34 pending frozen groups (`work/research/2026-11-06/kansas-promotion/README.md`). Ottawa primary identity, current court/effect histories and certification remain open.
- [x] Review five Kansas measure candidates against nine primary source versions, including El Dorado’s unsigned full proposal, distinct Emporia court/remedy clauses, Americus mixed-sector wording and fresh unofficial county counts (`work/research/2026-11-06/kansas-ballot-review/README.md`). Current judicial/effect review and Ottawa primary wording remain open; four scoped canonical publications are recorded above.
- [x] Publish Joliet Township’s advisory permission question, signed referral evidence and exact source counts with a public accounting-discrepancy note; reconcile 18 published / 38 pending frozen groups (`work/research/2026-11-06/joliet-promotion/README.md`). Certification, result reconciliation and legal implementation remain open.
- [x] Recover and visually review Joliet Township’s signed Resolution 2026-08 and county-clerk advisory notice; preserve two-stage referral terms and separate resolution certification from election certification (`work/research/2026-11-06/joliet-qualification-review/README.md`). Result reconciliation and legal implementation remain open; scoped canonical publication is recorded above.
- [ ] Keep unofficial, certified, recounted and amended results as distinct observations.
- [ ] Check exact wording, passage rules and reverse/mixed polarity for every included measure.
- [x] Review Eliot Question 5 against the official sample ballot, signed warrant and certified proposed text; pin five visual source passages and classify the enactment question, while leaving its effective date and legal-force interval unresolved (`work/research/2026-11-05/ballot-census-review/eliot-review.md`).
- [ ] Verify post-vote legal implementation, effective/applicability dates, exemptions and challenges.
- [ ] Match prior pending instruments before creating new moratorium rows.
- [x] Add Edgewater’s proposed charter restriction and accepted ballot `proposes` relationship, with unknown legal status/dates, preserved prior records and public relationship view (`edgewater-restriction-migration/`); full restriction/event/predecessor migration remains open.
- [ ] Record bans and other restrictions separately, with explicit predecessor/replacement links.
- [ ] Preserve failed qualification, withdrawn measures, unresolved cases and bounded negative searches.
- [ ] Reconcile earlier 2026 measures and stage upcoming December measures separately from November totals.
- [ ] Refresh council-adopted moratoria and expiry/extension worklists alongside election work.
- [ ] Resolve Elmwood MI original February ordinance versus June Resolution 2026.06.17.A identities/terms; obtain Frenchtown original Ordinance 300-19 and extension anchor (reviewed-michigan-b).
- [ ] Backfill jurisdiction/source links and document legacy calendar-duration compatibility.
- [ ] Reconcile Leominster petitions 02-27/03-27 into distinct instrument identities with preserved legacy lineage, and resolve the New Orleans January motion/interim-ordinance relationship (`reviewed-louisiana-massachusetts/review.json`).
- [ ] Produce row-level explanations for every change to legacy summary counts.

Exit: every seed has a documented disposition; evidence gaps are visible rather than silently omitted.

- [x] Review Alaska discovery proposals against official referral/first-reading records and six PDF pages; add two pending instruments with no operative dates, preserve all 1,293 prior records and verify replay (`alaska-discovery-review/`). The initial ledger retained 183 unreviewed proposals; subsequent coverage and dispositions are recorded below.
- [x] Complete disjoint distributed `gpt-6.1-terra` review-return coverage for all 183 remaining discovery candidates with independent input/body/text/schema/span checks (`discovery-distributed-review/`). Two initial partial returns remain recorded; 14 smaller assignments cover their missing keys. Worker recommendations do not close coordinator substantive review.
- [x] Add Braintree and Methuen as pending proposals after four-page primary-source review; recover Sun Prairie's omitted city-announcement DOM section and add its source-stage adoption classification. Preserve all 1,295 prior rows and unknown operative ends; build/check and replay pass (`massachusetts-discovery-review/`, `sun-prairie-discovery-review/`). The ledger then retained 179 candidates; subsequent dispositions are recorded below.
- [x] Review eight coordinator cases, retaining six with specific evidence gaps and adding two distinct historical Kent instruments after exact code-reference/application-script chasing and six-page PDF review. Preserve wind adoption-year conflict, retroactivity and the separate unsigned 22-07 source; all 1,298 prior rows remain unchanged (`discovery-coordinator-wave1/`, `kent-instrument-review/`). 167 candidates await coordinator processing; reviewed gaps also remain unresolved.
- [x] Restore 256 absent, untracked raw-body references as ignored exact-hash links to existing private CAS bytes; preserve every manifest and publication flag, and verify idempotent replay (`work/audit/source-body-link-recovery-2026-11-06/`).

## P6 — Public release and sibling handoff

Completed closure increments (the broader gates below remain open):

- [x] Record the book's historical full/Essential/audio edition boundary and explicit unresolved claim-review queue; verify 140 source/PDF artifacts unchanged (`work/audit/book-edition-disposition-2026-11-06.json`). Delivered and remote-verified as book commit `f3509d9`, preserving all 241 production-tree entries from its newer remote parent.

- [x] Verify Server Country Amplify job 43 BUILD/DEPLOY/VERIFY success for `195dd66` and the served historical-paper/working-data notices (`work/audit/servercountry-deployment-2026-11-06.json`). Fight a Data Center hosting verification remains open.

- [x] Restore the public candidate into a clean directory and verify all 25 retained generations (`work/audit/restore-and-replay-validation-2026-11-06.json`); current code passes 149 tests.
- [x] Verify deployed working landing page, canonical CSVs and ballot summary bytes, plus pydoll-rendered totals (`work/audit/pages-built-observation-2026-11-06.json`, `pages-browser-verification-2026-11-06.json`).
- [x] Create an unpublished GitHub draft candidate and verify all downloaded asset bytes and 420 archive members (`work/audit/draft-release-rc1-2026-11-06.json`); final publication/tag remains open.
- [x] Add deterministic ballot due-work rules and operator recovery/restore guidance (`scripts/build_ballot_due_work.py`, `docs/refresh-operations.md`); conditional caching and an advisory adaptive planner are implemented below; task resolution remains open.

- [x] Validate Elmwood four-field primary-source correction and generated Michigan page (`work/research/2026-11-06/elmwood-instrument-review/validation.json`).
- [x] Publish explicit dispositions for all seven unresolved frozen ballot groups (`work/audit/ballot-release-dispositions-2026-11-06.json`).
- [x] Reconcile README, download page, current changelog and landing generator with working counts, record-specific force limits and historical paper/chart scope.
- [x] Update FAQ/methodology to distinguish original collection cohorts, November acquisition/review and unpublished release state.
- [x] Deliver additive November public inputs to integration (`datacenter-data-integration` commit `5592a569`); downstream joins/packets remain unrefreshed.
- [x] Build a deterministic 420-member public data candidate twice with matching hashes (`work/audit/release-candidate-2026-11-06/validation.json`); final-revision build and remote publication remain open.

- [x] Capture initial tracked-text surface catalogue across seven current checkouts with hashes and match locations (`work/audit/release-surfaces-2026-11-06.md`); relevance, manual claim review, binary/rendered outputs and final consumer dispositions remain open.
- [ ] Inventory every affected current prose/copy/summary surface using the matrix in plan section 9.2; assign source, owner and disposition.
- [ ] Generate additive ballot/result/restriction/link exports and expanded codebook/schema documentation.
- [ ] Update state pages, site views, maps/GeoJSON and tables with separate counts and denominators.
- [ ] Show bindingness, certification, observation cutoff and legal-status caveats in public views.
- [ ] Keep advisory votes and permanent bans out of in-force moratorium totals.
- [ ] Update README, methodology, FAQ, known gaps, changelog and release/citation metadata as applicable.
- [ ] Update substantive narrative, rankings, percentages, completeness claims, examples, diagrams, captions, metadata and release labels, beyond replacing headline digits.
- [ ] Sync the paper mirror and rebuild revised manuscript/PDF, or conspicuously preserve the historical edition with no false alignment claim.
- [ ] Reconcile affected sibling sites, manuscripts, integration memos and collaborator packets; record any historical or blocked disposition.
- [ ] Extend copy/number audit coverage beyond the existing checker and inspect rendered landing/state pages and charts.
- [ ] Export stable IDs and reviewed relationships to datacenter-data-integration without changing project ownership.
- [ ] Review any RDF adapter against the integration repository's existing temporal/assertion model.
- [ ] Label proximity exposure separately from reviewed legal applicability in analytical outputs.
- [ ] Run compatibility, arithmetic, referential-integrity, conflict/idempotence and public/private-content checks.
- [ ] Verify clean restore/replay, deterministic exports and manifest hashes; document environmental limits.
- [ ] Inspect actual remote refs, tags, GitHub releases and asset conventions; reconcile stale release/version claims.
- [ ] Choose the release version, prepare final title/body/change ledger and update CITATION metadata without inventing a DOI.
- [ ] Prepare and validate an explicit public asset/checksum manifest, including data, schemas, summaries, freshness/gaps and paper disposition.
- [ ] Commit only owned changes and prepare the exact tag/commit and release payload; publish under applicable authorization.
- [ ] Push/verify the remote commit and immutable tag, publish the GitHub Release and upload all manifested assets.
- [ ] Download each published release asset and verify checksum, size, parseability and expected contents.
- [ ] Verify hosted site deployment, current copy, version/totals/cutoffs, paper edition and download links separately from GitHub release creation.
- [ ] Verify required sibling remote/deployment states and document any remaining blockers.
- [ ] Record the public release URL, tag/commit, asset hashes, deployment and validation receipt; retain rollback inputs and unresolved queues.

Exit: fresh, reproducible release with reconciled data/prose, a verified published GitHub Release and assets, required deployed updates, and explicit freshness limits. Local preparation alone does not close P6.

## P7 — Maintenance

- [x] Exercise bc-web conditional HTTP caching with an actual 200/304 round trip, preserved body time and immutable archive tests (`conditional-cache-pilot/`); native adaptive proposals are implemented below, with inventory-wide calibration still open.

- [ ] Implement due-work rules for qualification, elections, certification/recounts, implementation and expiry.
- [x] Add opt-in conditional HTTP caching and an offline native bc-web adaptive revisit planner, preserving prior observations and cached-body limitations; actual cache pilot and planner tests retained. Inventory-wide calibration and task resolution remain open.
- [ ] Exercise an end-to-end correction and refresh cycle manually.
- [ ] Track source failures, backend contribution, coverage gaps, freshness and review backlog.
- [ ] Document operator recovery, storage restore, interruption and budget-stop procedures.
- [ ] Create schedules only if explicitly requested; record cutoff, scope and budget for each.

Exit: repeatable refresh with visible freshness, costs, failures and unresolved work.

- [x] Independently review four California HTML-backed discovery candidates; retain action-stage/date conflicts and distinct wind/BESS/data-center identities without canonical promotion (`work/research/2026-11-06/california-discovery-review/`). The discovery ledger has 167 unreviewed candidates and ten reviewed withheld cases.

- [x] Add Brighton as city-reported approved and Chicago as source-stage pending from complete official announcements; preserve all 1,300 prior rows, unknown dates/coordinates and calendar terms. Archive two exact retained versions and verify native store readback (`work/research/2026-11-06/brighton-chicago-discovery-review/`). Current discovery ledger: 165 unreviewed.

- [x] Visually review all twelve pages of six Iowa PDFs; add two distinct historical Sac/Sioux records with explicit or calendar-derived recorded endpoints, preserve all 1,302 existing rows, and hold Cerro Gordo execution/publication, Grundy current-force and Jackson extension-chain gaps (`work/research/2026-11-06/iowa-discovery-review/`). Discovery ledger: 160 unreviewed candidates.

- [x] Resolve Fulton full-board extension vote with actual Exa and pydoll acquisition; visually review Tilton minutes pages 1/7 and reject unsupported wind coverage/six-month wording. Retain Edgar original-instrument gap after a bounded SerpAPI search (`work/research/2026-11-06/illinois-action-review/`). No canonical changes; 157 candidates remain unreviewed and sixteen reviewed cases remain withheld.

- [x] Review five NM/MT/OR candidate histories, three PDF pages and four complete HTML texts. Add Silver City’s historical solar instrument with explicit repeal but unknown original event endpoint; preserve all 1,304 prior rows and retain four distinct proposal/final-text gaps (`work/research/2026-11-06/southwest-northwest-discovery-review/`). Discovery ledger: 152 unreviewed and twenty reviewed withheld cases.

- [x] Independently review Millwood/Winlock complete notices and all three pages of the Chelan PUD draft; preserve planned future extension versus adopted action, published summary versus full ordinance, and electric-service versus city land-use identities (`work/research/2026-11-06/washington-discovery-review/`). No canonical changes; 149 candidates remain unreviewed and twenty-three reviewed cases remain withheld.

- [x] Review four Tennessee discoveries; add Orlinda from two-page visual review, preserving the original page-1 extraction gap, calendar term and all 1,305 prior rows. Hold Moore/Hardeman primary histories and Shelby first-reading final action separately (`work/research/2026-11-06/tennessee-discovery-review/`). Ledger: 145 unreviewed, twenty-six reviewed withheld cases.

- [x] Review two Texas discoveries against five original versions, ten PDF pages and two complete reports. Preserve Van Zandt signed adoption separately from enforceability and Delta’s opinion request; retain Tom Green Precinct 4 unsigned/tabled stage (`work/research/2026-11-06/texas-discovery-review/`). No canonical changes; 143 unreviewed and twenty-eight reviewed withheld cases remain.

- [x] Review all six RI discovery candidates against five complete retained HTML texts and two Portsmouth PDF pages; preserve failed extension, public-notice anchor, LLM recap limits, municipality/sector distinctions and shared newspaper lineage (`work/research/2026-11-06/rhode-island-discovery-review/`). No canonical changes; 137 unreviewed and thirty-four reviewed withheld cases remain.

- [x] Review five Idaho candidates; inspect Gooding minutes pages 1–2, all three Blaine draft pages and three complete reports. Add Blaine source-stage pending with unknown term; distinguish its 182-day plan task from Gooding’s 182-day termination rule. Preserve all 1,306 prior rows (`work/research/2026-11-06/idaho-discovery-review/`). Ledger: 132 unreviewed, thirty-eight reviewed withheld cases.

- [x] Independently review five Kansas candidates, eleven retained PDF pages and two complete HTML texts. Correct unsigned Harvey copy, preserve June/July BESS vote conflict and Jefferson April/May publication/adoption conflict; keep registered OCR separate from original extraction (`work/research/2026-11-06/kansas-discovery-review/`). No canonical changes; 127 unreviewed and forty-three reviewed withheld cases remain.

- [x] Review five NE/UT/WY cases; add historical Sarpy from four-page visual review correcting worker/extraction signature error. Preserve adoption versus stated earlier start, latest endpoint and unknown earlier event; all 1,307 prior rows unchanged. Hold four source-limited histories (`work/research/2026-11-06/plains-mountain-discovery-review/`). Ledger: 122 unreviewed, forty-seven reviewed withheld cases.

- [x] Review five North Dakota candidates using three complete retained reports and two Stark PDF pages. Preserve Bowman sector-vote versus instrument-count distinction, Durbin/Harmony identity and Stark’s printed year conflict; no canonical changes (`work/research/2026-11-06/north-dakota-discovery-review/`). Ledger: 117 unreviewed, fifty-two reviewed withheld cases.

- [x] Reconcile all 185 discovery candidates against 30 review packets; verify 179 explicit candidate fingerprints and re-verify 185 original/followup source versions, with four pilot versions independently checked in the Maine packet, while retaining six alternate-layout scope limits. Distinguish 38 additions, one covered instrument, 146 reviewed withheld cases and zero awaiting review (`work/audit/discovery-coordinator-accounting-2026-11-06.md`). This is mechanical accounting, not final freshness or legal-force acceptance.

- [x] Review six Minnesota candidates using ten PDF pages and two report portions; add Pequot Lakes city-reported active from official staff report, preserving unknown adoption and all 1,308 prior rows. Correct Foley signed-copy claim, retain Traverse date and Pipestone effective-date conflicts (`work/research/2026-11-06/minnesota-discovery-review/`). Ledger: 111 unreviewed, fifty-seven reviewed withheld cases.

- [x] Review six Maryland/New Jersey candidates, all seven retained PDF pages and four accessible report texts; add Talbot’s historical five-calendar-month solar instrument and East Windsor’s pending data-center draft. Preserve all 1,309 prior rows, registered OCR/original extraction distinction and four source/history gaps (`work/research/2026-11-06/maryland-new-jersey-discovery-review/`). Ledger: 105 unreviewed, 61 reviewed withheld cases.

- [x] Review eight remaining Colorado candidates, eleven PDF pages and four distinct accessible HTML source texts. Add two distinct Phillips County historical instruments with signed August 27, 2026 extension endpoints and Fort Collins’ unsigned pending proposal; preserve all 1,311 prior rows and five withheld histories (`work/research/2026-11-06/colorado-discovery-review/`). Ledger: 97 unreviewed, 66 reviewed withheld.

- [x] Review eight Indiana candidates, all eight PDF pages and four distinct retained HTML sources at their accessible scope. Add Vermillion County and Zionsville official pending proposals, preserve compound duration/referral stages and all 1,314 prior rows; retain six primary/action-history gaps (`work/research/2026-11-06/indiana-discovery-review/`). Ledger: 89 unreviewed, 72 reviewed withheld.

- [x] Review eight Alabama/Georgia candidates against nine distinct original sources and seven PDF pages; add Union County’s signed historical original-term instrument with separately registered OCR, preserving all 1,316 prior rows. Retain seven scoped act/action/history gaps and shared regional-news lineage (`work/research/2026-11-06/alabama-georgia-discovery-review/`). Ledger: 81 unreviewed, 79 reviewed withheld.

- [x] Fix legacy promotion identifier parsing for letter-prefixed resolution/ordinance numbers and explicit Number labels; preserve O/OR/ORD prefixes rather than consuming letters as punctuation. Reproduce same-day/same-sector false duplicate, verify original-row preservation and replay, inspect 35 changed parser outputs with no CSV edits, and pass all 181 native-runtime tests (`work/audit/prefixed-instrument-parser-validation-2026-11-06.json`). Free-text parsing remains a routing heuristic, not identity acceptance.

- [x] Review ten Kentucky/Louisiana candidates against thirteen distinct original versions and eight PDF pages; add Camargo adopted-instrument and Bossier historical records, preserving all 1,317 prior rows. Correct Henderson signed-copy claim and Camargo crypto scope; retain eight gaps and Washington 14/34-page review limit (`work/research/2026-11-06/kentucky-louisiana-discovery-review/`). Ledger: 71 unreviewed, 87 reviewed withheld.

- [x] Correct README Wisconsin count and explicitly include all three states tied at tenth; independently check both ranking sentences against current CSV counts (`work/audit/state-ranking-copy-review-2026-11-06.json`). This bounded check does not complete the full prose/rendered-surface audit.

- [x] Review twelve remaining Massachusetts/Pennsylvania discoveries against eleven retained HTML source versions. Preserve floor-substitution/definition and tally conflicts, distinct wind histories, county identities, curative-stay/model distinctions and Amity adoption-versus-commencement correction. All twelve withheld; canonical inputs unchanged (`work/research/2026-11-06/massachusetts-pennsylvania-discovery-review/`). Ledger: 59 unreviewed, 99 reviewed withheld.

- [x] Review nine remaining Carolina/Virginia discoveries against twelve original versions and seven PDF pages; add town-reported Mooresville and pending Awendaw while preserving all 1,319 prior rows. Keep unsigned/final-text, threshold, reading-stage, historical and predecessor gaps scoped; Greene visual review 3/46 only (`work/research/2026-11-06/carolinas-virginia-discovery-review/`). Ledger: 50 unreviewed, 106 reviewed withheld. Reconcile North Carolina ranking count to 70 in both README sentences (`work/audit/state-ranking-copy-review-carolinas-2026-11-06.json`).

- [x] Prepare the next fifteen discovery reviews with eighteen original version hash checks, 26 located worker excerpts and 35 PDF-page visual receipts; archive seventeen successful versions with twelve new native entries and five existing correspondences (`remaining-states-discovery-review/review-preparation.json`). Three additions and twelve withheld dispositions are prepared; promotion, final ledger changes and batch validation remain open. No inventory or ballot counts change at this checkpoint.

- [x] Finalize fifteen remaining-state discovery dispositions and add signed Stephenson County, Whitman County and Spokane Valley records; preserve all 1,321 prior rows. Retain twelve specific withholding reasons, unit/date/execution qualifications and partial-page scope (`remaining-states-discovery-review/`). Ledger: 35 awaiting review, 118 reviewed withheld; source archive preparation remains a historical checkpoint.

- [x] Review ten New York discoveries against eight retained source versions and all nine PDF pages; add historical Niagara and source-stage pending Massena while preserving all 1,324 prior rows. Retain Spafford nine/twelve-month conflict and distinct battery act, numbered-text lifecycle gaps, shared Preble lineage and unresolved instrument count (`new-york-discovery-review/`). Ledger: 25 awaiting review, 126 reviewed withheld.

- [x] Review all nine Michigan discoveries against nine original versions and all 29 PDF pages; add two separately numbered historical Locke acts and township-reported Meridian BESS adoption, distinct from its existing data-center act. Preserve all 1,326 prior rows; retain six execution/publication/history/primary-source gaps (`michigan-discovery-review/`). Ledger: 16 awaiting review, 132 reviewed withheld.

- [x] Complete the final sixteen Maine discovery dispositions; add historical Bridgton/Ashland and retain fourteen specific source/legal gaps, with fifteen source versions and fifteen selected PDF-page proofs (`maine-discovery-review/`). All 1,329 prior rows preserved. Frozen discovery queue fully dispositioned: 38 additions, one covered existing, 146 reviewed withheld.
- [x] Recover Jay's signed warrant/question, proposed petition and placement minutes using Exa/SerpAPI/bc-web/pydoll plus official-media reference chasing; publish scoped solar ballot/proposal and secondary unofficial1464/723observation outside frozen56groups (`jay-ballot-primary-review/`, `jay-ballot-promotion/`). All prior expanded records and both legacyCSVbytes preserved.
- [ ] Recover Jay's primary election return/certification, formal passage rule/outcome, enrolled law, town-established effectiveness and operative history; resolve independent petition sufficiency and any legacy instrument link (`work/audit/jay-solar-ballot-followup-2026-11-06.json`). Scoped publication does not close these evidence requirements.

- [x] Repair source-relative site link rewriting so only generated pages become HTML; preserve unrendered research Markdown, root landing/index mappings, URL queries/fragments and external links. Six regression cases and all 187 native-environment tests pass; local resolution checks cover 59 rendered pages and 953 references with zero missing targets (`work/audit/site-link-render-review-2026-11-06.json`). Hosted HTTP/anchor verification and broader copy/release gates remain open.
