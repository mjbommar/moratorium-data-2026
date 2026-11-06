# Implementation TODO

Plan: [Research modernization and ballot-measure expansion](docs/research-and-ballot-expansion-plan.md).

Created: 2026-11-05. Execution began under the user’s subsequent active-goal instruction.
Checked tasks have local evidence; unchecked tasks remain required. No release has been published.
Complete phases in dependency order; retain evidence and unresolved dispositions.

## P0 — Baseline and ownership

- [x] Record Git revisions, dirty state, canonical CSV hashes, counts and generated-artifact baseline.
- [x] Pin the inspected bc-modules revision, package versions and runtime/dependency configuration.
- [x] Confirm dataset ownership and exact consumer paths across public, research, site and integration repositories.
- [x] Establish admitted durable archive and local NVMe database paths; run storage preflight before bulk writes.
- [ ] Inventory existing source manifests and define a reversible mapping to bc-store observations.
- [ ] Record current legal-status cutoff and clause-extraction cohort limitations.

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
- [ ] Record all chunk coverage, extraction ceilings, failures and resumable status.
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
- [ ] Search new local instruments across all 50 states/sectors and document actual jurisdiction/time coverage.
- [x] Receive and mechanically audit all 50 state-discovery returns: five sector labels and schema-valid answers per state, 185 local proposals pending substantive review (`work/audit/state-discovery-returns-2026-11-05.json`). This does not close the preceding coverage task.
- [ ] Review site-operator search scope diagnostics and repair deficient official-record searches before accepting any negative coverage finding (`work/audit/search-scope-diagnostics-2026-11-05.json`).
- [ ] Define and budget the project/disclosure refresh scope separately; retain dated snapshots where full recollection is outside scope.
- [ ] Seed candidate lists from Ballotpedia, Duane Morris, Redbud and independently found official sources.
- [x] Compile all 22 terminal ballot jobs into a candidate review snapshot: 58 observations, 56 logical seed groups, pinned inputs and explicit Illinois duplicate identities (`work/research/2026-11-05/ballot-census-review/`). Evidence, census completeness and legal promotion remain open.
- [ ] Reconcile 41/44/45 November tallies by record-level set differences and explicit inclusion rules.
- [ ] Acquire ballot/warrant text, qualification/referral records and official return/certification evidence.
- [ ] Keep unofficial, certified, recounted and amended results as distinct observations.
- [ ] Check exact wording, passage rules and reverse/mixed polarity for every included measure.
- [x] Review Eliot Question 5 against the official sample ballot, signed warrant and certified proposed text; pin five visual source passages and classify the enactment question, while leaving its effective date and legal-force interval unresolved (`work/research/2026-11-05/ballot-census-review/eliot-review.md`).
- [ ] Verify post-vote legal implementation, effective/applicability dates, exemptions and challenges.
- [ ] Match prior pending instruments before creating new moratorium rows.
- [ ] Record bans and other restrictions separately, with explicit predecessor/replacement links.
- [ ] Preserve failed qualification, withdrawn measures, unresolved cases and bounded negative searches.
- [ ] Reconcile earlier 2026 measures and stage upcoming December measures separately from November totals.
- [ ] Refresh council-adopted moratoria and expiry/extension worklists alongside election work.
- [ ] Resolve Elmwood MI original February ordinance versus June Resolution 2026.06.17.A identities/terms; obtain Frenchtown original Ordinance 300-19 and extension anchor (reviewed-michigan-b).
- [ ] Backfill jurisdiction/source links and document legacy calendar-duration compatibility.
- [ ] Reconcile Leominster petitions 02-27/03-27 into distinct instrument identities with preserved legacy lineage, and resolve the New Orleans January motion/interim-ordinance relationship (`reviewed-louisiana-massachusetts/review.json`).
- [ ] Produce row-level explanations for every change to legacy summary counts.

Exit: every seed has a documented disposition; evidence gaps are visible rather than silently omitted.

## P6 — Public release and sibling handoff

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

- [ ] Implement due-work rules for qualification, elections, certification/recounts, implementation and expiry.
- [ ] Add conditional/adaptive recrawl while preserving prior observations and cached-body limitations.
- [ ] Exercise an end-to-end correction and refresh cycle manually.
- [ ] Track source failures, backend contribution, coverage gaps, freshness and review backlog.
- [ ] Document operator recovery, storage restore, interruption and budget-stop procedures.
- [ ] Create schedules only if explicitly requested; record cutoff, scope and budget for each.

Exit: repeatable refresh with visible freshness, costs, failures and unresolved work.
