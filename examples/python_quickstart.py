"""Quickstart: load the moratorium inventory and answer common questions.

Run with:  python examples/python_quickstart.py
Or with the URL directly (no clone required):

    import pandas as pd
    URL = "https://raw.githubusercontent.com/mjbommar/moratorium-data-2026/main/data/moratorium_inventory.csv"
    df = pd.read_csv(URL)
"""
from pathlib import Path
import pandas as pd

CSV = Path(__file__).resolve().parent.parent / "data" / "moratorium_inventory.csv"
df = pd.read_csv(CSV)

print(f"Total moratoria: {len(df)}")
print(f"States with moratoria: {df['state'].nunique()}")
print()

print("Top 10 states by moratorium count:")
print(df["state"].value_counts().head(10).to_string())
print()

print("Most common jurisdiction types:")
print(df["jurisdiction_type"].value_counts().head().to_string())
print()

# Approximate sector mentions — the exact sector is encoded in the trigger / legal_basis text
def has_sector(s, kw):
    text = " ".join(filter(None, [s.get("trigger",""), s.get("legal_basis",""), s.get("jurisdiction","")])).lower()
    return any(k in text for k in kw)

mask_dc = df.apply(lambda r: has_sector(r, ["data center", "data centre"]), axis=1)
mask_crypto = df.apply(lambda r: has_sector(r, ["crypto", "mining", "digital asset"]), axis=1)
mask_bess = df.apply(lambda r: has_sector(r, ["battery", "bess", "energy storage"]), axis=1)
mask_solar = df.apply(lambda r: has_sector(r, ["solar"]), axis=1)
mask_wind = df.apply(lambda r: has_sector(r, ["wind"]), axis=1)

print("Sector mention counts (one row may mention multiple sectors):")
print(f"  Data center: {mask_dc.sum()}")
print(f"  Cryptocurrency mining: {mask_crypto.sum()}")
print(f"  Battery storage: {mask_bess.sum()}")
print(f"  Solar: {mask_solar.sum()}")
print(f"  Wind: {mask_wind.sum()}")
print()

# Year of adoption — extract from messy date strings
df["year"] = df["date_enacted"].str.extract(r"(20\d{2})")[0]
print("Adoptions by year (where parseable):")
print(df["year"].value_counts().sort_index().to_string())
