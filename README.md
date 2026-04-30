# Moratorium Data 2026

**Open data on local-government moratoria targeting data centers, battery storage, solar, wind, and cryptocurrency mining across the United States.**

This is the open companion dataset for the working paper [*Moratorium Nation: A Survey of Data Center, Renewable Energy, and Battery Storage Moratoria in the United States*](#cite-this).

> **As of April 2026, 223 moratoria across 30 states.**
> Ohio leads with 35, followed by Michigan (34), Georgia (24), North Carolina (19), and Iowa (12).

![Moratorium counts by state](figures/png/map-moratorium-counts.png)

---

## Quick links

|  |  |
|---|---|
| 🗺️ **Find your state** | [Browse the 30-state index →](states/README.md) |
| 📊 **Get the data** | [`data/moratorium_inventory.csv`](data/moratorium_inventory.csv) (Excel-ready) |
| 📖 **Read the FAQ** | [What is a moratorium? Why does this dataset exist? →](docs/FAQ.md) |
| 🧪 **Reproduce the analysis** | [`docs/methodology.md`](docs/methodology.md) |
| 📚 **Cite this dataset** | [How to cite ↓](#cite-this) |

---

## What is in this repository

This repository contains four kinds of artifacts, each in its own folder:

| Folder | What's inside | Best for |
|--------|---------------|----------|
| [`states/`](states/) | One human-readable Markdown page per state, listing every moratorium in plain English. | Anyone who wants to know what's happening in a specific state. |
| [`data/`](data/) | The underlying data — CSV files for spreadsheets, JSON for programmers. | Journalists, analysts, researchers. |
| [`figures/png/`](figures/png/) | Eight maps as PNG images (with PDF and SVG copies in sibling folders for print). | Anyone making slides, articles, or reports. |
| [`tables/`](tables/) | LaTeX-formatted tables (already pre-built, drop-in) | Academics writing papers. |

We also include the [scripts](scripts/) and [methodology](docs/methodology.md) so anyone can re-run the analysis and audit our choices.

---

## What is a moratorium?

A **moratorium** is a temporary pause that a local government — usually a city, county, or township — places on accepting or approving certain kinds of new development. While the moratorium is in effect, no one can apply for permits to build the kinds of projects it covers. The pause is meant to give the local government time to study the impacts and write permanent rules.

**Why are these moratoria happening?** Local governments have been caught flat-footed by the speed of new infrastructure proposals — particularly hyperscale data centers (often 100+ megawatts) and large battery-storage facilities. Existing zoning codes, written decades ago, don't define or regulate these uses. A moratorium buys time to catch up.

**Are these moratoria permanent bans?** No. Almost all are time-limited (typically 6 to 12 months) and have an automatic expiration date. A small number have been extended; some have been replaced by permanent regulations; a few have been rescinded.

For more, see the [FAQ](docs/FAQ.md).

---

## The headline numbers

As of **April 2026**:

- **223** local moratoria identified in our cleaned inventory
- **30** states have at least one moratorium; **20** states have none we've identified
- **Top 10 states**: Ohio (35), Michigan (34), Georgia (24), North Carolina (19), Iowa (12), Indiana (11), Washington (11), Kansas (8), North Dakota (7), Tennessee (6)
- **Sectors covered**: most moratoria target **data centers** (~93% mention them); a substantial share also cover **cryptocurrency mining**, with smaller numbers covering **battery storage**, **solar**, and **wind**
- **413** state-level bills tracked in 2025–2026 (some proposing moratoria, others authorizing or restricting local moratoria)
- **348** moratorium texts have been read line-by-line and coded against a 44-clause taxonomy (see [`data/structured_extractions.jsonl`](data/structured_extractions.jsonl))

Full state-by-state breakdown: [**states/README.md**](states/README.md).

---

## How to use the data

### Open in Excel or Google Sheets

Download [`data/moratorium_inventory.csv`](data/moratorium_inventory.csv) and open it in Excel, Google Sheets, Numbers, or any spreadsheet tool. Each row is one moratorium. Column definitions are in [`docs/codebook.md`](docs/codebook.md).

### Load with Python (pandas)

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/mjbommar/moratorium-data-2026/main/data/moratorium_inventory.csv")
df["state"].value_counts().head(10)
```

### Load with R

```r
df <- read.csv("https://raw.githubusercontent.com/mjbommar/moratorium-data-2026/main/data/moratorium_inventory.csv")
sort(table(df$state), decreasing = TRUE)[1:10]
```

### Just want the numbers

[`data/summary_stats.json`](data/summary_stats.json) is a small JSON file with the headline totals (counts by state, total bills, etc.) — useful if you want to embed live-updating numbers in your own page.

---

## How to cite

> Bommarito, Michael J. (2026). *Moratorium Nation: U.S. Infrastructure Moratorium Data* (April 2026 release) [Data set]. Available at https://github.com/mjbommar/moratorium-data-2026.

If you cite the underlying paper:

> Bommarito, Michael J. (2026). *Moratorium Nation: A Survey of Data Center, Renewable Energy, and Battery Storage Moratoria in the United States.* Working paper. Available at SSRN.

A `CITATION.cff` file is included in the repo so GitHub renders a "Cite this repository" button automatically.

---

## License

- **Data** (`data/`, `states/`, `tables/`, `figures/`) is licensed under [Creative Commons Attribution 4.0 (CC-BY-4.0)](LICENSE-data). You can reuse, redistribute, and remix the data, including commercially, as long as you credit the source.
- **Code** (`scripts/`, `notebooks/`, `examples/`) is licensed under the [MIT License](LICENSE-code).

This is a working dataset that will be refreshed periodically. Each refresh is tagged as a release; current is **v2026.04**.

---

## Status, gaps, and how to contribute

This dataset is built from public records (municipal websites, board meeting minutes, news coverage) plus AI-assisted research. We are confident in **what we have**, but we know we don't have everything — small townships often don't post agendas online, and our automated tools sometimes can't reach behind authentication walls.

- **Found a moratorium we missed?** [Open an issue](https://github.com/mjbommar/moratorium-data-2026/issues/new?template=new-moratorium.md) — we'll add it in the next release.
- **Found an error?** [Submit a correction](https://github.com/mjbommar/moratorium-data-2026/issues/new?template=correction.md).
- **Question about the data?** [Ask here](https://github.com/mjbommar/moratorium-data-2026/issues/new?template=question.md).

Known gaps and limitations are documented in [`docs/known-gaps.md`](docs/known-gaps.md).

---

## Acknowledgments

This dataset was built using AI-assisted research agents to scan municipal websites, agenda portals, board minutes, and legislative trackers across all 50 states, supplemented by manual verification of high-priority entries. The methodology is documented in detail at [`docs/methodology.md`](docs/methodology.md).

Contact: [Michael J. Bommarito](mailto:michael.bommarito@gmail.com).

---

## Repository map

```
moratorium-data-2026/
├── README.md                      # this page
├── states/                        # 50-state index + 30 per-state pages
├── data/                          # canonical CSVs and JSON
│   ├── moratorium_inventory.csv   # the 223-row main table
│   ├── state_legislation.csv      # 413-row state bill tracker
│   ├── summary_stats.json         # top-level aggregates
│   ├── structured_extractions.jsonl  # n=348 line-by-line coded subset
│   └── clause_extraction_analysis.json  # clause prevalence summary
├── figures/                       # PNG (web), PDF (print), SVG (vector)
├── tables/                        # pre-rendered LaTeX tables
├── docs/                          # FAQ, methodology, codebook, known gaps
├── scripts/                       # generators (rebuild tables/maps from data)
├── notebooks/                     # Jupyter examples
├── examples/                      # one R / one Python / one Stata example
├── CITATION.cff                   # citation metadata
├── LICENSE-data                   # CC-BY-4.0 for data
└── LICENSE-code                   # MIT for scripts
```
