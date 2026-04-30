# Codebook

This document defines every column in every data file. Read this before doing analysis.

## `data/moratorium_inventory.csv`

**One row per moratorium instrument.** 222 rows total.

| Column | What it means | Example |
|--------|---------------|---------|
| `state` | The full state name. | `Michigan` |
| `state_abbrev` | The two-letter USPS abbreviation. | `MI` |
| `jurisdiction` | The local government that adopted (or proposed) the moratorium. May include disambiguating context. | `Pittsfield Township` |
| `jurisdiction_type` | The kind of local government. Closed vocabulary: `County`, `City`, `Town`, `Township`, `Village`, `Parish`, `Tribal`, `Utility-authority`, `State`, `Other`. | `Township` |
| `date_enacted` | When the local board voted to adopt the moratorium. ISO format `YYYY-MM-DD` when known. May include qualifying notes (`reported`, `proposed`, `[VERIFY]`) when uncertain. For pending instruments, may say `Not enacted as of <date>; hearing scheduled <date>`. | `2025-11-20` |
| `duration` | The originally-scheduled length of the moratorium. Free-text — common values are `6 months`, `180 days`, `1 year`, `12 months`, `Indefinite`. | `6 months` |
| `legal_basis` | The legal authority cited or implied. Often references the state enabling statute (e.g., `N.C.G.S. 160D-107`, `Iowa Code Chapter 414`) and the specific ordinance/resolution number. | `Resolution 2025-11-17-1` |
| `trigger` | Short summary of what prompted the moratorium — usually a specific proposal or a regulatory gap. | `Proposed Meta-backed hyperscale campus` |
| `current_status` | Free-text description of the current disposition. May be detailed and include `[VERIFY]` notes for uncertain elements. **The closed-vocab classification is in `enacted_status` (see below).** | `Active as of April 2026; extension under consideration` |
| `affected_projects` | Specific named projects the moratorium affected. Empty if none identified. | `1977 Saturn Street proposal (~49.9 MW)` |
| `outcome` | The endpoint, if known: replacement ordinance adopted, project withdrawn, etc. May be `Pending` for moratoria still in effect. | `Permanent data center ordinance adopted December 16, 2025` |
| `has_verify_tags` | `True` if any field on this row was flagged for verification. | `True` |
| `verify_count` | How many `[VERIFY]` flags remain on this row. | `2` |
| `cite_count` | How many citation markers exist on this row (legacy field, often 0). | `0` |
| `activity_level` | The state's overall moratorium-activity classification. **Closed vocabulary: `None`, `Low`, `Medium`, `High`.** | `High` |
| `enacted_status` | **Closed-vocab status bucket** derived from the free-text fields. One of: `active`, `extended`, `replaced`, `expired`, `rescinded`, `pending`. See breakdown below. | `active` |
| `moratorium_id` | **Stable identifier** of the form `<state-abbrev>-<jurisdiction-slug>-<year>`, with `-pN` appended for explicitly-numbered phases (e.g., Oliver County) or `-N` appended for repeat instruments at the same jurisdiction in the same year. Use this column as a primary key when joining with future releases. | `mi-pittsfield-township-2025` |
| `latitude` | WGS84 latitude of the jurisdiction's centroid. Geocoded via OSM Nominatim (with U.S. Census Geocoder fallback). For counties, the centroid is the county; for cities/towns/villages/townships, the centroid is the local government boundary. Six decimal places (~10 cm precision); blank if geocoding failed. | `42.238500` |
| `longitude` | WGS84 longitude of the jurisdiction's centroid (see `latitude`). Negative for U.S. jurisdictions. | `-83.706800` |

### `enacted_status` values

This is the column most users want for filtering. The values:

- **`active`** — moratorium is currently in force (~92 rows)
- **`extended`** — moratorium was extended past its original sunset and is currently in force (~8 rows)
- **`replaced`** — moratorium has expired and a permanent ordinance has been adopted in its place (~26 rows)
- **`expired`** — moratorium has lapsed without a documented replacement (~15 rows)
- **`rescinded`** — moratorium was affirmatively repealed before its expiration date (~10 rows)
- **`pending`** — moratorium has been proposed but is not yet in force (~71 rows; e.g., a public hearing is scheduled but the vote hasn't happened)

To filter to "moratoria currently in force":

```python
in_force = df[df["enacted_status"].isin(["active", "extended"])]
```

To filter to enacted-only (current or past):

```python
enacted = df[~df["enacted_status"].eq("pending")]
```

### Notes on the data

- **Multi-sector instruments** (one ordinance covering data centers + solar + battery storage + wind) are recorded as one row. Sectors are discoverable via the `trigger`, `legal_basis`, and `outcome` text.
- **Extensions of the same instrument** (e.g., Resolution X adopts a 6-month moratorium, Resolution X-A extends it 6 more months) are recorded as updates to the original row's `current_status` and `enacted_status`, not as new rows.
- **Successive new instruments** are recorded as separate rows. If a county adopts a moratorium, lets it lift or expire, and then later adopts a *new* moratorium, each is a separate row. Oliver County, ND has three such phases — three separate moratoria, three rows, distinguished by `(Phase 1)` / `(Phase 2)` / `(Phase 3)` in the `jurisdiction` field and by the `-p1` / `-p2` / `-p3` suffix on `moratorium_id`.
- **Pending moratoria** (proposed but not yet adopted) are intentionally included with `enacted_status = pending` because the public proposal is itself politically meaningful. Filter on `enacted_status` if you want enacted-only counts.
- **`[VERIFY]` flags** mark fields where we couldn't fully confirm the value from primary sources. Most often this is because the local government hasn't posted minutes or signed-ordinance text online yet.

## `data/state_legislation.csv`

**One row per state bill.** 413 rows total.

This file tracks state-level legislation in 2025–2026 that relates to moratoria — bills authorizing local moratoria, prohibiting them, preempting them, or imposing state-level moratoria of their own. Most are still pending; a small number have been enacted.

| Column | What it means | Example |
|--------|---------------|---------|
| `state` | Full state name. | `Michigan` |
| `state_abbrev` | USPS code. | `MI` |
| `bill` | The state's bill identifier (e.g., `HB 1012`, `SB 5982`). | `HB 4456` |
| `sponsors` | Lead sponsor name(s). May include co-sponsors. | `Rep. Wortz (R)` |
| `party` | Sponsor's party affiliation, where known. May say `R`, `D`, `Bipartisan`, or be empty. | `R` |
| `status` | Where the bill is in the legislative process. Free-text but usually one of: `Introduced`, `In committee`, `Passed House`, `Passed Senate`, `Enacted`, `Failed`, `Vetoed`, `Pending`. | `In committee` |
| `key_provisions` | One-sentence description of what the bill would do. | `Imposes statewide moratorium on data centers >100 MW` |
| `activity_level` | The state's overall moratorium-activity classification (matches `activity_level` in the inventory). | `High` |

## `data/summary_stats.json`

A single JSON object with top-level aggregates. Useful for embedding live counts on a page or programmatic comparison across releases.

Top-level keys:

- `total_local_moratoria`: 222 — total rows in the inventory
- `total_state_bills`: 413 — total rows in state_legislation.csv
- `states_with_moratoria`: 30
- `states_without_moratoria`: 20
- `moratoria_with_verify_tags`: 62 — rows with at least one `[VERIFY]` flag remaining
- `moratoria_without_verify_tags`: 160
- `enacted_status_breakdown`: `{active, extended, replaced, expired, rescinded, pending}` — the breakdown of the 222 rows by `enacted_status`
- `top_states_by_moratoria`: list of `[state_name, count]` pairs, top 15
- `top_states_by_bills`: list of `[state_name, bill_count]` pairs, top 15
- `states_by_activity_level`: count of states in each closed-vocab activity bucket
- `state_details`: per-state object with `abbreviation`, `activity_level`, `local_moratoria_count`, `state_bills_count`, `file`, and (for special cases like NJ) an `activity_notes` field that preserves qualifying context

## `data/structured_extractions.jsonl`

**One JSON object per line.** The file contains 864 lines:

- 526 lines are successful extractions (records with `extraction != null` and `error == null`)
- 338 lines are LLM-call errors retained for transparency (records with `error != null`)

The **n=348 cohort** referenced in the working paper is the subset of successful extractions with `confidence >= 0.4`. Use this filter when computing clause-prevalence percentages:

```python
import json
records = [
    json.loads(line) for line in open("data/structured_extractions.jsonl")
    if json.loads(line).get("error") is None
    and json.loads(line)["extraction"]["confidence"] >= 0.4
]
assert len(records) == 348
```

Each record has fields:

- `source_file`: relative path to the original document (in `research/_originals/` of the private working repository)
- `url`: original URL the document was downloaded from (where known)
- `extraction`: the structured object — jurisdiction, state, instrument form, sectors, durations, findings, definitions, common clauses, sector-specific clauses, confidence, narrative summary
- `error`: null on success; an error message string on failure

The full schema (60+ fields organized into five tiers) is in [`data/moratorium-extraction.json`](../data/moratorium-extraction.json) (JSON Schema format). Records where `error` is not null should be excluded from analysis.

## `data/clause_extraction_analysis.json`

The pre-computed aggregate analysis from `structured_extractions.jsonl` filtered at `confidence >= 0.4`. Used to generate the percentage tables in [`tables/`](../tables/).

Fields:

- `total_records`: 348
- `min_confidence_filter`: 0.4
- `confidence`: `{min, max, mean, median, brackets}`
- `geographic`: state counts, jurisdiction-type counts
- `temporal`: year breakdown of adoption dates
- `legal`: instrument forms, authority types, sector counts
- `clause_prevalence`: detailed breakdowns of every clause type in the 44-clause taxonomy (universal, common, sector-specific, definitional approaches, findings detail levels)

## A note on dates

Where possible, dates are ISO-8601 (`YYYY-MM-DD`). When a day is unknown but month+year are known, we use `YYYY-MM`. When only the year is known, `YYYY`. When the date is uncertain (sourced from news rather than minutes), we may write something like `2025-12-17 reported` or `January 2026 [VERIFY]`. Spreadsheet tools may need help parsing these; the [`examples/`](../examples/) folder shows how.
