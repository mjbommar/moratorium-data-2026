# Data

Canonical records and reproducible derived downloads for this project.

## Files

| File | What it is | Size | Format |
|------|------------|------|--------|
| [`moratorium_inventory.csv`](moratorium_inventory.csv) | 1330 local-moratorium instruments. **Start here.** | 1,692,615 bytes | CSV |
| [`state_legislation.csv`](state_legislation.csv) | 442 state-policy records in 2025–2026; mechanisms and legal effects vary | 247,229 bytes | CSV |
| [`summary_stats.json`](summary_stats.json) | Top-level aggregates (counts by state, by status, etc.) | ~12 KB | JSON |
| [`structured_extractions.jsonl`](structured_extractions.jsonl) | 864 lines: 526 successful clause extractions + 338 LLM-call errors retained for transparency | ~2 MB | JSONL |
| [`clause_extraction_analysis.json`](clause_extraction_analysis.json) | Pre-computed clause prevalence statistics for the n=348 cohort (confidence ≥ 0.4) | ~7 KB | JSON |
| [`moratorium-extraction.json`](moratorium-extraction.json) | JSON Schema describing the 60-field extraction format | ~25 KB | JSON Schema |

## Column definitions

See [`docs/codebook.md`](../docs/codebook.md) for full definitions of every column in every file.

## Useful inventory columns

The inventory CSV includes normalized fields alongside legacy descriptions. Useful fields include:

- **`enacted_status`** — closed-vocab status: `active`, `extended`, `replaced`, `expired`, `rescinded`, or `pending`. Filter to `active` + `extended` for records classified active or extended. These classifications do not prove freshly verified current legal force.
- **`moratorium_id`** — stable identifier (`<state>-<jurisdiction>-<year>`, with phase suffixes for repeat instruments). Use this as a primary key when joining with future releases of this dataset.
- **`current_end_date_iso`** — current fixed endpoint after any extension. Use it for expiry monitoring; `duration_days` preserves the original instrument's term.
- **`latitude` / `longitude`** — WGS84 coordinates of the jurisdiction centroid. Drop the CSV into Mapbox, kepler.gl, Tableau, or any GIS tool to get an instant point map. 1289 of 1330 rows have coordinates; nonblank coordinates do not establish correct jurisdiction identity or legal applicability. See [geocoding caveats](../docs/known-gaps.md#geocoding-caveats-added-v2026042).

## Quick examples

**Count records classified active or extended, by state (Excel):** Open `moratorium_inventory.csv`, filter `enacted_status` to `active` and `extended`, then PivotTable on `state`.

**Same in Python:**

```python
import pandas as pd
df = pd.read_csv("moratorium_inventory.csv")
in_force = df[df["enacted_status"].isin(["active", "extended"])]
print(in_force["state"].value_counts())
```

**Filter to data-center-only moratoria (Python):**

```python
df_dc = df[df["trigger"].str.contains("data center", case=False, na=False)]
```

**Just the headline numbers (any tool):** Read `summary_stats.json`. It has total counts, top-states list, and per-state aggregate stats including the `enacted_status_breakdown` field — useful for embedding live values in dashboards or articles.

## A note on `structured_extractions.jsonl`

This file has 864 lines. **526** are successful structured extractions; **338** are LLM-call errors retained for transparency (so you can audit what didn't extract cleanly). The **n=348** cohort referenced in the working paper is the subset with `extraction.confidence >= 0.4`.

```python
import json
records = []
with open("structured_extractions.jsonl") as f:
    for line in f:
        r = json.loads(line)
        if r.get("error") is None and r["extraction"]["confidence"] >= 0.4:
            records.append(r)
assert len(records) == 348
```

## A note on dates

Most `date_enacted` values are ISO format (`YYYY-MM-DD`). Some are `YYYY-MM` (day uncertain), `YYYY` (only year known), or include qualifying notes (`reported`, `[VERIFY]`, `proposed`). When parsing programmatically, expect to handle both clean and messy values. The [repository's `examples/` directory](https://github.com/mjbommar/moratorium-data-2026/tree/main/examples) has working code.

## Updates

The September 23, 2026 edition is a historical baseline. The November refresh is in progress; source/status dates vary by record. These local review batches have not been published as a new GitHub Release. Citation/version reconciliation remains part of the final release work.

## Reviewed ballot records

Canonical expanded records cover 50 reviewed measures (49 frozen-cohort publications plus Jay's solar ballot) across several election dates,
with 56 retained result observations and explicit supersession. Seven additional
frozen candidate groups remain unresolved; see the [gap dispositions](../docs/known-gaps.md#ballot-candidates-retained-outside-the-reviewed-publication).
Certification and legal implementation remain separate, record-specific findings.
[The generated results view](../docs/ballot-results.md) supplies current record and
observation counts; explicit supersession retains earlier observations. Unreported
blank/turnout categories remain unknown. Operative dates and instrument links remain
unresolved; electoral approval does not automatically increase in-force moratorium
totals. This is a reviewed subset, not the full election census. See
[scope and interpretation](../docs/ballot-measures.md) and the
[publication protocol](../docs/expanded-promotion.md). The relative `data/expanded`
pointer and its `data/expanded-snapshots` target must travel together.


## Expanded CSV downloads

The current source generation selects [validation profile 1.0.2](../docs/event-validity-publication.md), with five explicitly reviewed historical events. Separate retained, current-accepted and status event exports distinguish review state; none is a current-force timeline.

Instrument-event rows describe source-supported historical actions. An `effective`
event does not establish current legal force; original expected endpoints do not
prove actual expiry. See the [event contract and profile](../docs/instrument-events.md)
for occurrence/observation time, evidence and unresolved-history distinctions.

The JSONL tables reached through `data/expanded/` are authoritative for expanded
records. These CSV files are derived from one pinned reviewed generation. They do
not change the legacy moratorium denominator or establish new legal findings.
`measure_results.csv` retains every observation; `measure_results_current.csv`
excludes explicitly superseded observations while keeping separate county parts
and other reporting scopes. It does not reduce a measure to a single result row.

Null or absent fields become empty cells, never inferred zeroes. Arrays and objects
remain compact JSON within CSV cells. Use JSONL when distinguishing null, absent
fields and empty strings or restoring exact typed records. Empty CSV tables have
headers; their presence is not evidence that research coverage is complete.

<!-- BEGIN EXPANDED CSV DOWNLOADS -->
| CSV view | Records |
|---|---:|
| [ballot_measures.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/ballot_measures.csv) | 50 |
| [claims.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/claims.csv) | 540 |
| [coverage_observations.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/coverage_observations.csv) | 1 |
| [elections.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/elections.csv) | 46 |
| [instrument_event_status.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/instrument_event_status.csv) | 5 |
| [instrument_events.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/instrument_events.csv) | 5 |
| [instrument_events_current.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/instrument_events_current.csv) | 5 |
| [jurisdictions.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/jurisdictions.csv) | 46 |
| [local_restrictions.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/local_restrictions.csv) | 1 |
| [measure_instrument_links.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/measure_instrument_links.csv) | 1 |
| [measure_provisions.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/measure_provisions.csv) | 50 |
| [measure_results.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/measure_results.csv) | 57 |
| [measure_results_current.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/measure_results_current.csv) | 50 |
| [review_decisions.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/review_decisions.csv) | 2413 |
| [search_attempts.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/search_attempts.csv) | 3 |
| [search_runs.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/search_runs.csv) | 1 |
| [search_sightings.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/search_sightings.csv) | 18 |
| [source_documents.csv](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/source_documents.csv) | 144 |

[Projection manifest](expanded-csv-snapshots/e4cf4a8b345a39a3d9ece13977d14cd0ea7d37db3b8c25d1aa3ecccf1699163b/manifest.json) pins the source generation, schema, exporter and every file hash.
<!-- END EXPANDED CSV DOWNLOADS -->

The portable `data/expanded-csv` pointer selects an immutable directory under
`data/expanded-csv-snapshots/`. Keep the pointer, selected directory and manifest
together. Run `python3 scripts/build_expanded_csv.py` to regenerate or add `--check`
to detect changed bytes, stale links or a mismatched source generation. The same
checks run under `make data` and `make check`. Edit reviewed JSONL through the
publication process, then regenerate; do not treat CSV edits as canonical changes.

Reviewed duplicate retirements and original rows are retained in [`identities/legacy-moratoria.jsonl`](identities/legacy-moratoria.jsonl). Resolve historical IDs using the [legacy lookup rules](../docs/legacy-moratorium-identities.md); current CSV totals exclude retired duplicate rows.
