# Data

The canonical data files for this project.

## Files

| File | What it is | Size | Format |
|------|------------|------|--------|
| [`moratorium_inventory.csv`](moratorium_inventory.csv) | The 222-row main inventory. **Start here.** | ~190 KB | CSV |
| [`state_legislation.csv`](state_legislation.csv) | 413 state bills tracked in 2025–2026 | ~150 KB | CSV |
| [`summary_stats.json`](summary_stats.json) | Top-level aggregates (counts by state, by status, etc.) | ~12 KB | JSON |
| [`structured_extractions.jsonl`](structured_extractions.jsonl) | 864 lines: 526 successful clause extractions + 338 LLM-call errors retained for transparency | ~2 MB | JSONL |
| [`clause_extraction_analysis.json`](clause_extraction_analysis.json) | Pre-computed clause prevalence statistics for the n=348 cohort (confidence ≥ 0.4) | ~7 KB | JSON |
| [`moratorium-extraction.json`](moratorium-extraction.json) | JSON Schema describing the 60-field extraction format | ~25 KB | JSON Schema |

## Column definitions

See [`docs/codebook.md`](../docs/codebook.md) for full definitions of every column in every file.

## Two columns most users want

The inventory CSV has 17 columns. The two most useful for typical analysis are:

- **`enacted_status`** — closed-vocab status: `active`, `extended`, `replaced`, `expired`, `rescinded`, or `pending`. Filter to `active` + `extended` for "moratoria currently in force"; exclude `pending` for "ever-enacted moratoria".
- **`moratorium_id`** — stable identifier (`<state>-<jurisdiction>-<year>`, with phase suffixes for repeat instruments). Use this as a primary key when joining with future releases of this dataset.

## Quick examples

**Count moratoria currently in force, by state (Excel):** Open `moratorium_inventory.csv`, filter `enacted_status` to `active` and `extended`, then PivotTable on `state`.

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

Most `date_enacted` values are ISO format (`YYYY-MM-DD`). Some are `YYYY-MM` (day uncertain), `YYYY` (only year known), or include qualifying notes (`reported`, `[VERIFY]`, `proposed`). When parsing programmatically, expect to handle both clean and messy values. The [`examples/`](../examples/) folder has working code.

## Updates

This data is current through **April 2026**. Each refresh is tagged as a release on GitHub. The current version is shown in [`../CITATION.cff`](../CITATION.cff).
