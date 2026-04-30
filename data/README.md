# Data

The canonical data files for this project.

## Files

| File | What it is | Size | Format |
|------|------------|------|--------|
| [`moratorium_inventory.csv`](moratorium_inventory.csv) | The 223-row main inventory. **Start here.** | ~190 KB | CSV |
| [`state_legislation.csv`](state_legislation.csv) | 413 state bills tracked in 2025–2026 | ~150 KB | CSV |
| [`summary_stats.json`](summary_stats.json) | Top-level aggregates (counts by state, etc.) | ~10 KB | JSON |
| [`structured_extractions.jsonl`](structured_extractions.jsonl) | Line-by-line clause coding, n=348 cohort | ~2 MB | JSONL |
| [`clause_extraction_analysis.json`](clause_extraction_analysis.json) | Pre-computed clause prevalence statistics | ~7 KB | JSON |
| [`moratorium-extraction.json`](moratorium-extraction.json) | JSON Schema describing the 60-field extraction format | ~25 KB | JSON Schema |

## Column definitions

See [`docs/codebook.md`](../docs/codebook.md) for full definitions of every column in every file.

## Quick examples

**Count moratoria by state (Excel):** Open `moratorium_inventory.csv`, insert a PivotTable, drop `state` into rows, count any column.

**Count moratoria by state (Python):**

```python
import pandas as pd
df = pd.read_csv("moratorium_inventory.csv")
print(df["state"].value_counts())
```

**Filter to data-center-only moratoria (Python):**

```python
df_dc = df[df["trigger"].str.contains("data center", case=False, na=False)]
```

**Just the headline numbers (any tool):** Read `summary_stats.json`. It has total counts, top-states list, and per-state aggregate stats — useful for embedding live values in dashboards or articles.

## A note on dates

Most `date_enacted` values are ISO format (`YYYY-MM-DD`). Some are `YYYY-MM` (day uncertain), `YYYY` (only year known), or include qualifying notes (`reported`, `[VERIFY]`, `proposed`). When parsing programmatically, expect to handle both clean and messy values. The [`examples/`](../examples/) folder has working code.

## Updates

This data is current through **April 2026**. Each refresh is tagged as a release on GitHub. The current version is shown in [`../CITATION.cff`](../CITATION.cff).
