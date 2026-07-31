# Scripts

Code that regenerates this dataset's tables and figures from the source data files.

You don't need any of this to **use** the data — just download the CSVs from [`data/`](../data/). These scripts are here for transparency and so anyone can re-run the analysis.

## What's in here

| Folder / file | What it does |
|--------|---------------|
| [`generate_tables/`](generate_tables/) | Python module that regenerates every LaTeX table in [`tables/`](../tables/) from `data/moratorium_inventory.csv` and `data/clause_extraction_analysis.json`. |
| [`moratorium_maps/`](moratorium_maps/) | Python module that regenerates every map in [`figures/`](../figures/) from the inventory CSV plus the static state-classification dictionaries embedded in `data.py`. |
| `validate_dataset.py` | Checks the shipped CSVs against every rule in [`docs/codebook.md`](../docs/codebook.md) — closed vocabularies, date/duration consistency, ID uniqueness, geocoding bounds, `[VERIFY]` accounting, and agreement with `summary_stats.json`. Exits nonzero on error. |
| `normalize_vocab.py` | Idempotent normalizer for closed-vocabulary spellings. Reports every cell it changes; refuses to coerce values it has no declared mapping for. |
| `build_worklist.py` | Emits the set of rows needing research as of a given date (expired-but-in-force, stale pending, `[VERIFY]` backlog, unverified dates). |
| `make_packets.py` / `make_legislation_packets.py` | Split a worklist into per-state research packets. |
| `apply_research.py` | The only script that writes research findings into the inventory. Requires explicit answer-file paths, refuses to apply a change whose `from` value no longer matches the CSV, and writes an audit log. |
| `fetch_basemap.py` | Downloads the Census `cb_2023_us_state_5m` state boundary file the maps draw over (not vendored; ~1 MB). |
| `geocode_inventory.py` | Fills `latitude`/`longitude` for rows that lack them. |
| `make_timeline.py`, `update_state_counts.py`, `build_site.py` | Regenerate `site/timeline.svg`, the per-state Markdown counts, and the HTML site. |

## How to run

There is a `Makefile` at the repository root:

```bash
make install     # Python dependencies
make validate    # gate: check the CSVs against docs/codebook.md
make all         # regenerate every derived artifact, then validate
make check       # verify generated artifacts are in sync (CI-friendly)
```

Or run the steps directly:

```bash
pip install pandas matplotlib seaborn geopandas shapely markdown pymdown-extensions

python3 scripts/validate_dataset.py               # gate: before and after any edit
python3 scripts/fetch_basemap.py                  # one-time: state shapefile
python3 scripts/build_summary_stats.py            # data/summary_stats.json
python3 scripts/build_geojson.py                  # site/moratoria.geojson
python3 -m scripts.generate_tables                # tables/*.tex
PYTHONPATH=scripts python3 -m moratorium_maps all # figures/{pdf,svg,png}/*
python3 scripts/make_timeline.py                  # site/timeline.svg
python3 scripts/update_state_counts.py            # per-state counts in states/
python3 scripts/build_site.py                     # HTML site
```

`validate_dataset.py` is the single gate that keeps the CSVs, the codebook, and
`summary_stats.json` in agreement. Run it last as well as first.

## The refresh cycle

Rows go stale on a schedule — a moratorium expires on a known date whether or not
anyone updates the row. To refresh:

```bash
make worklist TODAY=2026-07-31   # what needs research, split into per-state packets
#   ... researchers write JSON decision files into work/answers/ ...
make apply    TODAY=2026-07-31   # merge, normalize, geocode, validate
make all      TODAY=2026-07-31   # regenerate artifacts
```

Research never edits a CSV. It emits decision files conforming to
[`work/schemas/research_decision.schema.json`](../work/schemas/research_decision.schema.json),
and `apply_research.py` merges them — refusing any change whose recorded prior
value no longer matches the CSV, so a stale answer cannot overwrite newer data.
Every applied change is logged under `work/audit/`. The whole cycle is
idempotent, so it is safe to re-run as answers land state by state.

Full description: [`docs/methodology.md`](../docs/methodology.md#phase-5-the-refresh-cycle-added-v202607).

## What's NOT in this repository

The earlier-stage pipeline that produced the source data lives in the [private working repository](https://github.com/mjbommar/moratorium-paper). That includes:

- The codex-CLI research scripts that built the per-state profiles
- The PDF classification + structured extraction scripts (LLM-driven)
- The Wayback Machine archive submission scripts
- Source verification + audit scripts

Those scripts depend on private API keys, OpenAI credits, SerpAPI credits, and access to the unpublished raw document corpus. They're not necessary to reproduce the published statistics; they're necessary to re-build the corpus from scratch.

If you want access for replication purposes, contact [Michael](mailto:michael.bommarito@gmail.com).

## License

The code in this folder is licensed under [MIT](../LICENSE-code).
