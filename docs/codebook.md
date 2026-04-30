# Codebook

This document defines every column in the data files. Read this before doing analysis.

## `data/moratorium_inventory.csv`

**One row per moratorium.** 223 rows total.

| Column | What it means | Example |
|--------|---------------|---------|
| `state` | The full state name. | `Michigan` |
| `state_abbrev` | The two-letter USPS abbreviation. | `MI` |
| `jurisdiction` | The local government that adopted the moratorium. May include disambiguating context in parentheses. | `Pittsfield Township` |
| `jurisdiction_type` | The kind of local government. Closed vocabulary: `County`, `City`, `Town`, `Township`, `Village`, `Parish`, `Tribal`, `Utility-authority`, `State`, `Other`. | `Township` |
| `date_enacted` | When the local board voted to adopt the moratorium. ISO format `YYYY-MM-DD` when known; may include qualifying notes (`[VERIFY]`, `reported`, `proposed`, etc.) when uncertain. | `2025-11-20` |
| `duration` | How long the original moratorium was scheduled to run. Free-text; common values are `6 months`, `180 days`, `1 year`, `12 months`, `Indefinite`. | `6 months` |
| `legal_basis` | The legal authority cited or implied. Often references the state enabling statute (e.g., `N.C.G.S. 160D-107`, `Iowa Code Chapter 414`). | `Resolution 2025-11-17-1` |
| `trigger` | Short summary of what prompted the moratorium — usually a specific proposal or a regulatory gap. | `Proposed Meta-backed hyperscale campus` |
| `current_status` | Current disposition. Possible values include: `Active`, `Extended`, `Replaced` (by permanent regulation), `Expired`, `Rescinded`, `Pending` (proposed but not yet adopted). | `Active as of April 2026` |
| `affected_projects` | Specific named projects that the moratorium affected. Empty if none identified. | `1977 Saturn Street proposal (~49.9 MW)` |
| `outcome` | The endpoint, if known: replacement ordinance adopted, project withdrawn, etc. May be `Pending` for moratoria still in effect. | `Permanent data center ordinance adopted December 16, 2025` |
| `has_verify_tags` | `True` if any field on this row was flagged for verification. | `True` |
| `verify_count` | How many `[VERIFY]` flags remain on this row. | `2` |
| `cite_count` | How many citation markers exist on this row (legacy field, often 0). | `0` |
| `activity_level` | The state's overall moratorium-activity classification. One of `None`, `Low`, `Medium`, `High`. | `High` |

### Notes on the data

- **Multi-sector instruments** are recorded as one row, with the sectors discoverable via the `trigger`, `legal_basis`, and `outcome` text. Some rows cover both data centers and crypto mining; others cover data centers + solar + battery storage in a single resolution. We do not split a multi-sector ordinance into multiple rows.
- **Extensions** are usually recorded as updates to the original row's `current_status`, not as new rows. This keeps the count of "moratoria" equal to the count of underlying instruments.
- **Proposed but not enacted** moratoria appear in the inventory with `current_status` = `Pending` (e.g., a public hearing was scheduled but the vote hasn't happened). State-level bills that propose moratoria appear in `state_legislation.csv`, not here.
- **`[VERIFY]` flags** mark fields where we couldn't confirm the value from primary sources. Most often this is because the local government hasn't posted minutes or signed-ordinance text online yet. The `verify_count` column tells you how many remain.

## `data/state_legislation.csv`

**One row per state bill.** 413 rows total.

This file tracks state-level legislation in 2025–2026 that is *related to* moratoria — bills authorizing local moratoria, prohibiting them, preempting them, or imposing state-level moratoria of their own. Most of these bills are still pending; a small number have been enacted.

| Column | What it means |
|--------|---------------|
| `state` | Full state name. |
| `state_abbrev` | USPS code. |
| `bill_id` | The state's identifier (e.g., `HB 1012`, `SB 5982`, `LD 307`). |
| `chamber` | `House` or `Senate`. |
| `title` | Short title of the bill. |
| `summary` | One-sentence description. |
| `topic` | What kind of bill: `moratorium`, `tax incentive`, `preemption`, `transparency`, etc. |
| `status` | Where the bill is in the process: `Introduced`, `In committee`, `Passed chamber`, `Enacted`, `Failed`, `Vetoed`, etc. |
| `last_action_date` | Date of the most recent legislative action. |
| `sponsor` | Lead sponsor's name. |
| `party` | Sponsor's party affiliation, where known. |
| `notes` | Free-text remarks. |

## `data/summary_stats.json`

A single JSON object with top-level aggregates. Useful for embedding live counts on a page or programmatic comparison across releases.

```json
{
  "total_local_moratoria": 223,
  "total_state_bills": 413,
  "states_with_moratoria": 30,
  "states_without_moratoria": 20,
  "moratoria_with_verify_tags": 63,
  "top_states_by_moratoria": [["Ohio", 35], ["Michigan", 34], ...],
  "top_states_by_bills": [["Pennsylvania", 18], ...],
  "state_details": { "Alabama": {"abbreviation": "AL", "activity_level": "Medium", ...}, ... }
}
```

## `data/structured_extractions.jsonl`

**One JSON object per line.** Each line is a structured extraction from one moratorium document. About 526 successful extractions; the n=348 cohort referenced in the paper is the subset with confidence ≥ 0.4.

Each record has:

```json
{
  "source_file": "research/_originals/example.pdf",
  "url": "https://example.gov/ordinance.pdf",
  "extraction": {
    "jurisdiction": "...",
    "state": "...",
    "jurisdiction_type": "...",
    "instrument_form": "ordinance",
    "sectors": ["data_center", "crypto_mining"],
    "duration": {...},
    "findings_detail_level": "moderate",
    "definition_approach": "functional",
    "has_severability": true,
    "has_extension_mechanism": true,
    ...
    "confidence": 0.85
  },
  "error": null
}
```

The full schema (60+ fields organized into five tiers) is in [`data/moratorium-extraction.json`](../data/moratorium-extraction.json) (JSON Schema format).

Records where `error` is not null are LLM extraction failures (token limits, unsupported parameter values, etc.) — they're kept in the file for transparency but should be excluded from analysis.

## `data/clause_extraction_analysis.json`

The pre-computed aggregate analysis from `structured_extractions.jsonl` filtered at confidence ≥ 0.4. Used to generate the percentage tables (`tables/findings-impact.tex`, `tables/clause-prevalence.tex`, `tables/definitional-approaches.tex`, etc.).

Fields:

- `total_records`: 348
- `min_confidence_filter`: 0.4
- `confidence`: `{min, max, mean, median, brackets}`
- `geographic`: state counts, jurisdiction-type counts
- `temporal`: year breakdown of adoption dates
- `legal`: instrument forms, authority types, sector counts
- `clause_prevalence`: detailed breakdowns of every clause type in the 44-clause taxonomy

## A note on dates

Where possible, dates are ISO-8601 (`YYYY-MM-DD`). When a day is unknown but month+year are known, we use `YYYY-MM`. When only the year is known, `YYYY`. When the date is uncertain (sourced from news rather than minutes), we may write something like `2025-12-17 reported` or `January 2026 [VERIFY]`. Spreadsheet tools may need help parsing these; the [`examples/`](../examples/) folder shows how.
