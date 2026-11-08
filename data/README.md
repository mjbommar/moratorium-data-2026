# Data

Canonical records and reproducible derived downloads for this project.

## Files

| File | What it is | Size | Format |
|------|------------|------|--------|
| [`moratorium_inventory.csv`](moratorium_inventory.csv) | 1330 local-moratorium records. **Start here.** | 1,698,568 bytes | CSV |
| [`state_legislation.csv`](state_legislation.csv) | 447 state-policy records; mechanisms and legal effects vary | 311,312 bytes | CSV |
| [`state_policy_scope_reviews.jsonl`](state_policy_scope_reviews.jsonl) | Reviewed analytical scope decisions; raw rows retained, applied by the separate scope exports | 1,744 bytes | JSONL |
| [`summary_stats.json`](summary_stats.json) | Top-level aggregates (counts by state, by status, etc.) | 15,298 bytes | JSON |
| [`structured_extractions.jsonl`](structured_extractions.jsonl) | 864 lines: 526 successful clause extractions + 338 LLM-call errors retained for transparency | ~2 MB | JSONL |
| [`clause_extraction_analysis.json`](clause_extraction_analysis.json) | Pre-computed clause prevalence statistics for the n=348 cohort (confidence ≥ 0.4) | ~7 KB | JSON |
| [`moratorium-extraction.json`](moratorium-extraction.json) | JSON Schema describing the 60-field extraction format | ~25 KB | JSON Schema |

## State-policy scope downloads

The raw state-policy CSV retains all historical observations, including one
reviewed exclusion concerning secure student/workforce research data. Use the
[reviewed inclusion export](policy-scope/reviewed-included.csv) for explicitly
accepted infrastructure scope; it currently contains headers only. The
[annotated raw view](policy-scope/all-annotated.csv) preserves all 447 observations
with their scope-review status. The
[candidate pool](policy-scope/not-explicitly-excluded-candidates.csv) contains
446 unreviewed observations after the known exclusion; it is not an accepted
infrastructure census. These counts concern historical observations, not unique
instruments or verified current law. The [receipt](policy-scope/receipt.json)
pins inputs, partitions and output hashes; see the [export contract](../docs/policy-scope-exports.md).

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
import json
df_dc = df[df["sectors"].map(lambda value: "data_center" in json.loads(value))]
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

Canonical expanded records cover 53 reviewed proposal and measure records (51 frozen-cohort publications, Jay's solar ballot and a separate Wilmington litigated initiative) across held or intended election dates,
with 61 retained result observations and explicit supersession. Five additional
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

The current source generation selects [validation profile 1.0.4](../work/schemas/expanded/1.0.4.json). Separate retained, current-accepted and status event exports distinguish review state; none is a current-force timeline.

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
| [ballot_measures.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/ballot_measures.csv) | 53 |
| [claims.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/claims.csv) | 583 |
| [coverage_observations.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/coverage_observations.csv) | 1 |
| [elections.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/elections.csv) | 47 |
| [instrument_event_status.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/instrument_event_status.csv) | 10 |
| [instrument_events.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/instrument_events.csv) | 10 |
| [instrument_events_current.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/instrument_events_current.csv) | 10 |
| [jurisdictions.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/jurisdictions.csv) | 48 |
| [local_restrictions.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/local_restrictions.csv) | 2 |
| [measure_instrument_links.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/measure_instrument_links.csv) | 1 |
| [measure_provisions.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/measure_provisions.csv) | 52 |
| [measure_results.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/measure_results.csv) | 61 |
| [measure_results_current.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/measure_results_current.csv) | 50 |
| [review_decisions.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/review_decisions.csv) | 2594 |
| [search_attempts.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/search_attempts.csv) | 3 |
| [search_runs.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/search_runs.csv) | 1 |
| [search_sightings.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/search_sightings.csv) | 18 |
| [source_documents.csv](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/source_documents.csv) | 156 |

[Projection manifest](expanded-csv-snapshots/99280efdf5431f4f8c6d78275efddfad8387a6c0d164aa76b2f23714c7b86229/manifest.json) pins the source generation, schema, exporter and every file hash.
<!-- END EXPANDED CSV DOWNLOADS -->

The portable `data/expanded-csv` pointer selects an immutable directory under
`data/expanded-csv-snapshots/`. Keep the pointer, selected directory and manifest
together. Run `python3 scripts/build_expanded_csv.py` to regenerate or add `--check`
to detect changed bytes, stale links or a mismatched source generation. The same
checks run under `make data` and `make check`. Edit reviewed JSONL through the
publication process, then regenerate; do not treat CSV edits as canonical changes.

Reviewed duplicate retirements and original rows are retained in [`identities/legacy-moratoria.jsonl`](identities/legacy-moratoria.jsonl). Resolve historical IDs using the [legacy lookup rules](../docs/legacy-moratorium-identities.md); current CSV totals exclude retired duplicate rows.
