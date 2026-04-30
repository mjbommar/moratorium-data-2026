# Scripts

Code that regenerates this dataset's tables and figures from the source data files.

You don't need any of this to **use** the data — just download the CSVs from [`data/`](../data/). These scripts are here for transparency and so anyone can re-run the analysis.

## What's in here

| Folder | What it does |
|--------|---------------|
| [`generate_tables/`](generate_tables/) | Python module that regenerates every LaTeX table in [`tables/`](../tables/) from `data/moratorium_inventory.csv` and `data/clause_extraction_analysis.json`. |
| [`moratorium_maps/`](moratorium_maps/) | Python module that regenerates every map in [`figures/`](../figures/) from the inventory CSV plus the static state-classification dictionaries embedded in `data.py`. |

## How to run

```bash
# From the repository root:
pip install pandas matplotlib seaborn geopandas shapely
python -m scripts.generate_tables           # rebuilds all tables/*.tex
PYTHONPATH=scripts python -m moratorium_maps all  # rebuilds all figures/*.{pdf,svg}
```

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
