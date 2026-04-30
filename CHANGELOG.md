# Changelog

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
