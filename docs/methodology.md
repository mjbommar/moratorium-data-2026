# Methodology

How this dataset was built, in plain English.

## What we set out to do

Every U.S. local government has the legal authority to pause new development of certain kinds for a defined period. When a city council, county commission, or township board uses that authority, they typically do it through a public ordinance or resolution that is published online (sometimes), posted in a meeting agenda (often), and recorded in board minutes (almost always, eventually).

Our goal: **identify every such moratorium adopted in the U.S. that targets data centers, battery storage, solar, wind, or cryptocurrency mining** — and capture enough structured information about each one to support cross-jurisdictional comparison.

## How we did it

Three phases.

### Phase 1: Document collection

We deployed AI-assisted research agents (built on the OpenAI Codex CLI with web-search enabled) across all 50 states. Each agent operated within a single state's scope and was given a research brief for that state.

The agents searched:

- Municipal websites
- Agenda portals (Granicus, CivicEngage, Legistar, IQM2, CivicWeb, CivicClerk, etc.)
- County board meeting minutes
- Planning commission and zoning board records
- State legislative databases (LegiScan, official state legislatures)
- News archives (local TV, regional papers, trade press)
- Academic and policy research (UNC SOG, MSU Extension, NREL, EIA)
- Court records (where applicable)

Each agent was instructed to download original documents — PDFs of ordinances, HTML of agenda pages, Word documents — and save them locally with provenance metadata (source URL, download timestamp, retrieval method).

We supplemented this with a SerpAPI sweep for `"<state>" "data center" moratorium` and similar queries, which surfaced documents the per-state agents had missed.

**Output of Phase 1:** approximately 4,400 unique source documents, totaling ~12 GB, archived in their native formats. Each has a `.meta` sidecar JSON file recording its provenance.

### Phase 2: Classification

Not every document we collected is a moratorium document. Many are project announcements, EIA reports, news articles unrelated to any specific ordinance. We classified each document with a small language model (gpt-5.4-mini at the OpenAI flex tier) using structured prompts that produced JSON-valid classifications:

- `document_type`: `ordinance`, `resolution`, `agenda`, `minutes`, `news`, `report`, `policy_document`, etc.
- `subject_matter`: `data_center`, `cryptocurrency`, `bess`, `solar`, `wind`, `general_zoning`, etc.
- `jurisdiction`: name + state of the issuing body
- `is_primary_legal_source`: whether the document is the operative instrument itself (vs. coverage of it)
- `is_moratorium_related`: yes/no
- `confidence`: 0.0 to 1.0

**Output of Phase 2:** 709 documents classified as moratorium-related across the corpus. About 1,123 of the 4,400 are primary legal sources of one kind or another.

### Phase 3: Structured extraction

For each moratorium-related document, we used a larger language model (gpt-5.5 at the OpenAI flex tier) with a detailed extraction schema to produce a structured record.

The extraction schema captures **60+ fields per document**, organized into five tiers that mirror the 44-clause taxonomy used in the working paper:

- **Tier 1: Universal clauses (14 coded fields).** Authority statement, findings (regulatory gap, threat enumeration, study intent, emergency declaration), definitions, prohibited actions, geographic scope, duration, exemptions, severability, effective date, repeal language.
- **Tier 2: Common clauses (10 boolean fields).** Extension mechanism, conflict-and-repeal, emergency declaration, open-meetings compliance, tolling, waiver provision, appeal process, vested-rights disclaimer, pending-application coverage, severability separately.
- **Tier 3: Sector-specific clauses (12 boolean fields).** Water-resource assessment, grid/energy-impact assessment, incentive guardrails, noise/generator provisions, fire-safety requirements, decommissioning bond, hazmat training, safety-incident trigger, farmland preservation, property-value guarantee, physical-hazard assessment, aviation clearance.
- **Tier 4: Definitional approach.** Whether the moratorium provides no definition, a functional definition, a bundled definition, or a size-threshold definition of the regulated use.
- **Tier 5: Quality metadata.** Confidence score, narrative summary, error flags, structural quality score.

Each extraction received a confidence score from the language model. We retained extractions with confidence ≥ 0.4 for downstream analysis. The cohort is **n = 348**, with mean confidence 0.72 and range 0.40 to 0.95.

**Output of Phase 3:** the JSONL file at [`data/structured_extractions.jsonl`](../data/structured_extractions.jsonl).

### Manual review and cleaning

We manually reviewed every extraction record to:

- Verify jurisdiction names and state codes
- Flag edge cases (regulatory ordinances mischaracterized as moratoria, rejected proposals, withdrawn projects, etc.)
- Resolve `[VERIFY]` flags by re-checking primary sources via real-Chrome browser sessions
- Add moratoria identified through news coverage but missed by automated extraction

As of the 2026-09-23 working snapshot the cleaned inventory has **1291 instruments across 47 states** (`data/moratorium_inventory.csv`). It held 222 at v2026.04.4; see Phase 5 below for how the refresh cycle works.

### Phase 4: Geocoding (added v2026.04.2)

Each row in the cleaned inventory was assigned WGS84 latitude and longitude coordinates representing the jurisdiction's centroid. Two-tiered approach:

1. **Primary geocoder: OSM Nominatim.** Free, open-source, with reasonable U.S. administrative boundary coverage. Rate-limited to 1 request/second per the public API usage policy.
2. **Fallback: U.S. Census Geocoder.** Used when Nominatim returns no result. The Census Geocoder is authoritative for U.S. jurisdictions but works best for street addresses; for "Jurisdiction, State" queries we found Nominatim more reliable.

Of 1291 rows, 1289 (99.6%) are successfully geocoded. The 2 blanks are aggregate meta-rows (`Other Reported Local Moratoria, Michigan` and `Proposed or Rejected Local Pauses, Maryland`) that aren't real geographic points.

After geocoding, a triple-check audit ran 89 verifications across three independent methods:

1. **Random sampling against geographic knowledge** (24 rows): manually verify each coordinate matches a well-known location.
2. **Wikipedia GeoSearch reverse-lookup** (50 rows): query Wikipedia for pages within 10 km of our coordinates; verify the jurisdiction name appears among them.
3. **Targeted high-risk subset** (15 rows): the 4 manual within-state-ambiguity fixes plus other generic township names where ambiguity is most likely.

Across all 89 verifications, **zero confirmed wrong geocodes** (after the 4 manual Ohio corrections in v2026.04.2). The audit caught and corrected:

- Lake Township, OH (geocoder picked Logan County → corrected to Wood County)
- Plain Township, OH (Franklin County → Stark County)
- Spencer Township, OH (Lorain County → Lucas County)
- Waterville Township, OH (Stark County → Lucas County)

Each correction used article-context disambiguation (`legal_basis`, `trigger`, and news-source mentions). Treat the lat/lon column as ≥99% accurate. The script is `scripts/geocode_inventory.py`; re-run after adding new rows to fill in their coordinates.

## Why the inventory (n=533) and the extraction cohort (n=348) differ

Right — the numbers can be confusing. Here's the difference:

- **Inventory (n=1291):** the cleaned, deduplicated count of unique moratorium **instruments** (one per local-government action). One DeKalb County resolution = 1 row, even if there are 5 documents about it.
- **Structured-extraction cohort (n=348):** the count of confidence-filtered structured **extractions**. A single moratorium can produce multiple extractions: the ordinance text, the meeting minutes, the agenda packet, etc. Plus the cohort includes some duplicate adoptions and extensions captured separately.

The two numbers measure different things and do not need to match. The 533 is the headline count of moratoria; the 348 is the size of the line-coded sample used for clause-prevalence percentages.

## What we don't claim

- **We don't claim to have every moratorium.** Small townships without online minutes are nearly impossible to find systematically. Where we know our coverage is incomplete, we say so in [`docs/known-gaps.md`](known-gaps.md).
- **We don't claim our percentages are statistical inferences.** They describe the corpus we have, not a probability sample of all moratoria. The corpus is biased toward jurisdictions that post things online.
- **We don't claim to predict outcomes.** This is a descriptive dataset, not a causal one.

## Phase 5: The refresh cycle (added v2026.07)

Phases 1-4 build a dataset. Keeping it true is a different problem: a moratorium
is a *time-bounded* instrument, so a correct record decays into a wrong one on a
known date, with no external signal. The v2026.07 refresh introduced an explicit
cycle for this, and it is the procedure future refreshes should follow.

**1. Gate before touching anything.** `scripts/validate_dataset.py` is the
executable form of the codebook — closed vocabularies, date/duration coherence,
ID uniqueness, geocoding bounds, `[VERIFY]` accounting, and agreement between the
CSVs and `summary_stats.json`. Run it first, so any error found later is
attributable to the refresh rather than inherited.

**2. Derive the worklist, don't guess it.** `scripts/build_worklist.py` computes
which rows need attention as of a reference date, and why:

| Bucket | Meaning |
|---|---|
| `expired_in_force` | recorded in force, but the known current end date (or, if unextended, `date_enacted_iso + duration_days`) has already passed |
| `extension_end_unknown` | an extended action has no independently recorded current fixed endpoint, so its original term cannot be used as its expiration |
| `until_date_stale` | in force, ends on a calendar date not captured in typed columns |
| `stale_pending` | proposed, and old enough that it has surely been decided |
| `open_ended` | in force with no scheduled end — currency must be affirmatively confirmed |
| `verify_backlog` | carries one or more `[VERIFY ...]` markers |
| `unverified_date` | adoption date never confirmed against a primary source |

Each item is emitted with the exact question to answer, so the researcher is not
inferring the ask. In v2026.07 this produced 160 of 222 rows needing work.

**3. Partition and fan out.** `scripts/make_packets.py` splits the worklist into
per-state packets, matching how the sources are organized — one state's portals,
minutes, and legislature. Research is then parallel and independent.

**4. Research writes JSON, never CSV.** Every pass emits a decision file
conforming to [`work/schemas/research_decision.schema.json`](../work/schemas/research_decision.schema.json):
an outcome (`confirmed_unchanged` / `status_changed` / `corrected` /
`unresolvable`), the proposed field changes with their *prior* values, resolutions
for each `[VERIFY]` marker, and evidence with a source-type ranking that puts
ordinances and minutes above news. `unresolvable` is a first-class outcome and is
recorded rather than papered over.

**5. Merge deterministically, with a conflict guard.**
`scripts/apply_research.py` is the only thing that writes findings into the
inventory. It requires explicit answer-file paths (never selecting by
modification time), validates against the schema, and **refuses any change whose
stated prior value no longer matches the CSV** — which is how a stale answer,
written against a revision another pass has since corrected, gets caught instead
of silently overwriting newer data. Every applied change is logged to
`work/audit/`.

**6. Flag weak evidence rather than laundering it.** A new instrument admitted on
news-only evidence, or below a confidence threshold, automatically receives a
`[VERIFY ...]` marker naming what is missing. It therefore reappears in the next
refresh's worklist instead of hardening into apparent fact.

**7. Reconcile, re-geocode, regenerate, re-gate.** `reconcile_durations.py`
enforces the codebook's one valid `duration_days`/`duration_kind` combination;
`geocode_inventory.py` plus declared overrides fill coordinates; the generators
rebuild every artifact; then the validator runs again.

### The September 2026 update: many helpers, and a saved copy of every source

In September 2026 we ran this cycle at full size for the first time. We also
added two things it had lacked.

**Written steps, tested first.** The research was done by AI helpers, each
given one state. Every helper followed the same written steps in
`work/research-process.md`. The steps list the search and download commands to
use. They say how to decide hard cases, such as when a row has expired and
when we simply cannot tell. They also say that a permanent ban is not a
moratorium, so it stays out of the list. We tried the steps on Nevada and
Alabama first, fixed what those runs showed, and then sent them to 29 more
helpers.

Each helper did two jobs. First it rechecked every row on its to-do list
against the town's own records. Then it searched the whole state for moratoria
we did not have. That search covered all five kinds of project, and it read
the statewide news roundups that list many towns at once.

**A saved copy of every source.** `scripts/save_source.py` downloads a web page
or a document and keeps a copy under `work/sources/`. If a page needs a real
web browser to open, the script uses one. If a document is a scanned image, the
script reads the text from the picture. It also notes where the copy came from
and a fingerprint of its contents, so anyone can confirm the copy is unchanged.
Before any finding is merged, `scripts/check_evidence_archived.py` confirms that
every source it cites was saved. So each fact in the data points to a copy we
hold, not only to a link that may break.

We publish only some of those copies. Public records, such as ordinances,
minutes, agendas, and staff reports, are published under `work/sources/`. News
articles and other groups' pages belong to the people who wrote them, so their
copies stay private. `scripts/classify_sources.py` sorts each source and keeps
the private ones out of the repository. For every private copy we still
publish the link, the date it was saved, and its fingerprint. When a source is
in doubt, the script keeps it private.

The update decided all 296 rows on the to-do list and added 520 new ones. It
saved about 2,800 sources and made 1,565 changes, with no clashes at merge time.
We learned three rules the hard way, and they are now in the written steps:

- Always search with the state's name. Wells, Nevada is not Wells, Maine.
- A search limited to one website that returns pages about something else has
  found nothing.
- Keep your working files in your own folder. The helpers shared one scratch
  folder, and once one helper's script overwrote another state's findings.
  That state's findings were rebuilt and checked again.

### Checking the September 2026 update

The update more than doubled the list, and 276 of its 520 new rows were
adopted before August. That seemed like too many to have missed. So before
publishing we checked the work four ways. Each check wrote its findings in the
same format as the research, and the same merge step applied them. The full
record is in `work/qa-progress-2026-09-23.md`.

1. **Re-read every new row.** Checkers were told to assume each row was wrong
   and try to prove it. Was it a pause and not a ban? Was the date the day of
   the final vote, not a first reading? Was it already in the list under
   another name? The steps are in `work/qa-process.md`.
2. **Check a random sample blind.** We picked 40 rows at random, some new and
   some older. New checkers saw only the place name. They were not allowed to
   open our data or our notes (`work/qa-blind-process.md`). Then we compared
   what they found with what we had. They matched on 34 of the 40.
3. **Compare with other lists.** Nine other groups publish lists of local
   moratoria. We saved each list and matched it against ours, both ways. We
   looked up every place they had that we lacked (`work/qa3-gaps-process.md`).
   Where a list disagreed with one of our rows, we went back to the source.
4. **Check that each row agrees with itself.** A script looked for rows whose
   parts did not match. One example: an extended moratorium with no new end
   date. Another: a row whose text says "solar" while its sector list leaves
   solar out. Helpers fixed each one (`work/qa4-process.md`). We also checked
   that each row sits on the map in the county it names.

The checks removed 14 rows. Most were permanent bans or proposals that never
passed. They added 243 rows that other lists had and we lacked. They moved 37
rows to the right county and changed about 640 other facts. The checks also
made the merge scripts stricter, so the same mistakes are caught next time.

A property worth preserving: every step is **idempotent**. Re-running the merge
over already-applied answers is a clean no-op, which is what makes incremental
application safe when different states' research lands at different times.

## Reproducibility

Every step of the pipeline can be re-run. The scripts and their README are in the [repository's `scripts/` directory](https://github.com/mjbommar/moratorium-data-2026/tree/main/scripts). To regenerate every artifact from the source data:

```bash
pip install pandas matplotlib seaborn geopandas shapely markdown pymdown-extensions

python3 scripts/validate_dataset.py          # gate
python3 scripts/fetch_basemap.py             # one-time: Census state shapefile
python3 scripts/build_summary_stats.py       # data/summary_stats.json
python3 scripts/build_geojson.py             # site/moratoria.geojson
python3 -m scripts.generate_tables           # tables/*.tex
PYTHONPATH=scripts python3 -m moratorium_maps all   # figures/{pdf,svg,png}/
python3 scripts/make_timeline.py             # site/timeline.svg
python3 scripts/update_state_counts.py       # states/
python3 scripts/build_site.py                # HTML site
```

Before v2026.07 these commands did not work: the table and map modules had been
copied from the private working repository without repathing, and
`summary_stats.json` and `moratoria.geojson` had no generator at all. Both are
fixed, which is why the artifacts in this release are reproducible from the
shipped CSVs.

The original document corpus (~12 GB) is not in this repository (it's hosted separately on Zenodo as the supplementary data deposit) but the cleaned inventory + structured extractions are sufficient to reproduce all published statistics.

## Tooling and models

| Step | Tool | Model |
|------|------|-------|
| Document discovery (through v2026.04) | OpenAI Codex CLI with web-search | `gpt-5.5` at medium reasoning effort |
| State-month chronology (v2026.07 sweep) | OpenAI Codex CLI with web-search | `gpt-5.6-sol` at high reasoning effort |
| Status, verification, and legislation research (v2026.07) | Claude Code subagents | `claude-sonnet-5` |
| Row recheck and statewide discovery (2026-09-23 update) | Claude Code subagents coordinated by `claude-fable-5-1` | `claude-sonnet-5` (47 answer files), `claude-opus-5-5` (7 largest packets) |
| Four rounds of checks (2026-09-23 update) | Claude Code subagents, coordinated by `claude-fable-5-1` and then `claude-opus-5-5` | `claude-sonnet-5` for most checks, `claude-opus-5-5` for Ohio, Michigan, the tracker comparison, and the hardest disagreements |
| Web search (2026-09-23 update) | bc-web `search --fuse` (Exa + Google via SerpAPI, reciprocal rank fusion) | n/a |
| Source archiving (2026-09-23 update) | `scripts/save_source.py` over bc-web, pdftotext, Tesseract | n/a |
| SerpAPI ordinance search | `google-search-results` Python package | n/a |
| Document download | Playwright + stealth wrappers | n/a |
| OCR (image-based PDFs) | EasyOCR + Tesseract | n/a |
| PDF classification | pydantic-ai with OpenAI provider | `gpt-5.4-mini` at flex tier |
| Structured extraction | pydantic-ai with OpenAI provider | `gpt-5.5` at flex tier |
| Real-browser verification | Playwright + system Chrome (Xvfb) for JS-rendered portals | n/a |
| Aggregation, table generation, mapping | Python (pandas, geopandas, matplotlib, seaborn) | n/a |

## A note on cost

The 50-state month-by-month sweep behind v2026.07 is **150 model calls**, one per
state per month, each with web search enabled. That is the expensive step in this
pipeline by a wide margin, and it scales as call count times model tier times
reasoning effort.

`research_moratoria.py` pins its model and reasoning effort rather than
inheriting them from the operator's interactive config, and refuses a batch above
25 calls without an explicit `--yes`. Both defaults are deliberately modest:
state-month research is retrieval and summarization against public records, and
raising the reasoning tier buys very little on that kind of work.

The September 2026 research used about 10.8 million tokens, the units AI models
are billed in, across 31 helpers. A typical state took one helper 10 to 50
minutes. The checks that followed used about as much again across 30 more
helpers. Searching is cheap. Reading is the costly part, since each helper
opened and read somewhere between 50 and 250 pages.

Anyone reproducing the sweep should scope it first -- `--only`, `--start`, and
`--end` narrow the run, and `--dry-run` prints the work plan without spending
anything.

## Updates

Each refresh of the dataset is a tagged GitHub release (`v2026.04`, `v2026.07`, ...) with a corresponding [Zenodo DOI](https://doi.org/) (planned). Refresh cadence is roughly quarterly while the moratorium wave is active.
