# Changelog

## 2026-08-19 — currency, state-policy, and publication refresh

This working snapshot updates the tracker through **2026-08-19**. It is newer
than the latest tagged release, v2026.07, and preserves that release's figures
below as a historical snapshot.

### Current headline numbers

| Measure | 2026-08-19 snapshot |
|---|---|
| Local moratorium instruments | **533** |
| Currently in force (active + extended) | **429** |
| Pending / proposed | **34** |
| Past (replaced + expired + rescinded) | **70** |
| Rows carrying `[VERIFY]` markers | **182** |
| State bills tracked | **438** |
| State policy actions, including non-bill instruments | **440** |
| States with at least one local instrument | **42** |

The local status mix is 381 active, 48 extended, 34 pending, 37 replaced, 27
expired, and 6 rescinded. The review reduced the recorded in-force total by six
relative to v2026.07 as elapsed terms and documented outcomes were reconciled.
Lakeland, Florida's August 3 ordinance is the first confirmed August adoption;
Parma Township, Michigan was added after its primary public notice was located.

Extensions now carry `current_end_date_iso`, separate from their original end
date. The worklist uses that operative date and flags extensions whose current
end remains unknown instead of reporting false expirations from the original
term.

The state tracker now contains 438 bills and two binding non-bill actions, each
with a stable `policy_action_id` and typed instrument, mechanism, legal-effect,
and scope fields. New York Executive Order 62 and Texas's August 3 data-center
audit directive are recorded as in-force restrictions; Pennsylvania SB 1345
and SB 1359 remain proposals and are not presented as binding moratoria.

The GitHub Pages landing page now carries current search and social metadata,
Dataset JSON-LD, a responsive local-versus-state scope guide, August commentary,
and an explicit warning that August is current only through the 19th. The
May-through-July sweep remains the completed comparable window.

## v2026.07 — 2026-07-31 (currency refresh)

The April release was a snapshot as of **2026-04-28**. Three months of local
government activity had accumulated behind it: moratoria that expired on paper
but were quietly extended, proposals that were adopted or voted down, and a wave
of new adoptions the inventory never saw. This release brings the dataset to
2026-07-31 and adds the tooling to keep it there.

### Headline numbers

| | v2026.04.4 | v2026.07 |
|---|---|---|
| Moratorium instruments | 222 | **533** |
| Currently in force (active + extended) | 148 | **435** |
| Pending / proposed | 24 | **35** |
| Past (replaced + expired + rescinded) | 50 | **63** |
| Rows carrying `[VERIFY]` markers | 123 | **180** |
| `[VERIFY]` markers outstanding | 238 | **139** |
| Geocoded | 220 / 222 | **321 / 323** |
| State bills tracked | 413 | **438** |
| States with at least one instrument | 30 | **42** |

Michigan overtakes Ohio as the most active state: **Michigan 63** (was 34),
**Ohio 53** (was 35), Georgia 47, North Carolina 40, Iowa 30, Tennessee 24, Indiana 20, Washington 19, Wisconsin 16, Kentucky 15.

**Florida went from 1 row to 14** once its three-month sweep was converted —
the single clearest illustration of how much a state's count depends on whether
anyone has looked.

**Five states enter the dataset for the first time**: Florida, Nevada, New
Mexico, South Carolina, and Texas (see the cross-dataset reconciliation below).

### What changed in the data

**311 new instruments**, led by MI 29, GA 23, NC 21, IA 18, OH 18, TN 18, with the remainder spread across the rest of the country.

**Status resolution across 74 flagged rows.** Every row whose recorded term had
provably run out, plus every pending row older than 60 days, was re-researched
against primary sources. Notable outcomes:

- **DeKalb County, GA** voted its permanent data-center ordinance *down* on
  2026-06-23 and instead extended the moratorium to **2027-03-30**.
- **Seattle** adopted an emergency moratorium (Ordinance 127447) on 2026-06-09.
- **Prince George's County, MD** re-upped its pause for two more years via
  CR-066-2026 rather than letting it lapse into permanent regulation.
- **Larimer County, CO** was extended a second time on 2026-07-13, six months
  past the date previously recorded.
- **Griffin, GA**, **Polk County, GA**, **St. Charles Parish, LA**, **Brevard,
  NC**, and **Montour County, PA** converted their moratoria into permanent
  ordinances (`replaced`).
- **La Grange, KY** and **Waterville, OH** lapsed with nothing adopted
  (`expired`); **Shutesbury, MA**'s expected permanent bylaw never reached a
  town-meeting vote.
- **Lowell Township, MI** *rejected* a proposed moratorium 2-5 — recorded
  distinctly from an ordinary lapse.

**Corrections that change the substantive record.** Morris, CT is a **12-month**
moratorium, not the two-year term reported in press coverage (the adopted text
governs). Lewiston, NY runs **18 months**, resolvable only by reading the
enacted local law. The Seminole Nation's moratorium is deliberately
**indefinite** rather than carrying an undisclosed fixed term.

**Sector-companion instruments separated.** Shelby County, IA adopted four
resolutions on 2026-03-17 covering data centers (2026-16), solar (2026-14),
battery storage (2026-15), and wind (2026-17). The inventory's grain is the
*instrument*, so these are now four rows. See the deduplication note in
`docs/codebook.md`.

### State legislation tracker

Every 2026 regular session has since adjourned or recessed. 438 of 425 bills now
carry a researched final disposition, including **84 enacted**. Three new typed
columns make the tracker filterable for the first time:

- `bill_status_category` — closed vocabulary (`enacted`, `failed_died`,
  `carried_over`, `in_committee`, …)
- `last_action_date_iso`
- `chamber_of_origin`

The `carried_over` vs `failed_died` distinction is session-structure dependent,
not calendar dependent, and was determined per state. Notable enactments: New
Jersey **A796/S731** (P.L.2026 c.32, signed 2026-07-07), Oklahoma **HB 2992**
(Data Center Customer Protection Act, 2026-05-11) and **SB 259** (2026-05-20),
Virginia HB153/HB496/SB94/SB553, South Dakota HB 1038 and SB 135, and Maryland's
Utility RELIEF Act (Ch. 353).

### Coverage: the May-July window is complete

**All 50 states were swept** month by month for May, June, and July 2026. Counts
inside that window are an enumeration, not a lower bound. This is the first
window in the dataset's history for which that holds.

**10 states recorded no local adoption in the window**: Alaska, Arizona,
Delaware, Hawaii, Idaho, Louisiana, Rhode Island, Vermont, West Virginia, and
Wyoming. Those are findings. Wyoming is the sharpest: Cheyenne's proposed
twelve-month moratorium was rejected 9-1 on second reading, so the state's
absence records a decision rather than a gap in our looking.

**What the sweep was worth.** Several states' counts moved sharply on conversion,
and nothing changed on the ground to cause it:

| State | Before its sweep | After |
|---|---|---|
| Florida | 1 | 14 |
| Georgia | 26 | 47 |
| North Carolina | 19 | 40 |
| Tennessee | 6 | 24 |
| South Carolina | 1 | 6 |
| Utah | 0 | 6 |

Read that as the measure of what single-source coverage of this topic misses.

**Earlier periods were not swept this way.** Anything dated before 2026-05-01
entered through document search and opportunistic discovery, so those counts stay
lower bounds. A time series crossing 2026-05 will show a step that is partly
method rather than only events -- `data/sweep_coverage.json` records exactly
which window was swept so the discontinuity is legible.

### What was deliberately NOT refreshed

The 44-clause taxonomy extraction was **not** re-run. Its cohort — 348 documents
across 211 jurisdictions — was collected before 2026-04-28, so the three tables
derived from it (`definitional-approaches`, `findings-impact`,
`sector-specific-clauses`) now describe roughly half the inventory rather than
all of it.

This was a judgment call rather than an oversight. The 50-state document sweep
was still running when the release was cut, and running the extraction against a
partial corpus would have produced a cohort mixing two collection snapshots —
harder to reason about than a clean one taken after the sweep finishes. Of the
200 instruments added this cycle, roughly 91 have a primary source that could
yield an extractable document; the other 109 are news-only and would contribute
nothing to clause-level coding either way.

The inventory-derived tables were regenerated and are current. The mismatch is
flagged in `README.md`, `docs/codebook.md`, and `docs/known-gaps.md` so the
clause percentages are not read as characterizing the present inventory.

Also noted while checking this: `tables/clause-prevalence.tex` has no generator
in this repository and cannot be rebuilt from the shipped data. It is carried
forward from an earlier release and should either gain a generator or be dropped.

### Cross-dataset reconciliation

A sibling research project maintains its own state-level rollup of data-center
moratoria, built to different inclusion criteria.
`scripts/reconcile_sibling_tracker.py` compares it against this inventory and
found the two **disagree in 31 of 34 shared states, in both directions**. The
sibling rollup names **44 jurisdictions across 23 states** that this inventory
has no row for, including seven states where we record none at all (Florida,
Nevada, New Mexico, Rhode Island, South Carolina, Texas, Utah).

We deliberately did **not** merge those counts. Two datasets built to different
definitions should not be reconciled by overwriting one with the other, and the
sibling file also carries research columns this project does not own. Instead
each lead was verified individually and admitted only on confirmation.

**Outcome of that verification: 33 of the 44 leads (75%) were real.**
Five states entered the dataset as a result — Florida (Nassau County, confirmed
from the county's own Ordinance 2026-044), Nevada (Nye County, Reno), New Mexico
(Socorro County), South Carolina (Newberry County), and Texas (Harlingen, plus
Hill County, adopted 2026-05-12 and then rescinded 2026-06-04 after a $100M
developer lawsuit).

The false positives are as instructive as the hits, and they characterize what a
secondary rollup gets wrong:

- **Advocacy mistaken for adoption.** Iron County, UT had no moratorium; the
  underlying item was a congressional candidate's event *calling for* one.
- **Jurisdiction confusion.** "Wichita" was Sedgwick County's moratorium, already
  in the inventory; "Chesterfield County, SC" was really Chesterfield County, VA.
- **Proposals counted as votes.** Baldwin Park, CA and Miami County, KS had
  discussion but no adopted instrument.
- **Adopted-then-invalidated.** Logan County, IL did vote a moratorium in May
  2026, but the State's Attorney ruled in June that it was never legally adopted
  (the required zoning-board hearings were skipped) and directed staff to accept
  applications. Not an operative instrument, so excluded.
- **Structural undercount.** "Durham, NC" was a single tracker entry, but Durham
  city and Durham county are distinct governments that each adopted their own
  moratorium. Any one-row-per-name rollup undercounts wherever a city and its
  namesake county both act.

The lesson generalizes: treat a secondary rollup as a lead generator, never as a
source. The disagreement also puts a floor under how incomplete single-source
coverage of this topic is, which is now recorded in `docs/known-gaps.md` so users
read the state list as a lower bound rather than an enumeration.

### Upstream synchronization

The private working repository's copy of the inventory had drifted to a 108-row,
15-column ancestor while the published file moved to 323 rows and 25 columns —
so any figure regenerated there was silently using year-old data.
`scripts/sync_upstream.py` now pushes the canonical file back to it and states
the direction of flow explicitly: research flows *out* of the working repository,
but the cleaned, typed, geocoded, validated inventory lives here and only here.

### Data-quality fixes

- **LaTeX escaping leaked into three fields.** `App\_Pages` (twice) broke a
  source URL and `\$11 million` misrendered. Now unescaped; the CSVs are data,
  so a backslash is never meaningful in them.
- **`Utility authority` → `Utility-authority`** — one row used an unhyphenated
  spelling outside the closed vocabulary.
- **11 New Jersey legislation rows** carried a full qualifying sentence in the
  closed-vocab `activity_level` column. They now read `None`; the qualifier
  already lives in `summary_stats.json` under `state_details`, which
  `docs/codebook.md` documents as its home.
- **A misplaced coordinate.** Automated geocoding resolved Lyon Township, MI to
  the Roscommon County township rather than the Oakland County one, putting a
  Detroit-area hyperscale moratorium 130 miles north. The row is now
  `Lyon Charter Township (Oakland County)` with corrected coordinates. Three
  further jurisdictions that no geocoder could resolve are handled by declared
  overrides with stated reasoning (`scripts/apply_geo_overrides.py`).
- **`duration_days` / `duration_kind` reconciled.** The codebook permits exactly
  one valid combination — `duration_days` is populated if and only if
  `duration_kind` is `fixed_days`. Six rows violated this and are fixed.
- **Weakly-evidenced new rows are flagged, not laundered.** A new instrument
  admitted on news-only evidence now receives an explicit `[VERIFY ...]` marker
  naming what is missing, so it surfaces in the next refresh rather than reading
  as established fact. Roughly a fifth of the new rows carry such a marker.
- The previously-unreleased `has_verify_tags` / `verify_count` recount described
  below is included in this release.

### New tooling

The repository could not previously rebuild its own published artifacts. That is
fixed, and the pipeline is now gated.

- `scripts/validate_dataset.py` — executable form of the codebook. Checks closed
  vocabularies, date/duration consistency, ID uniqueness and format, geocoding
  bounds, `[VERIFY]` accounting, and agreement between the CSVs and
  `summary_stats.json`. Exits nonzero on error.
- `scripts/build_summary_stats.py` and `scripts/build_geojson.py` — **these
  artifacts had no generator at all**, which is precisely why they drifted.
- `scripts/build_worklist.py`, `make_packets.py`, `make_legislation_packets.py` —
  turn the inventory into a prioritized, state-partitioned research worklist.
- `scripts/apply_research.py`, `apply_legislation.py` — the only scripts that
  write research findings into the CSVs. They require explicit answer-file
  paths, validate against a JSON Schema, refuse any change whose `from` value no
  longer matches the CSV, and write an audit log of every field change to
  `work/audit/`.
- `scripts/normalize_vocab.py`, `reconcile_durations.py`, `apply_geo_overrides.py`
  — idempotent normalizers that report every cell they touch and refuse to
  coerce values they have no declared mapping for.
- `scripts/fetch_basemap.py` — fetches the Census state shapefile the maps need.

**Fixed: the documented rebuild commands did not work.** `scripts/generate_tables`
and `scripts/moratorium_maps` were copied from the private working repository
without repathing and still pointed at `research/analysis/…`, `latex/tables/`,
and `latex/figures/` — paths that do not exist here. Anyone following
`scripts/README.md` got a `FileNotFoundError` on the first command. All paths now
resolve, figures are written to `figures/{pdf,svg,png}/`, and PNG output is
generated natively rather than by an undocumented external conversion step.
Regenerating also revealed that the committed `tables/*.tex` were stale relative
to the committed CSV; they are now rebuilt from it.

### The published site

`index.html` is the GitHub Pages landing page and the most public-facing artifact
here. It had no generator: its counts were hand-maintained, so it still read
"222 moratoria across 30 states. Updated April 2026" while the inventory had
nearly doubled. `scripts/build_index.py` now regenerates every number-bearing
span from the CSVs and is gated by `make check`.

Two presentation bugs came out of actually rendering the page and looking at it,
neither of which any markup check would have caught:

- **The timeline chart was truncated.** `make_timeline.py` hardcoded its end
  month at 2026-04, so the chart on the landing page silently dropped every
  adoption in the May-July window and reported 205 where the data holds 375. The
  range now derives from the data.
- **The chart and its caption disagreed by two.** The caption counted rows with a
  usable date (377); the chart plots rows it can bin to a month (375). Both were
  right. Entiat and Waterville carry year-only 2018 dates. The caption now
  reports the plotted figure and names both exclusions.

The page also got a design pass. Light and dark are each stepped against their
own surface rather than dark being an automatic flip, prose sections sit on
surfaces instead of bare background, and the stat numbers now wear ink rather
than status color -- the amber measured 1.79:1 on the light surface, and a
colored dot beside the label carries the status instead, never alone.

Copy across the landing page follows the house style in
`book-template/docs/guides/STYLE.md`.

### Reproducing this release

```bash
pip install pandas matplotlib seaborn geopandas shapely markdown pymdown-extensions
python3 scripts/validate_dataset.py --today 2026-07-31   # gate
python3 scripts/fetch_basemap.py                         # one-time
python3 scripts/build_summary_stats.py
python3 scripts/build_geojson.py
python3 -m scripts.generate_tables
PYTHONPATH=scripts python3 -m moratorium_maps all
python3 scripts/make_timeline.py
python3 scripts/update_state_counts.py
python3 scripts/build_site.py
```

---

## Unreleased

### Bug fix: stale `has_verify_tags` / `verify_count` columns recounted

The `has_verify_tags` and `verify_count` columns in
`data/moratorium_inventory.csv` were stale relative to the row text: only
10 rows were flagged `True` (30 flags total), while the free-text fields
actually contained 238 `[VERIFY ...]` markers across 123 rows. Separately,
`summary_stats.json` reported `moratoria_with_verify_tags: 62` — a number
that counted only markers in the `current_status` field, not "any field on
the row" as the codebook defines.

Both columns were recomputed directly from the published row text
(case-insensitive count of `[VERIFY` occurrences across every field of the
row). No substantive data changed — statuses, triggers, jurisdictions, and
all free-text fields are byte-identical.

Corrected numbers, now consistent everywhere:

- `has_verify_tags = True`: 10 → **123** rows (99 rows without)
- total `verify_count`: 30 → **238** flags
- `summary_stats.json` `moratoria_with_verify_tags`: 62 → **123**;
  `moratoria_without_verify_tags`: 160 → **99**
- codebook and known-gaps pages updated to match (known-gaps previously
  said "63 of the 223 rows", a pre-v2026.04.1-dedup figure)

---

## v2026.04.4 — 2026-04-30 (LLM-normalized typed columns)

### Six new typed columns

Free-text fields like `date_enacted` ("2025-11-20 introduction (Resolution
No. 2025-11-07 text recites 'Commissioners meeting in Regular Session this
20th day of November 2025'). The December 18, 2025 ... agenda places
Resolution 2025-11-07 under 'Old Business — Item 2,'...") and `duration`
("Initial 100 days; extended multiple times to 2026-06-23") are useful
for provenance but useless for filtering and analysis. We added six new
typed columns extracted by `scripts/normalize_inventory_fields.py`
(gpt-5.5 at the OpenAI flex tier with a Pydantic-typed structured output):

| Column | Type | Values |
|---|---|---|
| `date_enacted_iso` | string | `YYYY-MM-DD` / `YYYY-MM` / `YYYY` / empty |
| `date_enacted_uncertainty` | enum | `exact`, `month_only`, `year_only`, `range`, `unverified` |
| `duration_days` | integer or empty | numeric original duration in days; empty when not a fixed period |
| `duration_kind` | enum | `fixed_days`, `until_date`, `until_event`, `indefinite`, `unknown` |
| `sectors` | JSON array | multi-label: `data_center`, `battery_storage`, `solar`, `wind`, `cryptocurrency_mining`, `general` |
| `trigger_categories` | JSON array | multi-label: `specific_project`, `regulatory_gap`, `infrastructure_capacity`, `environmental`, `noise`, `water`, `grid_energy`, `fire_safety`, `land_use_compatibility`, `property_values`, `legal_or_litigation`, `agricultural_preservation`, `other` |

The original free-text columns (`date_enacted`, `duration`, `trigger`) are
preserved for provenance.

### Closed-vocab normalizations

The same script also audited `jurisdiction_type` and `activity_level`
against their closed vocabularies and patched 21 non-conforming
`jurisdiction_type` values (e.g. `City and County` → `City` for Denver,
`City (non-charter code city)` → `City` for 8 Washington cities,
`Tribal Government` → `Tribal`, 5 NC `City` → `Town`, 2 meta-rows from
empty → `Aggregate meta-row`). Activity level had no violations.

### Headline distribution

- **Sectors**: data_center 201 · cryptocurrency_mining 47 · battery_storage 15 · solar 8 · general 8 · wind 1
- **Top trigger categories**: regulatory_gap 176 · land_use_compatibility 151 · infrastructure_capacity 93 · grid_energy 89 · specific_project 78 · water 71 · noise 64 · environmental 59
- **Date confidence**: exact 151 · unverified 68 · month_only 2 · year_only 1 (and 27 empty for pending/undated)
- **Duration kinds**: fixed_days 160 · until_date 25 · unknown 28 · until_event 6 · indefinite 3

### Audit trail

`data/inventory_normalizations.json` records, for each `moratorium_id`,
the LLM's per-row picks, reasoning, and confidence — useful for sampling
the model's calls.

---

## v2026.04.3 — 2026-04-30 (enacted_status reclassification)

### Bug fix: 48 rows were mis-classified

The `enacted_status` column was previously derived by a regex classifier
that concatenated `current_status`, `outcome`, `date_enacted`, and
`jurisdiction` into one blob and substring-matched against keyword lists.
This produced false positives any time hypothetical phrasing
("Active unless extended"), tangential mentions ("article since removed"),
or follow-on regulatory work in `outcome` ("Pending. Staff directed to
prepare UDO amendments...") happened to contain a state-vocab keyword.

We rebuilt the classifier with a Pydantic-typed gpt-5.4-mini call
(`scripts/classify_enacted_status.py`) that reads the row's narrative
fields and returns one of `active`, `extended`, `pending`, `replaced`,
`expired`, `rescinded` with a written justification and a confidence
score. Every row was reviewed by hand against the LLM's call; one manual
override was applied (Mason, MI: rescinded → replaced).

### Headline counts revised

|                | Old (v2026.04.2) | New (v2026.04.3) |
|----------------|------------------|------------------|
| In force       | 100 (92 + 8)     | **148 (137 + 11)** |
| Pending        | 71               | **24**           |
| Replaced       | 26               | **27**           |
| Expired        | 15               | **18**           |
| Rescinded      | 10               | **5**            |

The total stays at 222. Many rows that were tagged `pending` because
their `outcome` field led with "Pending. [follow-on regulatory work]"
were actually adopted moratoria with `current_status: "Active"`. Those
flipped to `active`. Several rows whose `current_status` led with
"Active unless extended/replaced" stayed `active` instead of being
mis-bucketed as extended/replaced.

### Audit trail

`data/enacted_status_classifications.json` records, for each
`moratorium_id`, the LLM's chosen status, its written reasoning, its
self-reported confidence, and any manual override.

### Map and headline updates

- `site/moratoria.geojson` regenerated from the corrected CSV (so the
  Pages-site dot colors reflect the new classifications).
- `summary_stats.json` `enacted_status_breakdown` updated.
- README headline counters and the Pages-site stat cards updated to
  148 / 24 / 50.
- The April 2026 working paper draft was rebuilt with corrected
  in-force/pending/past totals.

---

## v2026.04.2 — 2026-04-30 (geocoding + paper-data alignment)

### Schema additions

- **New `latitude` and `longitude` columns** in the inventory CSV. WGS84 coordinates of each jurisdiction's centroid, geocoded via OSM Nominatim with a Census Geocoder fallback. Six decimal places (~10 cm precision). 220 of 222 rows successfully geocoded; the 2 blanks are aggregate "Other Reported" / "Proposed or Rejected" meta-rows that aren't real geographic points.
- New `scripts/geocode_inventory.py` lets anyone re-geocode after adding new rows.

### Geocoding QA

After the initial geocoding run, a manual triple-check across 89 verifications (random sampling against geographic knowledge, Wikipedia GeoSearch reverse-lookup, and nearby-page context analysis) caught 4 within-state same-name-township ambiguities — all in Ohio, where the geocoder had picked the wrong jurisdiction in the same state:

- Lake Township, OH: relocated from Logan County → Wood County (Tracy/Latcha Rd, Toledo suburb)
- Plain Township, OH: relocated from Franklin County → Stark County (article context: "Stark County data center concern")
- Spencer Township, OH: relocated from Lorain County → Lucas County (article context: "Anthony Wayne area")
- Waterville Township, OH: relocated from Stark County → Lucas County (article context: Toledo Free Press)

After these corrections, **all 89 verifications passed**. Treat the lat/lon column as ≥99% accurate. Washington Township, OH remains residually ambiguous (Franklin County is the most-likely default) and is flagged in [`docs/known-gaps.md`](docs/known-gaps.md).

### Paper-data alignment fixes

- `Moratorium_Survey_20260430_Draft_004.pdf` (in the private working repo) now matches this dataset exactly. Earlier drafts cited 223 moratoria; that's been corrected to 222 throughout the paper after the v2026.04.1 Harrison dedup. Paper text confidence range updated from `0.40 to 0.95` to `0.40 to 0.98` (the actual JSON max).
- `appendix-d-methodology.tex` Phase 2 classification table updated to current values: 3,925 PDFs classified (was 2,433); 709 moratorium-related (was 202); 1,123 primary legal sources (was 503). The "98 structured records" stub fixed to 348.

### Public-release sanitization

- Stripped the `source_path` field from all 864 records in `structured_extractions.jsonl`. The field had been leaking the private working repo's filesystem path (`/nas4/data/workspace/personal/...`). The `source_file` basename is preserved; the absolute path is internal-only.

---

## v2026.04.1 — 2026-04-30 (data-quality patch)

Five fixes after community review of the v2026.04 initial release.

### Data changes

- **Deduplicated Arkansas/Harrison.** Dropped the duplicate "City of Harrison, AR" row that the Feb 2026 baseline `update_inventory.py` was re-injecting on top of the April codex extract. The April record (jurisdiction = "Harrison") had the better disposition data — confirming the moratorium was *repealed* on 2023-11-28 — while the Feb stub was still flagged `[VERIFY]`. The fix: remove the Feb baseline entry from `get_new_entries()` and rely on the April extract. **Headline 223 → 222.**
- **Normalized New Jersey's activity_level.** The `summary_stats.json` value `"None for formal moratoria; High for non-moratorium restrictions"` violated the codebook's closed vocabulary. Replaced with `None` (this dataset specifically tracks formal moratoria); the qualifying narrative moves into `state_details["New Jersey"].activity_notes` so it remains discoverable.

### Schema additions

- **New column `enacted_status`** in the inventory CSV — closed-vocab classification derived from the free-text `current_status` and `outcome` fields. Values: `active`, `extended`, `replaced`, `expired`, `rescinded`, `pending`. Use this for filtering rather than parsing the free-text status.
- **New column `moratorium_id`** in the inventory CSV — stable identifier of the form `<state>-<jurisdiction-slug>-<year>`, with `-pN` appended for explicitly-numbered phases (e.g., Oliver County, ND has `-p1`, `-p2`, `-p3`). Use as a primary key for joins across releases.
- **New `enacted_status_breakdown` object** in `summary_stats.json` — counts of rows by status bucket.

### Documentation

- **Rewrote the `state_legislation.csv` section of the codebook** to match the actual CSV columns (`bill`, `sponsors`, `party`, `status`, `key_provisions`, `activity_level`). The previous codebook described columns that didn't exist.
- **Clarified `structured_extractions.jsonl` wording** in README and `data/README.md`. The file contains 864 lines (526 successful extractions + 338 LLM-call errors). The n=348 cohort cited in the paper is the confidence-≥-0.4 subset of the successful extractions.
- **README headline split** into "in force / pending / past" so the 222 isn't read as "222 moratoria currently in force." It's "222 moratorium instruments tracked: 100 in force, 71 pending, 51 past."

### Status of headline counts

- **222 moratorium instruments** total
- **100 currently in force** (active + extended)
- **71 pending or proposed** (not yet adopted)
- **51 past** (replaced, expired, or rescinded)
- **30 states** with at least one instrument

### Audit trail

A targeted dedup audit across all 30 states (normalized jurisdiction comparison + same-date + same-ordinance signals) found exactly one structural duplicate in v2026.04: the Harrison/AR pair fixed in this release. The other duplicate-shaped pairs flagged by the audit (Oliver County ND Phase 1/2/3, Lamar+Pike GA, Dundee+Sylvan Townships MI, Saginaw+Saline cities MI) were verified as **not duplicates** — separate instruments at different jurisdictions or in different time periods.

---

## v2026.04 — April 2026 (initial public release)

**Cutoff:** 2026-04-29

### What's in this release

- **223 moratoria** across 30 states in the cleaned inventory (later corrected to 222 in v2026.04.1)
- **413 state-level bills** tracked in 2025–2026
- **348 moratorium texts** structurally extracted with the 44-clause taxonomy (cohort filtered at confidence ≥ 0.4)
- **~4,400 original source documents** used to build the corpus

### Top states (initial)

1. Ohio — 35
2. Michigan — 34
3. Georgia — 24
4. North Carolina — 19
5. Iowa — 12
6. Indiana — 11
7. Washington — 11
8. Kansas — 8
9. North Dakota — 7
10. Tennessee — 6

### Notable findings

- The pace is accelerating: 130 moratoria were enacted in just the first four months of 2026 — more than in all of 2025.
- Ohio overtook Michigan as the highest-volume state.
- Most moratoria target data centers (~93%). Cryptocurrency mining, battery storage, solar, and wind appear at smaller but non-trivial volumes.
- 58.9% of analyzed moratoria provide no formal definition of the regulated use; 77.3% include no exemptions; only 23.6% contain detailed legislative findings.
- One tribal moratorium (Sault Tribe of Chippewa Indians, April 2026) is the first such record in our corpus.
- One utility-authority moratorium (Ypsilanti Community Utilities Authority, April 2026) is the first such record on water/sewer hookups for hyperscale data centers.

### Coming in the next release (planned ~Q3 2026)

- Searchable, filterable web table on a GitHub Pages site
- Zenodo DOI minted for this release and all future ones
- Geocoding of every jurisdiction
- Outcome tracking: each moratorium followed from enactment through replacement/extension/expiration/rescission
