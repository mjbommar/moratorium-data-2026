# Research modernization and ballot-measure expansion plan

Date: 2026-11-05

Status: proposed implementation plan. This document authorizes no scheduled jobs,
bulk research runs, model spending, dataset migration, or publication. The companion
[TODO](../TODO.md) tracks implementation; its unchecked items are future work.

## 1. Objective and scope

The delivery target is a fresh end-to-end release, not only a ballot-measure schema
addition: re-research the existing inventory and state-policy tracker through a
declared cutoff, incorporate new discoveries and electoral records, regenerate
derived outputs, revise related prose/copy/summaries, publish the GitHub release,
and verify what readers can actually download and read. Completion requires the
release and its consumer-facing updates, not merely locally passing generators.

Extend the evidence-backed infrastructure-policy system to cover direct democracy
alongside the local moratoria and state policies already tracked. Modernize discovery,
collection, extraction, review, refresh, and publication using the current local
`bc-modules` libraries rather than rebuilding their capabilities in this repository.

The desired result is a reproducible account of:

- What a government proposed, adopted, extended, replaced, or repealed.
- What residents petitioned for and what qualified for an election.
- What voters were actually asked, how they voted, and whether results are certified.
- What legal change, if any, followed the vote, with its own scope and dates.
- Which projects are demonstrably covered and which associations remain candidates.
- Which sources support each claim, which disagree, and what remains unknown.

Maintain all existing sectors: data centers, battery storage, solar, wind, and
cryptocurrency mining. Prioritize the November 3, 2026 data-center election cohort,
then the earlier 2026 elections, upcoming December elections, and broader sector
coverage. Recall elections are related political events, not policy ballot measures;
record pointers and a separate queue without mixing them into measure counts.

Success means reviewed, inspectable observations and explicit coverage limitations.
It does not mean forcing every candidate into an accepted record or claiming causal
effects from nearby projects, electoral sentiment, or corporate disclosure.

## 2. Verified starting architecture

Inspected locally on November 5, 2026:

| Owner | Current responsibility | Planned boundary |
|---|---|---|
| `moratorium-data-2026` | Canonical local inventory: 1,291 rows, 26 columns; state policy: 440 rows, 19 columns; public derivatives and research decision audit | Own public ballot records and related local restrictions; preserve existing identifiers and CSV contracts |
| `moratorium-paper` | Research corpus, clause extraction, legal analysis, manuscript; mirror of public inventory | Consume reviewed public data; supply historical leads without creating a second inventory authority |
| `servercountry.org` | Canonical project CSV: 1,048 rows, 33 columns; project identity registry, aliases, public website | Continue owning project facts and identities |
| `datacenter-paper-2026` | Project discovery and reviewed update actions, state research and paper | Supply leads and consume canonical datasets; its project CSV is a symlink to Server Country |
| `datacenter-data-integration` | Candidate legal/identity review, project-policy bridges, disclosure ledgers and collaborator exports | Consume versioned public ballot/instrument records; own cross-source analytical links and evidence decisions |
| `datacenter-data-integration.1` | Older separate checkout | Historical comparison only until its lineage and intended use are explicitly established |
| Books and companion sites | Narrative, practical guides, public presentation | Consume pinned releases; do not become alternative canonical inventories |

Counts above describe files, not currently verified legal force. The original
clause-extraction cohort is older and smaller than the inventory; no new release
may present its percentages as statistics for the expanded universe.

Existing strengths to retain: structured decisions, explicit answer-file selection,
expected-prior-value conflict detection, idempotent apply, archived evidence,
normalization, typed dates, and generated public artifacts. Current comparison in
`apply_research.py` tolerates punctuation, case, and whitespace; document that
behavior and add source/revision fingerprints for stronger concurrency control.

The existing codebook excludes permanent bans from the moratorium inventory.
Preserve that meaning. Permanent restrictions and electoral observations need new
tables rather than a silent widening of the old denominator.

## 3. Design principles

1. Separate object identity, source assertions, review decisions, and public views.
2. An election outcome and legal effectiveness are separate facts.
3. A measure can have several provisions, sectors, thresholds, and resulting acts.
4. A rejected pro-development measure can constrain a project without enacting a ban.
5. An advisory result records sentiment; it does not establish an operative pause.
6. Record unsuccessful searches and unresolved identity/status explicitly.
7. Discovery relevance, quote verification, factual support, and legal acceptance are
   different gates; no model score substitutes for all four.
8. Source text and dates survive interpretation; later corrections supersede rather
   than erase history.
9. Use deterministic checks for identities, arithmetic, referential integrity, and
   dates; use model judgments only where interpretation is required.
10. Preserve concurrent work and keep changes within the dataset owner's boundary.

## 4. Expanded relational model

Use versioned JSON Schema for authoritative structured records, JSONL for nested
ledgers, and documented CSV projections for ordinary users. Start with file-based
canonical data, matching the repository's review workflow. A local evidence database
and derived DuckDB views support research and analysis; neither is a second authoring
authority for public facts. Final schemas and paths must be settled in phase P1.

### 4.1 Objects, grains, and identifiers

| Proposed table/ledger | Grain and key | Required information |
|---|---|---|
| `jurisdictions` | One government or electoral jurisdiction; `jurisdiction_id` | State, county, government type, authoritative identifiers where available, names/aliases, boundary references and validity dates |
| `elections` | One election administration event; `election_id` | Date, administering authority, election type, official result endpoints; distinguish town meeting from conventional ballot where applicable |
| `ballot_measures` | One question in one jurisdiction/election; `measure_id` | Election and jurisdiction IDs, official designation, exact wording, title, placement method, bindingness, lifecycle, sectors |
| `measure_provisions` | One substantive provision; `provision_id` | Mechanism, covered uses, thresholds, exemptions, geography, implementation requirements, evidence pointers |
| `measure_results` | One observed result version; `result_observation_id` | Measure ID, yes/no/other votes, denominators, source, observation time, reporting status, certification status |
| `local_restrictions` | One non-moratorium local legal instrument; `restriction_id` | Bans, approval requirements, zoning limits, development conditions; identity, provisions, status and temporal evidence |
| `instrument_events` | One supported instrument action/event; `event_id` | Instrument reference, action type, occurrence bounds, observation/publication times, assertions and decisions |
| `measure_instrument_links` | One reviewed measure-to-instrument relation; `link_id` | Relation, source and target IDs, provision scope, supporting claims and review status |
| `source_documents` | One immutable payload/text version; `source_document_id` | URL observations, body and text hashes, retrieval provenance, extraction version, access/publication classification |
| `claims` | One source-qualified assertion; `claim_id` | Subject, predicate, typed value/object, exact quote/span, document ID, temporal support, extraction provenance |
| `review_decisions` | One append-only decision; `decision_id` | Target assertion/link, accepted/rejected/unresolved, scope, reviewer/method, rationale, time, supersedes |
| `search_runs` / `search_attempts` / `search_sightings` | Runs, attempts, and hit appearances | Query cell, backend, wording, rank, time window, response provenance, errors, spend and retry outcomes |
| `coverage_observations` | One bounded research scope/run disposition | Jurisdiction, sector, period, intent, endpoints checked, completeness state and remaining gaps |

Continue existing `moratorium_id` and `policy_action_id` unchanged. Use tagged
instrument references so local moratoria, local restrictions, and state actions
cannot collide. New IDs must come from a deterministic registry/allocator with
collision checks; a language model may select an existing ID but never invent one.
Do not derive permanent identity solely from mutable wording or titles. Preserve
aliases and explicit merge/split mappings, including a reason and prior references.

Jurisdiction names alone are insufficient: distinguish town/city/township, county,
and overlapping electoral districts. General-election day is not a globally unique
election identity. Reused designations such as “Question 2” need jurisdiction and
election context. Repeated votes are distinct measures linked by a common campaign
or instrument history; one question covering several sectors remains one measure.

### 4.2 Ballot lifecycle, mechanisms, and polarity

Separate these dimensions rather than creating one overloaded `status`:

- Placement method: citizen initiative, citizen referendum, governing-body referral,
  town-meeting article, other, unknown. Retain source terminology and legal basis.
- Procedural lifecycle: petition announced, collecting signatures, submitted,
  qualified, scheduled, withdrawn, disqualified, litigated, voted, canceled, unknown.
- Result: approved, defeated, tied, pending, unknown; source-reported versus
  mechanically calculated outcome must be distinguishable.
- Certification: unofficial, certified, recount pending, amended certification,
  unknown. A complete precinct count is not certification.
- Bindingness: binding, advisory, mixed, unresolved; permit provision-level values.
- Mechanisms: temporary permitting pause, permanent prohibition, time-limited ban,
  size/resource limit, voter-approval requirement, financial guarantee, zoning
  change, rezoning reversal, development-agreement approval/reversal, financing/tax
  authorization, advisory support/opposition, other, unresolved.
- Yes-vote direction: restricts, facilitates, mixed, neutral/procedural, unresolved.
  Preserve exact wording and separately derive the observed direction of outcome.

For referendums, record whether yes upholds or repeals the challenged act. Do not
assume a yes vote means opposition to development. Mixed or generally applicable
zoning questions need explicit scope notes, not a forced binary political label.
Qualification failure is not electoral defeat. A projected result is not certified.

Record vote totals as nullable integers, source percentages separately from calculated
percentages, and denominator definitions. Distinguish valid question votes, ballots
cast, registered voters, turnout, undervotes/overvotes, and precinct reporting.
Apply the actual passage rule, including supermajorities if relevant. Keep every
result revision, publication/observation time, source hash, and supersession link.

### 4.3 Measure-to-instrument relationships

Allow many-to-many links with typed relations: `enacts`, `proposes`, `advises`,
`upholds`, `repeals`, `amends`, `conditions`, `requires_implementation`, and
`succeeds_prior_pause`. Review applicability at the provision level when needed.

Examples to support:

- A binding voter-adopted pause links to a moratorium instrument, reusing its ID if
  the same instrument is already present as pending. Do not add a second instrument
  merely because it now has an election result.
- An advisory moratorium vote has no operative instrument unless a subsequent
  governing-body adoption is independently documented.
- A charter ban replacing a council pause creates a restriction record and a
  replacement/history link. Preserve the older pause's actual lifecycle.
- A rejected rezoning or financing authorization records that disposition; do not
  infer a citywide ban or canceled project from it.
- Several questions affecting one campus remain separate measures; multiple projects
  affected by one act do not multiply its instrument count.

### 4.4 Time, duration, geography, and thresholds

Represent uncertain dates with earliest/latest bounds, precision, original text,
and evidence. Use documented half-open intervals internally, preserving operative
“through”/inclusive wording and conversion rules. Keep election, adoption,
certification, effective date, retroactive applicability, publication, expiration,
extension, source retrieval, and review times separate. Retain local timezone when
timestamps matter; do not fabricate a midnight timestamp for a date-only source.

Keep original duration and units. Calendar months/years must not be silently
converted to 30/365-day terms. Migrate legacy `duration_days` semantics with an
explicit compatibility note; compute expiry only from the legal anchor and supported
calendar arithmetic. Event-based endings and disputed intervals remain explicit.

Wells is a pilot edge case: the November 3 warrant describes effectiveness upon
enactment but 180 days from June 16 applicability. Do not calculate its term from
election day. Verify adopted text and later actions before publishing current force.

Threshold records need operator, value, unit, measurement basis, aggregation rule,
and scope. Distinguish peak demand, IT load, connected capacity, daily water use,
floor area, impervious area, and contiguous acreage. Do not repair unusual source
units by guessing. Exemptions, pending applications, vested rights, accessory uses,
and grandfathering must be first-class provisions or explicit unresolved fields.

Jurisdiction centroids are not project parcels or proof of legal coverage. Keep
candidate spatial joins separate from reviewed project-instrument applicability.
Use the integration repository's project identities and exposure-review contracts.

## 5. Library capability map and integration boundaries

Inspected source root: `~/projects/bc/bc-modules`. Pin its Git revision and relevant
package/dependency versions in every run; version strings alone do not identify
local changes. The following APIs exist locally, but the project adapters below
are proposed and require contract tests before deployment.

| Component | Reuse | Application responsibility |
|---|---|---|
| `bc-spec` | `Space`, dimensions/values, closed-table selection, calendar intervals, pruning, seeded sampling, checks and estimates | Jurisdiction/sector/mechanism registry, sparse worklist, acceptance rubric |
| `bc-web` | `Searcher`, `SearchQuery`, `search_many`, `search_all`, Exa, SerpAPI, Google News RSS, GDELT, `Retriever`, bounded collection, cache/recrawl | Source profiles, query policy, storage routing, rights flags, response retention |
| `bc-research` | `ResearchContext`, `ResearchSearch` tiers, plans, intent queries, host discovery, time walks, feedback/relaxation, reference chase, coverage rounds, `deep_research` | Legal/electoral relevance rules, stopping rules, escalation priority, review queues |
| `bc-evidence` | Search cells and plans, collection, full-document extraction, `EvidenceDB`, instrument/entity candidates, events, packs, selection and support audits | Domain schema adapter, source-quality review, legal adjudication and deterministic promotion |
| `bc-content` | Payload parsing, chunking, temporal checks and text/NLP primitives | PDF/table quality gates, OCR provenance, typed vote/threshold extraction |
| `bc-store` | Content-addressed observations, `store_fetch`, search response sinks and ledgers | Map existing archives to observations without dropping hashes or access classification |
| `bc-core` | Budget/rate primitives, bounded execution and rank fusion | Whole-run budgets, interruption policy, manifests and explicit unpriced-call handling |
| `bc-llm` | Configured model roles, validated transports, pricing and cached model outputs | Pinned role/model/effort settings, calibration and per-stage accounting |
| `bc-lawid` | Official legal identifier parsing where supported | Check applicability to local instruments; retain unsupported local IDs verbatim |
| `bc-collect` | Collection lifecycle and restore/replay contracts when a durable collection is adopted | Scope-specific adapter and receipts; avoid creating a competing crawler |
| `bc-report` | Optional evidence-backed PDF briefing generation | Public Markdown/CSV remain sufficient; no dependency required for initial release |

Read the current implementation, not only library README examples. In particular:

- `ResearchSearch` read triage can inspect head/tail excerpts; it is a relevance
  filter, not proof that the entire ordinance was legally reviewed.
- `bc-evidence` extraction processes every document chunk and validates located
  quotes and date support. Explicit ceilings and failed chunks must be disclosed;
  a verified quotation still does not establish legal effect or correct identity.
- A document's text identity and its original payload hash are different. Preserve
  URL/retrieval observations even when equivalent text is deduplicated.
- Library instrument/entity resolution and event near-duplicate folding nominate
  candidates. They must not silently merge numbered acts, extensions, election
  questions, or governments that share names.
- NLI, similarity, source counts, salience weights, and published library evaluation
  scores are not calibrated legal acceptance criteria for this dataset.
- Forecast/scenario modules are outside this implementation's acceptance workflow.
  Predictions must never populate observed results or current legal status.

## 6. Search strategy

### 6.1 Three coordinated lanes

**Inventory refresh:** use existing IDs and worklist buckets for overdue expiry,
unverified facts, stale proposals, extensions, replacements, and litigation.

**Election census:** discover measures independently of the old inventory, including
qualification failures and measures favoring development. Seek ballot text, petition/
referral records, sample ballots, official returns, canvass/certification, adopted
text and implementation. Track later elections without assuming November is complete.

**Gap discovery:** systematic state/sector/time coverage plus nearby-government and
project-linked leads. Register negative findings with bounded search scope; never
equate zero indexed hits with absence of an instrument or a complete statewide census.

### 6.2 Sparse typed search space

Build a reviewed jurisdiction registry with aliases, official government/election
hosts, portal vendors, state/county context, and source-discovery status. Use closed
IDs from it and from the existing inventories. Represent tasks by jurisdiction,
sector, period, mechanism, intent, and known object ID where applicable.

Do not expand the full Cartesian product across every local government. Prioritize
known IDs, identified ballots, stale records, event deadlines, project hotspots and
documented gaps, then allocate a stratified exploratory sample. A month/state sweep
and a jurisdiction census are different coverage claims. Record search-space version,
sampling seed, exclusions, estimated calls, and unresolved dimensions.

### 6.3 Provider-specific queries and rank fusion

Use `Searcher.search_many` with named variants rather than sending identical prose
to every backend. Exa receives semantic descriptions; Google receives exact phrases,
aliases, official designations, boolean combinations and domain filters.

Use native domain controls where supported: `research_client.py search ...
--backend exa --domain <verified-host>` sends Exa `includeDomains`, rather than
assuming that Google-style operators constrain semantic retrieval. SerpAPI's
`include_domains` compiles to site operators. Retain the intended domains and
diagnose returned URL hosts for both. An empty or out-of-scope response does not
establish absence; repair deficient searches before accepting negative coverage.
Obtain hosts and records-platform links from retained official sources rather
than guessing municipal domains. Follow actual archive, attachment and pagination
links to original records; a stale informational page may lag a later ordinance.

Illustrative query families, to be rendered from registry values:

| Intent | Examples |
|---|---|
| Discovery | `"<place>" ("data center" OR "data centre" OR hyperscale) (ballot OR referendum OR initiative OR "town meeting")` |
| Primary text | `site:<official-host> "<measure designation>" (warrant OR ordinance OR charter OR "ballot language")` |
| Results | `site:<election-host> "<place>" "2026" (canvass OR certified OR "statement of votes" OR results)` |
| Lifecycle | `"<instrument number>" (extension OR repeal OR replacement OR injunction OR expiration)` |
| Substantive gaps | `"<place>" ("25 megawatts" OR "voter approval" OR "industrial development")` |
| Reverse polarity | `"<place>" ("permit data centers" OR "allow data centers" OR "uphold rezoning")` |
| Other sectors | `"<place>" ("battery energy storage" OR BESS OR solar OR wind OR "cryptocurrency mining") (moratorium OR ballot)` |

Add local naming variants, parcel/site names, project aliases, petition sponsors,
election dates, official numbers, and exact quoted passages learned from sources.
Search questions whose wording never says “data center,” including general zoning,
industrial review, bonds, tax incentives, and resource thresholds.

Fuse by reciprocal rank and retain backend/variant ranks and every original sighting.
Search-engine agreement is retrieval support, not independent factual corroboration.
Report marginal contribution by backend and query family; do not discard uniquely
retrieved official sources merely because no other provider indexed them.

### 6.4 News, time walks, primary discovery, and chasing

- Use keyless Google News RSS/GDELT for broad news leads, with paid Google News
  escalation where it adds measured recall. Retain clusters and original publishers.
- Treat GDELT's index-window decline separately from an empty completed search;
  use archived primary sources and general web search for older periods.
- Use explicit publication windows for recent news and `TimeWalk`/`run_walk` for
  historical cells. Publication filtering is not filtering by legal event date.
  Preserve undated primary pages and run an unfiltered recovery query for them.
- Discover actual election/municipal hosts, including vendor/CDN result endpoints.
  `SourceDiscovery` can help locate endpoints with retained conversations and quotes;
  endpoint discovery does not establish corpus completeness.
- Chase named ordinances, petition certifications, council referrals, warrant
  appendices, court orders, and canvass reports using exact phrase/identifier search.
- Use feedback vocabulary, alternate angles and bounded relaxation for empty or
  low-quality cells; preserve the original question and reasons for relaxation.
- Use `ResearchSearch` search → ensemble → triage → read selectively; a known
  authoritative URL may bypass relevance triage but never provenance/review gates.
- Use `deep_research` for bounded difficult cases rather than making it the default
  per-record workflow. Record skipped stages, unextracted documents and chase gaps.

## 7. Collection, extraction, and evidence

### 7.1 Collection and retention

Fetch HTTP first, then use configured browser escalation for JS result portals and
agenda systems. Retain response status, final URL/redirect chain, engine, retrieval
time, raw payload hash, parser version, extracted text hash, and source observation
ID. Preserve search response bodies through the library's response sink, after
credential redaction; retain failed attempts as well as successful responses.

Use bounded `CrawlSpec` scopes with explicit page/depth/byte/time limits and allowed
document/resource hosts. Government query parameters may identify a document; remove
tracking parameters without collapsing distinct resources. HTML success with a login,
challenge, or empty app shell is not document acquisition.

For delayed JavaScript portals, use explicit headful pydoll mode with bounded
settling or a known rendered selector (`research_client.py fetch ... --mode browser
--settle-ms 5000`, optionally `--wait-for-selector`). Record those controls and
inspect substantive content before following the actual attachment links. A second
attempt with diagnosed rendering controls is an explicit recovery, not an automatic
retry. Preserve the initial shell/failed result and its consumed reservation.

Some public portals issue transient signed download links. Retain the exact private
retrieval URL and response bytes privately, while public provenance uses the unsigned
resource identifier, a hash of the retrieval URL, and the stable public portal and
document label needed to refresh access. Do not publish transient download capabilities
or present an unsigned identifier as necessarily anonymously retrievable.

For PDF/image returns, preserve page count, page numbers, OCR engine/version and
text confidence. Inspect tables and headers; visual checking is necessary when OCR
or extraction cannot reliably associate vote columns with the right question. Do not
derive complete results from search snippets or detached table fragments.

Keep public-record text publishable under the existing classification policy; keep
news text and restricted material private as appropriate. Public provenance may
include permissible quotations, metadata, URLs and hashes. Search provider payloads,
screenshots and extracted text inherit their own access decisions, not automatically
the source page's classification. Reuse `classify_sources.py` and extend it rather
than bypassing it with a new archive tree.

Map `work/sources/<ST>/` manifests into store observations with a migration receipt.
Keep legacy URLs/hashes resolvable. Durable collections/backups belong on admitted
mounted `/data0` storage per bc-modules' storage policy; active SQLite/WAL state must
use admitted local NVMe, never NFS. Resolve actual paths and preflight storage before
bulk writes. Do not replace compatibility symlinks.

### 7.2 Extraction and assertion review

Extract once per unique document text with all relevant cells attached. Process full
documents with bounded chunk concurrency; preserve chunk coverage, overlap dedup,
failures and retries. A partially processed document cannot be marked complete.
Split vote totals, ballot meaning, bindingness, thresholds, dates and legal effect
into separately reviewable claims; one supporting quote rarely establishes all.

For each candidate assertion:

1. Locate the quote in versioned source text and retain offsets/page anchors.
2. Check date/value support and retain original wording and units.
3. Confirm exact jurisdiction, election, question and instrument identity.
4. Classify source authority and scope: official return, operative text, agenda,
   staff summary, news, advocacy, aggregation, or unresolved.
5. Seek contradictions and independent support, grouping syndicated/reposted text
   and common upstream result feeds so repetition is not counted as independence.
6. Record a scoped accepted, rejected, or unresolved review decision. Mechanically
   verified quotations remain candidates until substantive review is satisfied.

Official texts settle wording; election authorities settle certification; subsequent
acts and court orders settle later changes within their scope. Official summaries
can still omit exemptions or use the wrong date anchor. Conflicts require explicit
adjudication, not majority voting over sources. An NLI alert is a review lead.

Do not publish model-generated `bc-evidence` instrument profiles or deterministic
timeline merges directly as canonical records. Adapt them to domain candidates,
validate, then apply reviewed decisions through this project's existing pattern.

## 8. Run control, costs, caching, and refresh

Each run manifest records purpose, as-of/evidence cutoff, input file hashes and Git
revisions, schema/query/prompt versions, model roles and settings, cache identity,
provider configurations, stage limits, routing context, start/end and completeness.
Never include API keys, proxy credentials, or unredacted authenticated URLs.

Use one whole-run `BudgetMeter` across search, query generation, triage, extraction,
review and drafting, with per-stage call/token/USD ceilings. Record known charges,
estimates and unknown prices separately. SerpAPI returned an unpriced warning during
the November 5 review; configure the actual plan rate before budgeted batch work.
Do not treat unpriced calls as free or claim the dollar cap covers them without an
explicit conservative reservation policy. Browser/OCR/storage limits also need caps.

Before expensive work: deterministic dry-run → stratified pilot → inspect calibration
and spend → explicitly authorize a stated batch size/model/effort/budget. Authorization
to write this plan is not authorization to launch the batch. No parallel agents or
new scheduled tasks are required by this plan.

Reuse content, search and model caches with fingerprints covering document text,
schema, prompt, model and settings. Pin result versions during adjudication. Result
pages require fresh observations even if the URL is unchanged; never let a cached
election-night result masquerade as a current certified return. Resume from explicit
completed stages and failed work queues, not the newest file by modification time.

Use source/public-IP pacing, Retry-After, bounded retries and provider quotas.
If multi-host execution is later approved, use the supported coordinator and verified
egress configuration rather than sharing a SQLite scheduler over NFS. A backend
failure is incomplete search coverage, not a negative finding. Keep acquisition,
parsing, extraction, review and publication completeness independently visible.

Proposed refresh priorities, to configure later rather than schedule now:

| State | Refresh trigger |
|---|---|
| Petition/qualification | Official deadlines, referral meetings, litigation events |
| Scheduled election | Ballot/warrant publication and amendments |
| Unofficial results | Source-aware polling during counting with strict rate caps |
| Certification/recount | Published canvass dates and amended returns |
| Approved binding measure | Effective/publication requirements and implementation |
| Advisory measure | Subsequent governing-body agendas and adopted acts |
| Active pause | Before supported expiry and after relevant meetings |
| Stable historical record | Adaptive recrawl plus known correction/repeal triggers |

Conditional requests/recrawl can reduce unnecessary transfer. Retain observation
history and previous hashes; a 304 without an available archived body cannot supply
new quote proof. Distinguish an unchanged source from an unchanged legal situation.

## 9. Review, promotion, and publication

Implement proposed adapters under `scripts/` with explicit CLI inputs and dry-run
modes. Suggested responsibilities: plan search, execute cells, collect sources,
extract domain candidates, build review packets, validate decisions, apply ballot
decisions, and build public exports. These are proposed interfaces, not existing
commands. Keep reusable retrieval/NLP changes in bc-modules only when necessary.

Extend structured decisions with target IDs, expected source-record hash/revision,
field changes, evidence claim IDs, review scope and supersession. Validate the full
batch before writing. Use atomic writes or a recoverable staged transaction across
related ledgers; never leave an applied result without its required referenced object.
Reapplying the same decision must be a no-op; conflicting stale decisions fail loudly.
Record exact changed fields and before/after values, including explicit nulls.

Update public generators, state pages, GeoJSON, tables and documentation from typed
views. Add distinct views for moratoria, restrictions and ballot measures; display
result direction, bindingness, certification, source date and review caveats.

Publish separate denominators for:

- Measures, distinct electoral jurisdictions and elections.
- Measures scheduled for a specific date versus the whole calendar year.
- Qualified/voted/certified measures and pending/failed-qualification proposals.
- Binding versus advisory, mechanism categories, and multi-sector membership.
- Temporary moratoria versus permanent restrictions and other conditions.
- Approved/defeated votes versus derived restrict/facilitate/mixed outcomes.
- Legal instruments currently supported as in force versus historically adopted.

Label overlapping categories as non-additive. No “anti-data-center wins” total should
silently include general zoning questions, recalls, earlier elections, or uncalled
results. Reconcile 41/44/45-measure news tallies through a record-level set difference,
not by selecting the largest or most repeated headline.

Generate a release manifest with schemas, counts, cutoff dates, hashes, exclusions,
unresolved queues and provenance. Export stable join keys and explicit relationship
tables to the integration repository; do not flatten measures × instruments ×
projects × issuers into a single misleading count. Any RDF/JSON-LD adapter should
extend that repository's existing temporal/assertion ontology after semantic review,
not create a competing ontology here. Analytical/collaborator tables must label
proximity exposure separately from legally reviewed applicability.

### 9.1 Full refresh scope and freshness accounting

Before execution, freeze a release scope matrix naming each dataset, repository,
owner, research cutoff, baseline snapshot, intended output, validation command and
delivery state. Use one release ID across the matrix, with separate source-specific
cutoffs where collection cannot reach that date. Set the actual cutoff at execution
time; November 5 is this plan's date, not an indefinitely reusable freshness claim.

The required core scope is:

- Revisit every existing local inventory ID, not just currently flagged worklist
  rows. Assign a researched disposition: confirmed, corrected, superseded/duplicate,
  or unresolved with attempts and last-supported observation date. Prioritize overdue
  cases, but do not confuse priority selection with a full-inventory refresh.
- Revisit every state-policy ID for legislative disposition, enactment, veto,
  effective dates, amendments, executive/utility actions, preemption and litigation
  as applicable. Search for new actions across all 50 states and all existing sectors.
- Search for newly adopted or proposed local instruments across all 50 states and
  sectors, alongside the distinct election census. Record the actual search method
  and jurisdiction coverage; a 50-state search is not a census of every municipality.
- Reconcile every ballot seed through the cutoff and record pending future elections,
  without presenting an unofficial result as certification or a future vote as decided.
- Reconcile cross-dataset identities and predecessor/successor links. Historical
  releases remain intact; reviewed corrections must have an explicit change ledger.

Publish the freshness funnel: total records, attempted, successfully checked,
changed, confirmed unchanged, unresolved, not attempted, and source-unavailable.
Keep these categories disjoint where summed and define their denominators. An
unresolved older record retains its earlier supported status date; merely searching
for it does not make its legal status current. List exceptions in the release notes.

Sibling projects require explicit dispositions in the same matrix. Refresh the
project facts used by newly updated prose through the canonical Server Country
workflow, and identify whether the full 1,048-project inventory is in the batch or
only a declared subset. Rebuild affected integration links and collaborator summaries
from pinned inputs, preserving that project's review gates. An independently scoped
full project/disclosure corpus refresh is not silently implied by updating the
moratorium inventory: either include and budget it explicitly or retain its own
dated snapshot and disclose that limit. No required consumer may silently disappear
from scope; record delivered, intentionally historical, or blocked with the reason.

### 9.2 Prose, copy, summaries, and publication dependency matrix

Inventory all number-bearing and substantive claims, not only headline counters.
Search for old totals, percentages, dates, sector shares, rankings, coverage claims,
“currently,” “latest,” release labels, example outputs, titles and descriptions.
Numeric replacement alone cannot explain the new electoral mechanisms or changed
legal outcomes. Classify each surface as generated, manually reviewed current copy,
or intentionally historical with an explicit date/version label.

| Surface | Required update or explicit historical disposition |
|---|---|
| `data/summary_stats.json`, CSV/JSON downloads and new ballot/restriction exports | Recompute from reviewed records; expose definitions, cutoffs and separate denominators |
| `README.md`, `data/README.md`, `scripts/README.md`, `work/README.md` | Update scope, counts, repository diagrams, examples, commands and workflow descriptions |
| `docs/codebook.md`, methodology, FAQ and known gaps | Explain electoral versus legal objects, bindingness, result certification, units, coverage and unresolved facts |
| `states/README.md` and each state page | Reconcile totals and narrative descriptions, including formerly empty states and new restrictions |
| Root `index.html`, generated `site/`, timeline and GeoJSON | Update cards, narrative sections, legends, labels, filters, tooltips and download links |
| Figures and LaTeX tables | Regenerate with dated captions and correct population/cohort labels; retire unsupported stale graphics |
| `CHANGELOG.md`, `CITATION.cff` and release manifest | Record version/date, material changes, corrections, schema compatibility, freshness and remaining gaps |
| Bundled paper PDF and `moratorium-paper` | Sync the canonical mirror, update affected body/abstract/conclusion/appendices and rebuild; otherwise retain the old edition conspicuously dated and do not claim paper-data alignment |
| `datacenter-paper-2026` and integration exports/memos | Reconcile affected claims, legal/project bridges, summaries and collaborator packets; retain distinct corpus cutoffs |
| `servercountry.org`, `fightadatacenter.com`, book/manuscript and author-site references | Find affected current copy and reconcile against canonical facts; preserve published historical editions and log any deliberately deferred updates |
| GitHub release title/body/assets and hosted landing page | Present the same version, counts, scope, certification caveats and working downloads as the pinned release |

Create a claim-to-output checklist with source/view and reviewer for each manual
summary. Check both arithmetic and interpretation: electoral outcomes are not new
moratorium counts; a time-limited prohibition is not automatically permanent;
restrictions favoring opponents are not automatically project cancellations.
Review broad “complete coverage” and causal claims explicitly. Do not globally
replace numbers in historical changelog entries, source quotations or older editions.

The existing `check_docs_numbers.py` covers selected files and numbers, not the full
matrix. Extend coverage or add a release-copy audit for every current surface, then
inspect rendered landing/state pages and representative charts/tables. Require a
documented disposition for every surface before marking the release complete.

### 9.3 GitHub release and remote verification

Treat a Git push, a tag, a GitHub Release, its attached assets and a Pages deployment
as separate deliverables. Local tags and prose describing a release are not proof
that the remote release exists or serves the intended bytes.

1. Inspect remote branch, tags, GitHub release list and existing asset conventions
   read-only at execution time. Resolve discrepancies with README/CITATION claims;
   do not infer remote state from the local tag list or invent a version/DOI.
2. Select the next version according to verified repository conventions and schema
   compatibility. Update citation metadata and prepare release notes from the actual
   reviewed change ledger, including comparison to the previous published release.
3. Build from pinned inputs and run validation, `make check`, generated-artifact
   consistency checks and expanded ballot/copy gates. Run `make all` where appropriate;
   inspect any generated changes and verify a repeat build produces no new diff.
4. Prepare an explicit asset manifest: reviewed inventory/state-policy/ballot/result/
   restriction/link data, codebook/schemas, summary statistics, checksums, coverage/
   freshness/gap report, and updated paper or clearly dated historical-paper pointer.
   Respect existing licensing and asset conventions; do not attach private evidence.
5. Stage only owned changes, commit them, and prepare the exact tag/target commit,
   release title/body and asset set for review. Use a temporary file for multiline
   release text if publishing with `gh`; avoid shell interpolation of prose.
6. Under applicable publication authorization, push the intended commit and immutable
   tag, create/publish the GitHub Release against that tag and upload the listed
   assets. Existing tags/releases must not be silently overwritten. If authorization
   remains outstanding, leave the concrete release ready and report it as pending;
   do not describe preparation as publication.
7. Query remote refs and release metadata, confirming tag target, published/draft
   status, title, body, asset names and sizes. Download every release asset into a
   clean temporary location, compare checksums and parse representative tables.
8. Verify the public landing page/Pages deployment after publication: version, key
   totals, source cutoffs, working links, paper edition and downloadable bytes. Keep
   the GitHub-release and site-deployment results separate if one succeeds first.
9. Verify required sibling updates at their intended branch/deployment or deliver
   an explicit pending/blocked disposition. Finish with a release receipt linking
   the public release, tag/commit, asset checksums, deployed page, validation evidence
   and remaining freshness limits. Release completion requires remote verification.

This planning turn does not execute these publication steps. During implementation,
continue within the user's established authorization; do not invent a second approval
gate if publishing has already been authorized.

## 10. Migration and compatibility

1. Freeze current files, hashes, derived counts and source identities as a baseline.
2. Introduce additive schemas/ledgers with unchanged legacy CSV contracts.
3. Backfill jurisdiction mappings and source observations, retaining unresolved IDs.
4. Import ballot leads as candidates; do not convert news lists into accepted facts.
5. Review links to existing pending/active/replaced instruments before adding rows.
6. Represent bans in the new restriction table, including replacements previously
   mentioned only in `outcome`; do not rewrite history from present-day status.
7. Add temporal/unit fields and compatibility exports; document old day-conversion
   assumptions before replacing any duration calculation.
8. Run old and new summaries side by side. Every legacy count change needs a
   reviewed, row-level explanation rather than an unexplained migration delta.
9. Update documentation and consumers, then publish a versioned additive release.
10. Keep a tested rollback to pinned source files and a replay of accepted decisions.

The inventory remains authoritative for legacy moratorium fields during migration;
new ledgers are authoritative only for their declared new fields. If instrument
authority later moves into an event ledger, make that a separate versioned migration
with one explicit writer and generated legacy CSVs. Avoid dual write authority.

## 11. Pilot, calibration, and meaningful validation

Create a dated, source-backed fixture set with these cases:

- Peru: binding voter-adopted temporary pause.
- Wells: retroactive applicability, non-election duration anchor, area definition.
- Bloomington: advisory moratorium support without automatic legal adoption.
- Piqua: charter prohibition and possible predecessor pause.
- Grove City: general development thresholds and voter-approval requirements.
- Harwood: defeated extra-review requirement; no inferred project permit.
- Wilmington: several rezoning questions in one jurisdiction and project context.
- El Dorado: data-center and battery-storage scope and duration interpretation.
- One earlier-2026 election and one December pending measure, kept out of November totals.
- A failed qualification, an amended certification/recount, and a mixed-polarity
  measure, using real examples if available and labeled synthetic fixtures otherwise.
- A council-only adoption/extension and an inaccessible official portal.

Use reviewed official records where available; source availability is itself a
pilot result. Hold out cases from prompt tuning. Measure discovery recall against a
reviewed bounded list, false exclusion rate, primary-source recovery, correct quote
localization, jurisdiction identity, polarity, certification, date anchors, units,
dedup errors and cost per review-ready record. Record reviewer disagreement.

Required regression checks are behavioral:

- No advisory vote creates an active moratorium automatically.
- No defeated pro-development question creates a citywide ban automatically.
- No date-only result invents certification or legal effectiveness.
- No same-name jurisdiction or same-day act is merged without identity evidence.
- Vote totals/percentages/pass thresholds reconcile, with missing values preserved.
- Chronology permits evidenced retroactivity and flags unexplained contradictions.
- A changed source URL body creates a new observation; old claims still resolve.
- Multi-question/multi-sector instruments do not inflate incompatible denominators.
- Interrupted extraction remains incomplete; resume avoids duplicate accepted facts.
- Dry-run is read-only, stale decisions conflict, apply is atomic and idempotent.
- Legacy exports remain stable except for individually reviewed corrections.
- Public outputs contain no private source bodies, credentials or restricted payloads.
- A clean restore/rebuild verifies hashes and reproduces deterministic exports.

Do not hard-code library benchmark scores as acceptance thresholds. Set pilot
thresholds before the full run, prioritize zero silent high-impact legal/polarity
errors, and leave unresolved cases explicit when review cannot settle them.

## 12. Implementation phases and exit criteria

| Phase | Deliverable | Exit criterion |
|---|---|---|
| P0 Baseline | Source/owner map, version pins, archival and count snapshot | Reproducible current-state manifest; unrelated work preserved |
| P1 Contracts | Schemas, vocabularies, IDs, temporal rules and sample records | Pilot cases representable without changing legacy meaning |
| P2 Search adapters | Typed sparse plans, multi-provider searches and provenance | Dry-run cost preview; backend failures and unpriced calls handled explicitly |
| P3 Evidence/review | Archive mapping, extraction adapter, decision schemas and gates | Every accepted pilot assertion resolves to reviewed source evidence |
| P4 Pilot | Reviewed cases, holdout results, spend and disagreement report | Documented quality/cost gate and explicit bounded-batch authorization |
| P5 Collection | Full local/state-policy refresh, new discovery, November census reconciliation, earlier/December queues | Every existing ID and seed has a disposition; source-specific freshness and gaps are visible |
| P6 Release | Updated data, prose/copy/summaries, paper/consumer dispositions, published GitHub release and site | Checks pass; remote tag, release assets and required deployments verified against the manifest |
| P7 Maintenance | Due-work rules, adaptive recrawl, correction workflow | Manually exercised refresh cycle; scheduling only if separately requested |

Dependencies: P1 follows P0; P2/P3 use P1 contracts; P4 requires P2/P3;
P5 requires the pilot gate; P6 requires reviewed collection and migration checks;
P7 uses the released contracts. These are phases, not a promise of calendar dates.

## 13. Reference material and evidence status

Local implementation references inspected for this plan:

- This repository: `Makefile`, `docs/codebook.md`, `scripts/README.md`,
  `work/README.md`, `scripts/apply_research.py`, `scripts/save_source.py`,
  `scripts/gate_answer.sh`.
- `bc-modules/bc-web`: `python/bc_web/search.py`, `settings.py`,
  `docs/SEARCH.md`, `COLLECT.md`, `EXTRACTION.md`, `RECRAWL.md`,
  `DURABLE-SCHEDULING.md`.
- `bc-modules/bc-research`: `README.md`, `python/bc_research/__init__.py`.
- `bc-modules/bc-evidence`: `docs/DESIGN.md`, `docs/SELECTION.md`,
  `python/bc_evidence/search.py`, `collect.py`, `extract.py`, `db.py`.
- `bc-modules/bc-spec/README.md` and workspace `AGENTS.md` storage guidance.
- Integration repository: merge design, semantic-ledger documentation, September 30
  candidate-release report and October 12 disclosure build/report contracts reviewed
  in the preceding project review.

November 5 discovery starting points, not an accepted canonical import:

- [Ballotpedia: 2026 data-center measures](https://ballotpedia.org/Data_center-related_ballot_measures,_2026).
- [Duane Morris: election roundup and measure categories](https://statecapitallobbyist.com/artificial-intelligence-ai/data-centers/data-centers-on-the-ballot-where-things-stand/).
- [Redbud: Data Centers on the Ballot](https://datacentersontheballot.com/).
- [Wells: official November 3 warrant](https://wellstown.org/DocumentCenter/View/8514/November-3-2026-Special-Town-Meeting-Warrant?bidId=).
- [Wells: published election results](https://www.wellstown.org/DocumentCenter/View/8559/November-3-2026-Official-Election-Results?bidId=).
- [Hayward: October moratorium announcement](https://www.hayward-ca.gov/discover/news/oct26/hayward-city-council-enacts-immediate-moratorium-new-data-centers).

Archive and reverify these at implementation time. This plan records the research
design and known edge cases, not a certification of every electoral or legal fact.
