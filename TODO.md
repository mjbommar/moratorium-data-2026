# Implementation TODO

Plan: [Research modernization and ballot-measure expansion](docs/research-and-ballot-expansion-plan.md).

- [x] Reconcile seven Seattle survivor narrative fields against retained ordinance/clerk evidence, including expansion exception and distinct work-plan deadlines; preserve current-force and consumer gaps. [Packet](work/research/2026-11-06/seattle-survivor-reconciliation/README.md).

- [x] Refresh California AB2170, AB222 and SB978 primary histories with native Exa/HTTP/pydoll acquisition; qualify three status strings. Ultimate dispositions remain unresolved. [Evidence packet](work/research/2026-11-06/ca-policy-wave3/README.md).

Closeout execution order: [November refresh closeout](docs/release-closeout.md). This preserves the full requirement scope and sequences remaining review, final data freeze, copy/consumer reconciliation, publication and deployment verification.

Latest repair: [controlled model transport](docs/controlled-model-transport.md)
has persistent HTTP ceilings and six passing mock-transport tests; all 248 project
tests and 42 subtests pass. Shared bc-llm retry fix is isolated at `d5acda10`.
The installed runtime remains unchanged; no new paid extraction or canonical
promotion occurred. Full extraction-quality and P2/P4 gates remain open.

Composed-support development: [checkpoint](docs/extraction-support-development.md)
records transport schema 1.1.0, two distributed terra CLI reviews, preservation
of rejected-context packets and exact frozen-code auditing. This is regression
coverage, not a passed extraction evaluation or completed semantic migration.

- [x] Define the development-relative advisory mechanism axis and contest-count
  completeness semantics; inventory all eight current advisory uses and the one
  complete result, with two independent terra CLI reviews
  ([definitions and field-specific follow-up queue](docs/ballot-semantic-definitions.md)).
- [x] Strengthen explicit mechanism claim lineage for Wrightstown, Downe, Joliet
  and Bloomington; re-review Monterey Park's final contest canvass and record
  completeness/scope support. Preserve prior decisions and all legal qualifications.
  [Applied packet](work/research/2026-11-06/ballot-semantic-lineage/README.md)
  retains the immutable predecessor and separately records two geography corrections.

Created: 2026-11-05. Execution began under the user’s subsequent active-goal instruction.
Checked tasks have local evidence; unchecked tasks remain required. No release has been published.
Complete phases in dependency order; retain evidence and unresolved dispositions.

## P0 — Baseline and ownership

- [x] Record Git revisions, dirty state, canonical CSV hashes, counts and generated-artifact baseline.
- [x] Pin the inspected bc-modules revision, package versions and runtime/dependency configuration.
- [x] Confirm dataset ownership and exact consumer paths across public, research, site and integration repositories.
- [x] Establish admitted durable archive and local NVMe database paths; run storage preflight before bulk writes.
- [x] Map 6,647 current legacy manifest entries to native observations or explicit path gaps; import 3,204 verified-body versions after private CAS link recovery, retaining 3,443 listed-path gaps (initial mapping and subsequent migration/recovery deltas). Of those gaps, 119 are failed acquisitions without a recorded body hash. Other private stores remain incompletely searched; this does not close the full P3 archive gate.
- [x] Record the November 5 working-cohort cutoff, record-specific source/legal-force limits and historical 348-extraction/211-jurisdiction pre-April-28 cohort in README, methodology and known gaps; no inventory-wide legal-force renewal is claimed.

Exit: reproducible baseline manifest with unrelated work preserved.

## P1 — Data contracts

- [x] Add explicit versioned instrument-event action validation and exact accepted
  event-claim/field binding, preserving historical profile selection and the frozen
  predecessor/replacement example ([event contract](docs/instrument-events.md)).
- [x] Promote the reviewed initial five-event/three-instrument cohort through
  identity, source-proof and field-review gates; preserve legacy rows and unknown
  expiry/current force ([cohort](work/research/2026-11-06/instrument-event-migration/cohort.json)).

- [x] Define schemas and fixtures for jurisdictions, elections, ballot measures and provisions.
- [x] Define versioned result observations, vote denominators, passage rules and certification states.
- [x] Define non-moratorium local restrictions without widening the legacy inventory denominator.
- [x] Define typed measure–instrument links, instrument events, claims and scoped review decisions.
- [x] Define and test explicit UUID allocation, pinned observation aliases, collision checks and append-only merge/split lineage (`docs/expanded-identity-registry.md`). Domain-fact import remains separate.
- [x] Preserve existing moratorium/project/state-action IDs and document tagged references. The reviewed Seattle duplicate retirement retains both full original rows and permanent IDs in the append-only legacy alias registry, with lookup and validation compatibility (`docs/legacy-moratorium-identities.md`); final downstream snapshot reconciliation remains open.
- [x] Separate lifecycle, result, certification, bindingness, mechanism and yes-vote direction.
- [x] Define date bounds, precision, local timestamps, retroactivity, calendar durations and end conditions.
- [x] Define threshold units, operators, aggregation, exemptions and measurement basis.
- [x] Define search/coverage provenance and independently tracked stage-completeness states.
- [x] Decide authoritative JSONL/snapshot/identity paths and document all fifteen CSV projections plus the current-result view, with pinned generation manifests, unknown-value rules, atomic relative pointers, checked downloads and release inclusion (`docs/expanded-data-contracts.md`, `scripts/build_expanded_csv.py`). This does not close broader pilot review or legal/source migration.
- [ ] Review schema examples against all pilot cases before implementing import/apply logic. A retrospective seventeen-case review is now frozen and checked (`pilot-contract-review/`); the original ordering was not met and this does not close the pre-tuning/P4 gate.

Exit: ballot cases fit without conflating votes, legal force or legacy counts.

## P2 — Search and acquisition adapters

- [ ] Build a closed jurisdiction/official-source registry with aliases and election-portal hosts.
- [x] Build sparse bc-spec worklists for inventory refresh, election census and gap discovery: all 1,330 local, 442 state-policy and 50 ballot IDs, plus distinct 50-state/five-sector exploration frames. Sector-neutral queries preserve unresolved sectors; full selection and seeded exclusions are explicit. Generation is not research or full host review ([documentation](docs/sparse-refresh-worklists.md)).
- [ ] Add deterministic plan preview, seeded sampling and call/cost estimates.
- [x] Configure provider-specific Exa/Google query variants through native `Searcher.search_many`; run bounded Seattle and Jay cases with persistent call reservations and exact native/runtime pins (`docs/search-refresh-batch.md`). Full registry/worklist generation, account pricing and calibration remain separate open gates.
- [x] Retain native reciprocal-rank fusion provenance, original per-variant sightings, response hashes and backend errors in the search-batch adapter. Verify shared-URL fusion, concurrent same-provider attribution, credential redaction, normalizer compatibility and exact cached replay; broader canonical provenance migration remains open (`docs/search-refresh-batch.md`).
- [x] Add offline research-client search provenance review adapter; verify three actual Jay responses/provider exchanges and preserve unpriced spend separately. Error-path exchange ingestion and new durable query/window intent are also tested; canonical publication and rank fusion remain open (`scripts/normalize_search_provenance.py`).
- [ ] Add Google News RSS/GDELT and bounded paid-news escalation with index-window decline handling.
- [ ] Add intent-specific query expansion, primary-host discovery, historical time walks and undated-source recovery.
- [ ] Add exact-identifier/reference chasing, feedback queries and bounded relaxation.
- [ ] Calibrate ResearchSearch tiers without excluding primary sources or reverse-polarity measures.
- [ ] Reserve bounded deep_research/source-agent use for difficult cases; retain skipped stages and conversations.
- [ ] Configure current SerpAPI pricing and whole-run/per-stage budgets, including unpriced-call policy. The frozen extraction trial also finds that backend max_attempts1 leaves SDK retries enabled; actual provider attempts and failed-attempt spend are unobserved (`frozen-domain-evaluation/sdk-retry-audit.json`). The new committed development comparison pins SDK retries to zero, observes HTTP reservations and holds unpriced failures under a before-write storage cap (`work/research/2026-11-07/compound-chunk-policy-evaluation/`); its four-case provider execution finished with 13 HTTP attempts, 12 returned results, 52 unpromoted candidates and a held $0.75 unpriced failure reservation; two independent reviews, root adjudication and the frozen audit are complete. Both policies failed the quality gate (default 36/40 supported, whole-text 10/12; incomplete required slots); no candidates were promoted. This does not reconstruct the old run or settle SerpAPI/whole-run pricing.
- [ ] Pin model roles/settings and cache fingerprints; redact secrets from retained responses.
- [x] Implement HTTP/browser escalation and bounded PDF/office-document collection.
- [ ] Configure source/provider pacing, Retry-After, explicit retries and verified routing as applicable.
- [x] Distinguish backend errors, successful zero-hit queries, index-window declines and returned hits in bounded search coverage reports; retain separate domain-mismatch diagnostics. Test error/zero/decline paths and retain the actual deficient Seattle query plus separately capped repair (`docs/search-refresh-batch.md`).
- [x] Publish the first bounded canonical search provenance cohort (Jay: one run, three attempts, eighteen sightings, one partial coverage observation), after full evidence preflight and identity review; preserve all prior domain tables and verify exact replay. Broader canonical migration and coverage calibration remain open; the later native fusion adapter is recorded separately (`jay-search-promotion/`, `docs/search-refresh-batch.md`).

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
- [ ] Obtain Bloomington's original township placement/qualification disposition and boundary reference (`work/research/2026-11-05/illinois-remaining-ballot-review/`, current canonical scope note). June 1 and June 22 agendas do not establish a final placement vote or boundary.
- [x] Recover and publish Joliet's original referral/advisory authority: signed Resolution 2026-08 and county-clerk notice (`work/research/2026-11-06/joliet-qualification-review/`, `joliet-promotion/`). November 7 re-fetch matched the existing canonical resolution body; no new measure or fact was added.
- [ ] Resolve Joliet's original annual-meeting minutes, actual transmittal/complete petition history, final result certification and five-ballot source-accounting discrepancy (`work/research/2026-11-06/joliet-promotion/`). Clerk certification of the resolution copy does not certify election results.
- [ ] Verify electorate/qualification and policy direction for the additional Madison-report wind/solar zoning-control question; reconcile it beyond the frozen v3 seed set without treating it as a development ban or silently changing census counts (`illinois-township-ballot-review/additional-leads.json`).
- [ ] Complete broader promotion/recovery calibration and the remaining ballot identity/fact reviews; the initial Eliot batch does not close P3.
- [ ] Extend evidence archive/publication gates to new records and source payload types.
- [ ] Add behavioral regression checks from plan section 11 (initial subset includes offline publication/receipt drift, historical identity baselines and portable-pointer checks; full gate coverage pending).

Exit: every accepted pilot assertion traces to reviewed evidence; unresolved cases stay unresolved.

## P4 — Pilot and calibration gate

- [ ] Freeze a source-backed pilot and holdout set before prompt tuning.
- [x] Review Peru, Wells, Bloomington, Piqua, Grove City, Harwood, Wilmington and El Dorado against their scoped source packets and immutable canonical records. Freeze explicit expectations and unresolved fields rather than treating the plan descriptions as established facts (`work/research/2026-11-06/pilot-contract-review/`). This retrospective review does not close the P4 metrics/holdout gate.
- [x] Include earlier/December elections, failed qualification, changed results, mixed polarity and portal failure cases in the seventeen-case fixture set. Clarksville retains its conditional/conflicting date; five artificial schema examples are explicitly labeled. No synthetic or unresolved candidate is counted as a canonical election (`pilot-contract-review/`).
- [x] Include a real historical council adoption/extension example: Morro Bay Ordinances 668/670, backed by official city minutes (`work/research/2026-11-07/morro-bay-council-review/council-history-reference.json`). Final signed terms and current force remain unresolved; this additive retrospective reference does not repair original pilot ordering or pass P4.
- [ ] Include a source-backed predecessor-pause/replacement-ban history; Piqua/Grove City relationships remain unestablished.
- [ ] Measure discovery recall, false exclusions, primary-source recovery and identity/quote/date/unit accuracy.
- [ ] Report reviewer disagreement, unresolved facts, extraction completeness and spend per review-ready record. A first frozen three-document actual-model evaluation now records 36 candidates, two independent terra CLI reviews, 35/36 label agreement, four unresolved classifications, 11/12 slot matches and no review-ready documents (`frozen-domain-evaluation/`); the broader P4 gate remains open.
- [ ] Set and assess documented quality thresholds; resolve silent high-impact errors before scaling. The first frozen extraction trial failed its 95% fully-supported-candidate gate; do not scale or count ambiguous candidates as errors resolved (`work/research/2026-11-06/frozen-domain-evaluation/README.md`).
- [ ] Present exact batch scope, call count, model/effort and budget for authorization before bulk execution.

Exit: accepted pilot report and separately authorized bounded collection scope.

## P5 — Reviewed collection and migration

- [ ] Freeze the full-refresh scope matrix, execution-time cutoff and required sibling/consumer dispositions (plan section 9.1).
- [x] Add a hashed per-record collection/edit accounting snapshot for both canonical inventories, keeping unresolved worker returns, queued jobs, pilot exclusions and apply-ledger changes separate (`scripts/build_refresh_accounting.py`, `work/audit/refresh-record-accounting-2026-11-05.md`). This is not the completed source/current-force freshness funnel.
- [x] Finish and mechanically audit all 333 distributed `gpt-6.1-terra` queue jobs, with zero running/queued jobs and hashed terminal execution receipt (`work/audit/distributed-queue-terminal-2026-11-05.json`). This records returns for 1,283 assigned local and 434 assigned state-policy IDs; it does not complete substantive review or legal-force verification.
- [ ] Re-research every existing local inventory ID and publish confirmed/changed/unresolved/not-attempted freshness accounting.
- [x] Finish the new six-job, 474-row calendar-versus-fixed-day encoding review, independently adjudicate returns and apply only source-supported original-term corrections (`work/jobs/2026-11-06-duration/queue.json`). Preserve genuine day-based originals and calendar extension distinctions; this is separate from whole-record freshness.
- [x] Close the frozen duration queue: all 474 coordinator-dispositioned, 230 corrected / 21 retained / 223 withheld / zero awaiting review. Final cohort applies 43 corrections and exact cumulative comparison limits changes to 460 duration fields (`closure.json`, `validation-wave6.json`).
- [ ] Resolve the remaining 219 original-term numeric/calendar-unit source-support requirements from the frozen 223 (`work/research/2026-11-07/california-original-term-review/remaining-original-term-requirements.json`). Carroll County/Anniston original clauses and scoped Gilroy/Angels descriptive 45-day fields have support. Exact Angels/Gilroy operative-wording, finality and effectiveness questions remain explicitly queued in `operative-wording-followups.json`; Calera/South Fork and Ormond questions remain. No whole-record freshness or current-force acceptance is implied.
- [x] Confirm Seattle’s two legacy rows describe the same ordinance using retained original text, fresh official legislative summary/history and three visually reviewed pages; distinguish council9–0 from the3/4threshold. Test a guarded frozen-row mapping preview; no count/ID changes applied (`seattle-identity-review/`).
- [x] Apply the reviewed Seattle duplicate retirement with permanent alias/history and reconcile seven survivor narrative fields. The current CSV contains only `wa-seattle-2026`; `wa-seattle-2026-2` resolves through the retained registry, and current source counts already include this correction (`seattle-identity-review/retirement-validation.json`, `seattle-survivor-reconciliation/`). This corrects a stale unchecked task; it is not a new count change.
- [ ] Finish final downstream consumer/release reconciliation for Seattle identity and survivor corrections; later renewals, termination and current legal force remain unverified.
- [x] Adjudicate the fifth 79 duration cases: apply 50 corrections, retain three original day counts and withhold 26; cumulative 395 reviewed / 187 corrected / 17 retained / 191 withheld / 79 pending. Preserve city/county Durham distinctions, original versus extension intervals and voluntary/ballot legal-effect limits (`coordinator-fifth-cohort.json`).
- [x] Adjudicate the fourth 79 duration cases: apply 30 corrections, retain Pendleton’s explicit-day original and withhold 48; cumulative 316 reviewed / 137 corrected / 14 retained / 165 withheld / 158 pending. Visually verify Salina’s term and preserve Cairo’s stable ID (`coordinator-fourth-cohort.json`).
- [x] Adjudicate the third 79 duration cases: apply 36 corrections, retain three explicit-day originals and withhold 40; cumulative 237 reviewed / 107 corrected / 13 retained / 117 withheld / 237 pending. Preserve original versus extension semantics and every other field (`coordinator-third-cohort.json`).
- [x] Adjudicate the second 79 duration cases: apply 36 more encoding corrections, retain two explicit-day originals and withhold 41; cumulative 158 reviewed / 71 corrected / 10 retained / 77 withheld / 316 pending. Current-force, dates and all other fields preserved (`coordinator-second-cohort.json`).
- [x] Receive and mechanically validate all six duration-review returns; adjudicate first 79 cases and apply 35 encoding-only corrections, retain eight explicit-day originals and withhold 36. Verify all other values unchanged and exact replay (zero edits); 395 coordinator reviews remain (`duration-encoding-review/`).
- [ ] Re-research every state-policy ID and discover new state actions across all 50 states and existing sectors.
- [x] Complete the bounded original positive-force flag audit: source-review NY EO62 and Texas directive as unknown at cutoff; recover Texas SB6 code through pydoll and retain scoped statutory force, alongside the prior Delaware codification reviews. Apply twelve guarded descriptive/epistemic corrections, preserve IDs and other cells, record extraction omissions and explicit source failures (November 7 executive-force packet). Broader freshness remains open.
- [x] Account for all 40 Pennsylvania/Virginia policy IDs and apply 92 scoped source-supported corrections, including 38 links, four enacted effective dates and source-specific proposal/exception/actor corrections; three terra CLI reviews, native Exa, pydoll and 22 coordinator-inspected print/PDF pages retained (`pa-va-policy-review/`). All-field freshness and later legal histories remain open.
- [ ] Migrate reviewed state-policy precursor/resolution forms and lineage with backward-compatible IDs before claiming a unique-bill census; three PA memo links are verified while legacy types/counts remain explicitly qualified (`pa-va-policy-review/precursor-links.json`).
- [x] Separate ten source-reviewed legislative-resolution rows and three precursor memo rows from the bill-type bucket with all 442 IDs preserved. Update legal-form contracts, typed bill rankings and current count/copy surfaces; keep compound observations and memo-to-bill associations intact (`work/research/2026-11-07/state-policy-forms/`). Canonical lineage and unique-instrument grain remain open.
- [x] Review all 23 Ohio/Illinois policy rows within retained source scope, add official links and correct version-specific provisions, exceptions, sponsor dates and mechanisms; three terra CLI reviews and eight coordinator-inspected PDF pages support 60 field changes (`oh-il-policy-review/`). Full disposition/current-force and other field requirements remain open.
- [x] Separate the New Jersey S3379/A4096 and A4696 identities and apply five bounded corrections (`work/research/2026-11-06/nj-policy-wave1/README.md`); signed chapter 75/effective date, report-triggered expiration, implementation and remaining dispositions remain open.
- [x] Review the remaining three NJ worker returns and correct fifteen fields:
  S4293 conditional veto versus unsupported final death, S3611 SPC/default/subsidy
  limits, and A1170's conditional plan/supply rules with companion-version scope
  ([wave2](work/research/2026-11-06/nj-policy-wave2/README.md)). Signed Chapter75,
  S4293 final session disposition and implementation remain unresolved. Fresh
  catalogue retrieval reproduced the earlier body; no absence inference follows.
- [x] Review all three assigned Delaware records against retained and freshly recovered official sources; confirm two enactments/current codification and bound the failed SB 205 disposition (`work/research/2026-11-06/de-policy-wave1/README.md`). Rulemaking/tariff implementation and SB 205 amendment details remain open.
- [x] Review remaining California history returns and correct SB 978 using deletion-aware amended text (`work/research/2026-11-06/ca-policy-wave2/README.md`); AB 2170, AB 222 and SB 978 ultimate dispositions and full current-force review remain open.
- [x] Review six California enactments and SB 57’s final wording, and add missing AB 2469 using Exa, pydoll and chaptered text (`work/research/2026-11-06/ca-policy-wave1/README.md`); six other assigned California rows and current implementation remain open.
- [x] Apply three bounded Missouri policy corrections with independently recovered primary sources (`work/research/2026-11-06/mo-policy-wave1/README.md`); all seven assigned disposition/current-force reviews remain open.
- [x] Review all seven Missouri histories, refresh four through existing reservations and apply 12 bounded narrative/source-link/tariff-summary corrections; preserve every other cell and explicitly retain inherited disposition/party requirements (`mo-policy-wave2/`). This does not close Missouri final-disposition/current-force review.
- [x] Follow the five missing Missouri House action iframes and verify six 2026 sponsor-party fields with two separately bounded Terra CLI jobs, four Exa calls and twelve fetches including pydoll. Correct only SB 1750 party; retain final session/force requirements and visually verify that May 15 adjourned until May 28 (`work/research/2026-11-07/mo-full-actions-followup/`).
- [ ] Search new local instruments across all 50 states/sectors and document actual jurisdiction/time coverage.
- [x] Receive and mechanically audit all 50 state-discovery returns: five sector labels and schema-valid answers per state, 185 local proposals pending substantive review (`work/audit/state-discovery-returns-2026-11-05.json`). This does not close the preceding coverage task.
- [ ] Review site-operator search scope diagnostics and repair deficient official-record searches before accepting any negative coverage finding (`work/audit/search-scope-diagnostics-2026-11-05.json`).
- [ ] Define and budget the project/disclosure refresh scope separately; retain dated snapshots where full recollection is outside scope.
- [ ] Seed candidate lists from Ballotpedia, Duane Morris, Redbud and independently found official sources.
- [x] Compile all 22 terminal ballot jobs into a candidate review snapshot: 58 observations, 56 logical seed groups, pinned inputs and explicit Illinois duplicate identities (`work/research/2026-11-05/ballot-census-review/`). Evidence, census completeness and legal promotion remain open.
- [ ] Reconcile 41/44/45 November tallies by record-level set differences and explicit inclusion rules.
- [ ] Acquire ballot/warrant text, qualification/referral records and official return/certification evidence.
- [x] Use the remaining Clarksville and Ottawa recovery reservations: retain exact city document-folder leads, pydoll/API metadata and a visually checked Ottawa draft-minute passage; complete two terra reviews (`work/research/2026-11-06/pending-ballot-source-recovery/`). Both Clarksville groups and Ottawa remain unresolved; no canonical promotion or cap reset.
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
- [x] Review and separately publish Wilmington's proposed Chapter 1161 initiative as dated court-reported litigation history, with intended-election linkage and no result or legal effect. Preserve all four voted parcel referendums and frozen census groups; qualify later court/ballot history as unknown (November 7 initiative-history packet). Broader lifecycle coverage remains open.
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

- [x] Reconcile Fight a Data Center with its newer remote June printing/July research page, deliver scoped edition/ballot/White County copy corrections, and verify 95 rendered pages (`fightadatacenter.com` commit `58027fc`; `work/research/2026-11-06/fightadatacenter-current-copy/`). Broader legal/project-value claims and hosted revision remain open.

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
- [x] Prepare isolated paper-import compatibility candidate with independent manifest pin, verified-byte derivation and legacy API tests: nine targeted tests, offline ready replay and one fresh offline export/import pass. Preserve live owner files and campaign baseline; adoption remains open (consumer compatibility checkpoint).
- [ ] Extend copy/number audit coverage beyond the existing checker and inspect rendered landing/state pages and charts.
- [x] Export stable IDs and reviewed relationships to datacenter-data-integration without changing project ownership. Verified working-input delivery at `836a5a79`; see `work/research/2026-11-06/integration-handoff-v2/delivery-validation.json`. Downstream join acceptance remains separate.
- [x] Deliver profile 1.0.3 working inputs and corrected policy forms/rankings at integration remote `bf3d4a8b`; verify all 918 files/symlinks, five semantic tests, identical re-export and a clean Git-subtree round trip. Preserve old snapshots and joins (`work/research/2026-11-07/consumer-policy-form-compatibility/`). Final consumer/source freeze remains open.
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
- [x] Recover working-source Pages deployment for `81bf960`: native build/run `42352389597` succeeds, and hosted summary JSON matches committed bytes through bounded bc-web fetch (November 7). Final-release deployment and full page/link audit remain open.
- [ ] Verify required sibling remote/deployment states and document any remaining blockers.
- [ ] Record the public release URL, tag/commit, asset hashes, deployment and validation receipt; retain rollback inputs and unresolved queues.

Exit: fresh, reproducible release with reconciled data/prose, a verified published GitHub Release and assets, required deployed updates, and explicit freshness limits. Local preparation alone does not close P6.

## P7 — Maintenance

- [x] Integrate explicit profile 1.0.2 into structural validation, sealed publication/predecessor receipts, narrow historical field review, source-proof checks and retained/current/status CSV generation. Exercise source-byte synthetic withdrawal/correction/reinstatement, replay and offline restore with missing/tampered dependency cases. A deterministic 727-member committed bundle restores successfully; the real five-event validity migration is applied; broader consumer reconciliation and final release-asset verification remain open ([contract](docs/event-validity-publication.md)).

- [x] Implement and exercise the isolated event-validity maintenance contract: withdrawal/reinstatement, time-specific support, combined review timeline, typed one-to-many corrections and immutable predecessor retention. Subsequent versioned production integration and the real five-event migration are recorded below; broader maintenance/delivery gates remain open ([development history](docs/event-maintenance-development.md)).

- [x] Design and exercise event correction/withdrawal with retained rejected history. Profile 1.0.2 supports source-proof-backed synthetic withdrawal, correction, reinstatement and offline restore; the real five-event cohort now has explicit source-reviewed validity. No fake real-data withdrawal was created. Broader event-history collection, consumer reconciliation and the rest of P7 remain open ([real migration](work/research/2026-11-06/event-validity-migration/README.md)).

- [x] Exercise bc-web conditional HTTP caching with an actual 200/304 round trip, preserved body time and immutable archive tests (`conditional-cache-pilot/`); native adaptive proposals are implemented below, with inventory-wide calibration still open.

- [ ] Implement due-work rules for qualification, elections, certification/recounts, implementation and expiry.
- [x] Add opt-in conditional HTTP caching and an offline native bc-web adaptive revisit planner, preserving prior observations and cached-body limitations; actual cache pilot and planner tests retained. Inventory-wide calibration and task resolution remain open.
- [ ] Exercise an end-to-end correction and refresh cycle manually.
- [ ] Track source failures, backend contribution, coverage gaps, freshness and review backlog.
- [x] Audit the explicit retained search-ledger cohort with duplicate-ID checks and separate legacy/subset exceptions: 396 ledgers, 4,109 verified unique attempts, 22,863 sightings; distinguish errors, zero hits, nonterminal reservations and unpriced spend (`scripts/audit_search_cohort.py`, `search-provenance-cohort-2026-11-06.md`). This does not close freshness, canonical migration or complete coverage reporting.
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

- [x] Audit follow-up extraction readiness with two terminal distributed Terra CLI reviews and independently verify the isolated retry-fix backend through controlled mock HTTP: SDK retries zero, one 503 attempt, second invocation blocked by persistent cap; six transport tests pass (`work/research/2026-11-06/extraction-followup-readiness/`). Historical quality gate remains failed.
- [x] Freeze and execute the separate four-case Mandan/Harwood development comparison with source/model/pricing/caps, guarded storage/runtime pins, two independent reviews and root adjudication (`work/research/2026-11-07/compound-chunk-policy-evaluation/`). Both policies failed acceptance; no candidates promoted. This corrects a stale unchecked execution task and does not close unseen holdout, P4, source freshness or invoice accounting.
- [x] Implement optional compound-condition profile 1.0.3 and extraction transport 1.2.0, retaining legacy flat semantics and native transport/local-validation separation. Add complete-group scoring, quotation-location/context checks, invalid-neighbor retention and profile upgrade/replay/downgrade/withdrawal regressions. The subsequent source-reviewed migration activates profile 1.0.3 for twelve clauses; this implementation alone does not establish source acceptance or a passing quality evaluation (`docs/compound-condition-development.md`).

- [x] Verify full domain extraction through the isolated retry-fix SDK/backend and bc-evidence using mock HTTP: success, reconstructed-backend cache replay, failure retention, adapter cap and shared HTTP cap. No provider requests; no canonical writes (`compound-condition-development/full-runner-preflight.json`).

- [x] Publish twelve source-adjudicated proposed compound clauses on the existing Mandan/Harwood provisions under profile1.0.3, with twelve new claims/fourteen scoped decisions; reverify all540claims and preserve all other prior fields and records. Retain definition/comparison ambiguities, no current force inference, and unchanged headline counts (`work/research/2026-11-06/compound-clause-source-review/`).

- [x] Add explicit chunk-policy forwarding/context pins and preserve prior packets on rejected preflight input. The isolated native API has 92 unit tests; the application has 343 tests. Source-window analysis corrects the split-list hypothesis: all 12 primary quotes fit default windows, while full selected support jointly fits 2/12 default windows and 12/12 large windows. This is context availability, not measured extraction quality (`work/research/2026-11-07/chunk-policy-development/`).

### November 7 publication-surface audit follow-up

- [x] Record inspected core and sibling surface registers with authoritative inputs, edition limits, reviewer roles and concrete next actions (`work/audit/publication-surfaces-2026-11-07/`). This is an audit register, not full P6 acceptance.
- [x] Correct FAQ row total, unflagged subtotal and unsupported geocode accuracy inference; clarify extraction cohort units and selected numeric-checker coverage.
- [x] Resolve malformed dates, guessed statuses and stale caption in `tables/moratorium-inventory-clean.tex`; restore two false name-filter exclusions and verify all 1,330 rows/statuses (`work/audit/inventory-table-2026-11-07/`). Standalone layout limits remain documented.
- [ ] Complete all unverified visual, substantive-copy, edition and consumer actions in the publication surface registers before release approval.

### Revised condition-contract development evaluation

- [x] Freeze and independently review a separate bounded protocol after the complete-condition prompt revision; exercise healthy and failed-attempt accounting offline.
- [x] Execute four known-source cases in the new namespace: 12 HTTP attempts, 46 candidate fields, no extra calls on replay (`work/research/2026-11-07/compound-contract-evaluation/`). This does not establish quality acceptance.
- [x] Complete independent source reviews, selected coordinator adjudication and frozen accounting/quality audit for the revised-contract experiment. Both policies fail; old outputs and all disagreements are preserved. See `compound-contract-evaluation/audit-result.json`.
- [ ] Complete unseen-holdout and remaining P4 requirements; development performance alone cannot close P4.

### Direct rule-unit extraction development

- [x] Implement opt-in full-source per-rule typed extraction with explicit unresolved slots, sealed durable reservations and private workspace checks; verify 415 tests and independent controlled-development review (`work/audit/rule-unit-extraction-2026-11-07/`). No quality acceptance follows.
- [x] Prepare and independently review blind source inventories: 20 Mandan / 66 Harwood units, exact anchors and contextual locators private; preserve source/OCR ambiguities.
- [x] Freeze the separate direct rule-unit development protocol with reviewed inventories, actual backend/runtime/HTTP/storage/pricing pins and independent budgets (`direct-rule-unit-evaluation/protocol.json`).
- [x] Execute and independently source-review the known-source direct-unit pipeline; its quality gate failed. Prior failures, source-specific freshness, unseen holdout and broader quality acceptance remain open.

### Jay November 7 primary-source recheck

- [x] Recheck Jay using two Exa, two SerpAPI and six bc-web fetches (one pydoll); root-review official November 9 agenda. No recovered primary return/certification or canonical promotion (`work/research/2026-11-07/jay-primary-recheck/`).
- [ ] After the November 9 meeting, manually check posted minutes, primary Article 3 return/certification, enrolled text and operative dates; preserve the existing legal/result gaps. Queue only; no schedule created.

### Direct rule-unit live development protocol

- [x] Freeze and independently review the separate 86-request direct-unit development protocol, actual model/runtime/tool/retry/HTTP/storage/pricing pins and reviewed private plans (`work/research/2026-11-07/direct-rule-unit-evaluation/`).
- [x] Exercise full healthy/failing MockTransport runs and three-review auditor integration; preserve a pre-first-call correction allowing justified source nonextractability without discarding returned clauses or weakening required-slot/error rules.
- [x] Execute the frozen direct-unit live run:86responses, no failed/unpriced attempts or replay calls; frozen accounting reconciles $1.614114 in SDK estimates, not invoice.
- [x] Complete independent source reviews, selected coordinator adjudication and frozen quality audit:64/86supported labels,5/12slots,71exact-location-flagged units; gate failed, no promotion/P4closure.

- [ ] Before another known-document automatic-condition retry, reconcile the actual remaining P4 exit criteria (including unseen holdout/discovery metrics) and full-record freshness work; do not substitute repeated development experiments for the comprehensive refresh.
- [ ] Fix source-bound citations, reviewed document-context propagation and governing qualification/direction handling before further automatic condition generation; preserve all frozen failures.

- [x] Review all 78 fields in the three Alaska records with independent source checks; retain all three as researched/unresolved and apply only the guarded Houston project-attribution correction (`work/research/2026-11-07/alaska-source-review/`). This does not close whole-inventory freshness or later-history gaps.
- [x] Replace both legacy CSV writers atomically using same-directory staging, file/directory fsync and permission preservation; exercise failures before/after replacement and document separate receipt recovery (`work/audit/legacy-write-atomicity-2026-11-07.json`). This is the legacy single-file write guarantee, not cross-file transaction atomicity or the complete behavioral/P4 gate.
- [x] Exercise changed-body same-URL archive continuity through import and evidence auditing, including old/new claims, replay and tamper rejection (`work/audit/source-version-continuity-2026-11-07.json`); this is source-version lineage, not source entailment or the complete P4 gate.
- [x] Pin the prospective remaining-closeout scope, all 1,772 local/state baseline row hashes, all 15 expanded tables, archive inventories and seven required consumers (`work/research/2026-11-07/remaining-refresh-scope/`). The November 7 execution target retains older field support dates; this late freeze does not retroactively satisfy original ordering or close P4/P5.
- [x] Independently assess all 228 fields in the first six PA and first six VA policy records, retain source-specific unresolved gaps, and apply 12 guarded corrections across six records (`work/research/2026-11-07/pa-va-full-field-review/`). This is twelve of the 40-record packet and does not complete whole-policy freshness.
- [x] Complete independent substantive assessments of all 760 fields in the 40-record PA/VA packet; retain forty researched/unresolved outcomes and apply the final guarded 22-cell correction batch (`work/research/2026-11-07/pa-va-policy-review-closeout/`). This bounded completion does not close all-policy/current-force freshness, P4 or release.
- [x] Independently review and natively archive six recovered VA primary prints with original and separate layout text retained; replay adds no versions and existing 3,442 body gaps remain explicit (`work/research/2026-11-07/va-primary-print-recovery/archive-and-native.json`).
- [x] Independently assess all 26 Seattle fields; add only the source-matched July15 hearing and retain unknown extension/current-force gaps. Independently assess all 26 Grove City fields and qualify agenda/report wording; reject the other-item Effective span and unsupported Piqua/charter links (`seattle-history-followup/`, `ohio-history-followup/`). These bounded reviews do not complete all-local freshness or P4 histories.
- [x] Propagate caller-reviewed document title/role into experimental requests, flag proposed/enacted conflicts without label repair, and exercise actual native-store changed-body observation/claim continuity (`work/audit/document-context-and-native-lineage-2026-11-07.json`). Live model quality and P4 remain unproven.
- [x] Restore one exact-hash old Morro Bay staff-report PDF without altering original manifest bytes or observation date; reject the different Tribune body as a substitute (`work/audit/morro-bay-exact-body-restoration-2026-11-07.json`). Existing archive gaps decrease from 3,442 to 3,441; current force is not renewed.
- [x] Independently assess all 26 Morro Bay fields, apply four historical/uncertainty wording corrections and two original 45-day encoding corrections, retain final670/current-force gaps, and archive six source versions with reviewed OCR (`work/research/2026-11-07/morro-bay-council-review/`). Morro Bay is outside the frozen219 original-term queue; its count remains219.

- [x] Complete 156 independent field assessments across six Ohio records; apply 18 authored corrections plus one derived count across five records, clear three unsupported end dates, retain conflicting Shalersville reports and avoid duplicating Hubbard ballot measure (`work/research/2026-11-07/ohio-six-record-closeout/`). All six remain researched/unresolved overall; original-term queue remains 219.

- [x] Publish two source-supported historical Morro Bay council events with profile 1.0.3, retained prior records, all 545 claims source-checked and exact idempotent replay (`work/research/2026-11-07/morro-bay-event-migration/`). Seven events now; effective interval, permanent-ban linkage and broader P4 remain open.

- [x] Recover certified Arcata Ordinance 1594 using Exa/Serp/bc-web, independently and coordinately verify its original 45-day term, preserve frozen 219-entry queue and publish successor 218-entry ledger (`work/research/2026-11-07/original-instrument-recovery/`). Final successor, current force and three other recovered histories remain unresolved.

- [x] Apply six source-stage/endpoint corrections across Escondido and El Monte, preserve historical classifications and original-term requirements, and recompute four verification fields (`work/research/2026-11-07/california-successor-stage-review/`). Two unsupported operative endpoints cleared; final enactment/text and current force remain unresolved.

- [x] Execute frozen 27-unit Virginia domain evaluation and independently recompute all raw HTTP outputs against pinned layouts: at most 1/27 clauses meets literal-support prerequisites, so acceptance fails regardless of disputed semantic findings (`work/research/2026-11-07/prospective-va-domain-evaluation/`). No candidates promoted; semantic second adjudication and broader P4 remain open.

- [x] Independently adjudicate six wind/solar/BESS original-term cases, correct six fields across Sedgwick and Oshtemo, reject continuation-to-original misbinding for Seward, and retain five scoped gaps. Sedgwick-only closure reduces the successor queue from 218 to 217 (`work/research/2026-11-07/cross-sector-term-adjudication/`).

- [x] Apply ten Coachella legacy source/term corrections after independent review and root source adjudication; retain inherited classification as explicitly unverified pending lifecycle reconciliation, clear unsupported endpoint, and preserve the 217-item queue (`work/research/2026-11-07/coachella-legacy-source-review/`). Typed restriction/history publication remains open.
- [x] Complete 104 primary field assessments for the first four Georgia rows and independently adjudicate two changed fields; preserve other source judgments as qualified and unresolved (`work/research/2026-11-07/georgia-first-four-field-review/`). Subsequent packets complete the remaining 208 primary assessments; broader independent review remains open.

- [x] Complete the second 104-field Georgia subdivision and root-adjudicate Banks County's interdependent original 30-day/date-precision/extension/endpoint fields; preserve classification with explicit force limits and leave the 217 queue unchanged (`work/research/2026-11-07/georgia-second-four-field-review/`). Final subdivision now has 104 primary assessments; broader independent review remains open.
- [x] Make the appendix inventory table use canonical typed original-duration fields rather than extension prose; regenerate and add it to ordinary data/check targets, with regression cases for 45-day original versus 15-day extension fragments, calendar terms and unknown values. Broader chart/manuscript review remains open.

- [x] Integrate validation profile 1.0.4 for qualified typed policy succession, with old-profile preservation, exact related-reference/field/validity support, current restriction identity-alias checks and downgrade regressions. Native full suite passes 430; actual Coachella migration and committed portable bundle remain separate (`work/research/2026-11-07/policy-succession-profile/`).
- [x] Align appendix sector labels with canonical arrays; record 179 prior prose-heuristic disagreements without claiming independent legal-scope verification (`work/research/2026-11-07/typed-inventory-table/`). Other charts and narrative consumers remain open.

- [x] Finish all three Georgia subdivisions: 12 records/312 primary field assessments, with 116 third-packet proof spans checked and published as hashes/line ranges rather than raw OCR (`work/research/2026-11-07/georgia-twelve-field-assessment/`). This closes primary enumeration only; independent judgments, source gaps and current-force freshness remain open.

- [x] Publish Coachella's restriction and three historical events with a qualified typed policy predecessor under profile 1.0.4; verify 559 retained-source claim bindings, preserve all prior records and exact replay (`work/research/2026-11-07/coachella-restriction-history-migration/`). Ten events/two restriction records now; formal termination, current force, broader P4 and final release remain open.

- [x] Build the actual profile 1.0.4 working bundle twice at committed da17280 with identical hashes, restore and verify 1,068 members/all 36 retained generations/current CSVs/exact replay. Record internal-consistency limits and keep final source/consumer/release gates open (`work/research/2026-11-07/policy-succession-profile/committed-bundle-verification.json`).

- [x] Complete independent peer disposition enumeration for all twelve Georgia rows (312 fields); retain exact review hashes and per-packet counts in `work/research/2026-11-07/georgia-twelve-field-assessment/independent-review-coverage.json`. This closes review coverage only; coordinator correction adjudication and source/current-force gaps remain open.

- [x] Apply first two Georgia peer correction packets after independent source adjudication and full-row guards: 27 cells/six records including derived flags (`work/research/2026-11-07/georgia-peer-corrections/`). Third packet, original instrument/history gaps and comprehensive freshness remain open.

- [x] Recover and adjudicate actual signed Brooks/Calhoun originals and Calhoun extension minutes; apply 16 cells/two rows, preserve supported exact adoption dates and Calhoun January 25 endpoint, and qualify both Brooks draft-minute versions (`work/research/2026-11-07/georgia-recovered-originals/`). Current force, Brooks successor act and the Calhoun zoning transition remain unresolved.

- [x] Adjudicate eight retained-source original-term cases with independent review and full row guards: 56 cells/eight records; retain explicit Prichard 180-day report, remove seven unsupported numeric day encodings, clear Cullman endpoint and refine all eight open requirements (`work/research/2026-11-07/original-term-eight-source-adjudication/`). All 217 final-clause requirements and current-force gaps remain open.

- [x] Review all 19 fields in the seven Alabama/Alaska policy rows, independently adjudicate proposed corrections and apply 30 cells with exact guards (`work/research/2026-11-07/alabama-alaska-policy-source-review/`). Correct three Alaska moratorium mechanism mislabels and preserve qualified unresolved terminal-history/current-force and party questions. This does not close full-policy freshness.

- [x] Publish two source-reviewed Clarksville conditional referendum proposals under profile 1.0.4; preserve unknown final dates/ballots/effects, provisional intended-election identity, six concise source observations and all prior record bytes (`work/research/2026-11-07/clarksville-proposal-publication/`). Reconcile 51/56 frozen correspondences and two outside-freeze records.
- [x] Apply 15 guarded Colorado policy corrections after all 76 field assessments and independent source review (`work/research/2026-11-07/colorado-policy-source-review/`). Retain version, sponsor and amendment gaps and historical Lost observations.

- [x] Migrate the two Clarksville petition-described financing/tax-authorization mechanisms into source-qualified proposed provisions, preserving final-date/wording/effect unknowns and treating bond ceilings as authorization amounts, not project spending or eligibility thresholds. Two proposed provisions, two claims and ten decisions published after independent Terra and coordinator review; no legal-force claim accepted (`work/research/2026-11-07/clarksville-financing-publication/`).

- [x] Apply 21 guarded Arkansas policy cells across seven existing records after 133 field assessments and final visual source adjudication; retain current-law and effective-date followups (`work/research/2026-11-07/arkansas-policy-source-review/`).

- [x] Apply 21 distinct field corrections across the first four Arizona policy records after 76 assessments and independent review; retain the other nine rows and current-force/current-law followups (`work/research/2026-11-07/arizona-first-four-policy-review/`).

- [x] Apply 55 guarded cells across the remaining nine Arizona records after 171 assessments and independent adjudication, and reconcile four unsupported terminal categories in the first-four packet; all 13 Arizona records have 247 field assessments and 80 net field changes. Current-force/history/party/activity followups remain open (`work/research/2026-11-07/arizona-remaining-nine-policy-review/`).

- [x] Apply 40 guarded Connecticut/Delaware fields across ten existing records after 190 assessments, independent review and separate HB233/HS1 identity adjudication; retain carryover, later-law/current-force, party/activity and implementation followups (`work/research/2026-11-07/connecticut-delaware-policy-review/`).

- [x] Apply 80 guarded Florida/Hawaii fields across thirteen existing records after 247 assessments and independent source review; retain compound-resolution, intervening-amendment, party/activity and current-force limits (`work/research/2026-11-07/florida-hawaii-policy-review/`).

- [x] Apply 65 Iowa fields after 228 independent decisions; add the reviewed 19-field HF2799 record and resolve HF2357 identity without duplicate enactment. Current-force and source gaps remain open. [Review](work/research/2026-11-07/iowa-policy-source-review/README.md).

- [x] Apply 42 Georgia policy fields after 171 independent decisions; preserve legacy procedural and source limits, reject unfetched party/substitute/sunset claims, and register retained originals. [Review](work/research/2026-11-07/georgia-state-policy-source-review/README.md).
- [x] Refresh three data-derived figure families and timeline; fix legacy-date parsing to validated normalized months, preserve month-only precision, test regressions and retain four historical static legal-map families pending their source audit. [Receipt](work/research/2026-11-07/georgia-iowa-source-recovery/figure-review.json).

- [x] Review all 171 fields across nine Idaho policy records, independently adjudicate and apply 39 corrections with exact guards; recover enacted H0521 approval evidence and archive 29 source versions. Final-journal/current-force gaps remain open ([packet](work/research/2026-11-07/idaho-policy-source-review/README.md)).

- [x] Independently review 209 fields across eleven Illinois policy records and apply 26 guarded corrections; preserve synopsis/text conflicts and missing full versions, without resetting the shared acquisition ceiling ([packet](work/research/2026-11-07/illinois-policy-source-review/README.md)).

- [x] Independently assess 190 fields across ten Indiana policy records and apply 46 guarded corrections; preserve section-level dates and unresolved current force, and exercise native Exa/pydoll official-notice acquisition ([review](work/research/2026-11-07/indiana-policy-source-review/README.md)).

- [x] Independently assess 228 Kansas policy fields and amendment/carrier identity, apply 62 guarded corrections, and add tested legal-form support without treating the carrier enactment as amendment adoption ([review](work/research/2026-11-07/kansas-policy-source-review/README.md)).
