# Data

Canonical records and reproducible derived downloads for this project.

## Files

| File | What it is | Size | Format |
|------|------------|------|--------|
| [`moratorium_inventory.csv`](moratorium_inventory.csv) | 1328 local-moratorium records. **Start here.** | 1,829,745 bytes | CSV |
| [`state_legislation.csv`](state_legislation.csv) | 448 state-policy records; mechanisms and legal effects vary | 358,836 bytes | CSV |
| [`state_policy_scope_reviews.jsonl`](state_policy_scope_reviews.jsonl) | Reviewed analytical scope decisions; raw rows retained, applied by the separate scope exports | 1,097,764 bytes | JSONL |
| [`summary_stats.json`](summary_stats.json) | Top-level aggregates (counts by state, by status, etc.) | 15,337 bytes | JSON |
| [`structured_extractions.jsonl`](structured_extractions.jsonl) | 864 lines: 526 successful clause extractions + 338 LLM-call errors retained for transparency | ~2 MB | JSONL |
| [`clause_extraction_analysis.json`](clause_extraction_analysis.json) | Pre-computed clause prevalence statistics for the n=348 cohort (confidence ≥ 0.4) | ~7 KB | JSON |
| [`moratorium-extraction.json`](moratorium-extraction.json) | JSON Schema describing the 60-field extraction format | ~25 KB | JSON Schema |

## State-policy scope downloads

The raw state-policy CSV retains all 448 observations. The
[reviewed inclusion export](policy-scope/reviewed-included.csv) contains 381
observations explicitly included in infrastructure scope; 19 are excluded and 48
remain unresolved, with none unreviewed. The
[annotated raw view](policy-scope/all-annotated.csv) preserves every observation
and scope decision. The [candidate pool](policy-scope/not-explicitly-excluded-candidates.csv)
contains 429 observations, including the unresolved cases. It is an exploratory
pool, not an accepted infrastructure census. These counts concern observations,
not unique instruments or verified current law. The [receipt](policy-scope/receipt.json)
pins inputs, partitions and output hashes; see the [export contract](../docs/policy-scope-exports.md).

## Column definitions

See [`docs/codebook.md`](../docs/codebook.md) for full definitions of every column in every file.

## Useful inventory columns

The inventory CSV includes normalized fields alongside legacy descriptions. Useful fields include:

- **`enacted_status`** — closed-vocab status: `active`, `extended`, `replaced`, `expired`, `rescinded`, `pending`, `rejected`, or `unknown`. The last two preserve rejected proposals and genuinely unresolved recorded stages separately. Filter to `active` + `extended` for records classified active or extended. These classifications do not prove freshly verified current legal force.
- **`moratorium_id`** — stable identifier (`<state>-<jurisdiction>-<year>`, with phase suffixes for repeat instruments). Use this as a primary key when joining with future releases of this dataset.
- **`current_end_date_iso`** — current fixed endpoint after any extension. Use it for expiry monitoring; `duration_days` preserves the original instrument's term.
- **`latitude` / `longitude`** — WGS84 jurisdiction reference points. Census overrides use internal representative points, which are not necessarily geometric centroids. Drop the CSV into Mapbox, kepler.gl, Tableau, or any GIS tool to get an instant point map. 1326 of 1328 rows have coordinates; nonblank coordinates do not establish correct jurisdiction identity or legal applicability. See [geocoding caveats](../docs/known-gaps.md#geocoding-caveats-added-v2026042).

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

The September 23, 2026 edition is a historical baseline. The November refresh is in progress; source/status dates vary by record. Release `v2026.11.9.post1` publishes the reviewed current state with pending QA and explicit unresolved questions. Further source checks continue. The earlier `v2026.11.8` prerelease remains an incomplete checkpoint.

## Reviewed ballot records

Canonical expanded records cover 57 reviewed proposal and measure records:
53 mapped frozen-cohort publications, Jay's solar ballot, Wilmington's litigated
initiative, Bethel's town-meeting question, and an Augusta notice-only question
with unresolved frozen-seed correspondence. There are 65 retained result versions
and 53 current observations across 52 measures; five measures lack a current result.
Three frozen candidate payloads remain held. Augusta's notice-only record may
overlap one of them, so held payloads are not additional disjoint contests.
Its sector and result/ordinance links remain unaccepted; see the
[gap dispositions](../docs/known-gaps.md#ballot-candidates-retained-outside-the-reviewed-publication)
and [current accounting](../work/research/2026-11-08/ballot-current-accounting/README.md).
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
| [ballot_measures.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/ballot_measures.csv) | 57 |
| [claims.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/claims.csv) | 625 |
| [coverage_observations.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/coverage_observations.csv) | 1 |
| [elections.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/elections.csv) | 51 |
| [instrument_event_status.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/instrument_event_status.csv) | 12 |
| [instrument_events.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/instrument_events.csv) | 12 |
| [instrument_events_current.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/instrument_events_current.csv) | 12 |
| [jurisdictions.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/jurisdictions.csv) | 53 |
| [local_restrictions.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/local_restrictions.csv) | 3 |
| [measure_instrument_links.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/measure_instrument_links.csv) | 1 |
| [measure_provisions.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/measure_provisions.csv) | 52 |
| [measure_results.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/measure_results.csv) | 65 |
| [measure_results_current.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/measure_results_current.csv) | 53 |
| [review_decisions.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/review_decisions.csv) | 2756 |
| [search_attempts.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/search_attempts.csv) | 3 |
| [search_runs.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/search_runs.csv) | 1 |
| [search_sightings.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/search_sightings.csv) | 18 |
| [source_documents.csv](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/source_documents.csv) | 168 |

[Projection manifest](expanded-csv-snapshots/7b585b49998f8ca39b0ff433fe15c34335ea171bdd8960af1e7e9fdcf852f6cb/manifest.json) pins the source generation, schema, exporter and every file hash.
<!-- END EXPANDED CSV DOWNLOADS -->

The portable `data/expanded-csv` pointer selects an immutable directory under
`data/expanded-csv-snapshots/`. Keep the pointer, selected directory and manifest
together. Run `python3 scripts/build_expanded_csv.py` to regenerate or add `--check`
to detect changed bytes, stale links or a mismatched source generation. The same
checks run under `make data` and `make check`. Edit reviewed JSONL through the
publication process, then regenerate; do not treat CSV edits as canonical changes.

Reviewed duplicate retirements and original rows are retained in [`identities/legacy-moratoria.jsonl`](identities/legacy-moratoria.jsonl). Resolve historical IDs using the [legacy lookup rules](../docs/legacy-moratorium-identities.md); current CSV totals exclude retired duplicate rows.
