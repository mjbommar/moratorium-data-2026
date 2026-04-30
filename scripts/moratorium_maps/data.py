"""Data loading and normalization for moratorium maps."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

# Project root (two levels up from this file: src/moratorium_maps/data.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "research" / "analysis"
GEO_DIR = PROJECT_ROOT / "data" / "geo"
SHAPEFILE = GEO_DIR / "cb_2023_us_state_5m" / "cb_2023_us_state_5m.shp"

# Canonical 50 states + DC
STATES_50 = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

ABBREV_TO_NAME: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

NAME_TO_ABBREV = {v: k for k, v in ABBREV_TO_NAME.items()}


def load_states_geo(*, lower48_only: bool = False) -> gpd.GeoDataFrame:
    """Load US state boundaries from Census TIGER shapefile.

    Returns GeoDataFrame with columns: NAME, STUSPS, STATEFP, geometry
    Filtered to 50 states + DC (no territories).
    """
    gdf = gpd.read_file(SHAPEFILE)
    # Filter to 50 states + DC
    gdf = gdf[gdf["STUSPS"].isin(STATES_50)].copy()
    if lower48_only:
        gdf = gdf[~gdf["STUSPS"].isin({"AK", "HI"})].copy()
    return gdf[["NAME", "STUSPS", "STATEFP", "geometry"]]


def load_moratorium_inventory() -> pd.DataFrame:
    """Load the moratorium inventory CSV."""
    df = pd.read_csv(DATA_DIR / "moratorium_inventory.csv")
    return df


def moratorium_counts_by_state() -> pd.DataFrame:
    """Aggregate moratorium counts per state.

    Returns DataFrame with columns: state_abbrev, state_name, count
    Includes all 50 states (0 for states with no moratoria).
    """
    inv = load_moratorium_inventory()
    counts = inv.groupby("state_abbrev").size().reset_index(name="count")

    # Ensure all 50 states present
    all_states = pd.DataFrame(
        [(abbr, name) for abbr, name in ABBREV_TO_NAME.items()],
        columns=["state_abbrev", "state_name"],
    )
    result = all_states.merge(counts, on="state_abbrev", how="left")
    result["count"] = result["count"].fillna(0).astype(int)
    return result


def load_moratorium_analysis() -> dict:
    """Load the moratorium analysis JSON."""
    with open(DATA_DIR / "moratorium-analysis.json") as f:
        return json.load(f)


# --- Legal authority classification ---
# Source: appendix-b-state-authority.tex and Section 4

AUTHORITY_TYPE: dict[str, str] = {
    "AL": "Implied",    "AK": "Implied",    "AZ": "Express",
    "AR": "Implied",    "CA": "Express",    "CO": "Implied",
    "CT": "Implied",    "DE": "Implied",    "FL": "Implied",
    "GA": "Implied",    "HI": "Implied",    "ID": "Express",
    "IL": "Implied",    "IN": "Express",    "IA": "Implied",
    "KS": "Implied",    "KY": "Express",    "LA": "Implied",
    "ME": "Express",    "MD": "Implied",    "MA": "Implied",
    "MI": "Implied",    "MN": "Express",    "MS": "Implied",
    "MO": "Implied",    "MT": "Express",    "NE": "Implied",
    "NV": "Implied",    "NH": "Express",    "NJ": "Restricted",
    "NM": "Implied",    "NY": "Implied",    "NC": "Express",
    "ND": "Implied",    "OH": "Implied",    "OK": "Implied",
    "OR": "Express",    "PA": "Prohibited", "RI": "Express",
    "SC": "Procedural", "SD": "Express",    "TN": "Implied",
    "TX": "Express",    "UT": "Express",    "VT": "Express",
    "VA": "Prohibited", "WA": "Express",    "WV": "Restricted",
    "WI": "Express",    "WY": "Implied",    "DC": "Implied",
}


# --- Dillon's Rule vs Home Rule ---
# Three-way classification based on Wikipedia "Home rule in the United States"
# and state constitutional/statutory provisions.
# "Home Rule" = home rule granted, Dillon's Rule does NOT apply
# "Dillon"    = no home rule, Dillon's Rule applies
# "Hybrid"    = home rule for some classes (e.g. cities) but Dillon's Rule
#               for others (e.g. townships, counties)

HOME_RULE_TYPE: dict[str, str] = {
    "AL": "Hybrid",      "AK": "Home Rule",  "AZ": "Hybrid",
    "AR": "Hybrid",      "CA": "Hybrid",     "CO": "Hybrid",
    "CT": "Hybrid",      "DE": "Dillon",     "FL": "Home Rule",
    "GA": "Hybrid",      "HI": "Hybrid",     "ID": "Hybrid",
    "IL": "Hybrid",      "IN": "Hybrid",     "IA": "Home Rule",
    "KS": "Hybrid",      "KY": "Hybrid",     "LA": "Hybrid",
    "ME": "Hybrid",      "MD": "Hybrid",     "MA": "Home Rule",
    "MI": "Hybrid",      "MN": "Hybrid",     "MS": "Dillon",
    "MO": "Hybrid",      "MT": "Dillon",     "NE": "Hybrid",
    "NV": "Dillon",      "NH": "Dillon",     "NJ": "Home Rule",
    "NM": "Hybrid",      "NY": "Hybrid",     "NC": "Hybrid",
    "ND": "Hybrid",      "OH": "Hybrid",     "OK": "Dillon",
    "OR": "Home Rule",   "PA": "Hybrid",     "RI": "Hybrid",
    "SC": "Home Rule",   "SD": "Hybrid",     "TN": "Hybrid",
    "TX": "Hybrid",      "UT": "Home Rule",  "VT": "Dillon",
    "VA": "Dillon",      "WA": "Hybrid",     "WV": "Hybrid",
    "WI": "Hybrid",      "WY": "Dillon",     "DC": "Home Rule",
}


# --- Statutory duration limits (in days) ---
# Only states with express statutes that specify duration
STATUTORY_DURATION_DAYS: dict[str, int | None] = {
    "AZ": 120,    "CA": 730,    "ID": 365,    "IN": 365,
    "KY": 365,    "ME": 180,    "MN": 365,    "MT": 365,
    "NH": 365,    "OR": 730,    "RI": 365,    "SD": 365,
    "TX": 120,    "UT": 180,    "VT": 730,    "WA": 365,
    "WI": 548,    # 18 months = 12 + 6 month extension
}


# --- Preemption posture ---
PREEMPTION_TYPE: dict[str, str] = {
    "WV": "Full Preemption",
    "MI": "Incentive-Linked",
    "IL": "Sector Restriction",  # solar/wind moratorium ban
    "NV": "Sector Restriction",  # wind energy preemption
    "AR": "Sector Restriction",  # digital asset mining preemption
    "OK": "Sector Restriction",  # digital asset mining preemption
    "MT": "Sector Restriction",  # digital asset mining protection
    "TN": "Sector Restriction",  # energy infrastructure preemption
    "FL": "Sector Restriction",  # post-hurricane moratorium ban
    "VT": "Sector Restriction",  # PUC exclusive jurisdiction for energy
}


def authority_df() -> pd.DataFrame:
    """Return a DataFrame of legal authority classifications for all states."""
    rows = []
    for abbr, name in ABBREV_TO_NAME.items():
        rows.append({
            "state_abbrev": abbr,
            "state_name": name,
            "authority_type": AUTHORITY_TYPE.get(abbr, "Unknown"),
            "home_rule_type": HOME_RULE_TYPE.get(abbr, "Unknown"),
            "preemption_type": PREEMPTION_TYPE.get(abbr, "None"),
            "statutory_duration_days": STATUTORY_DURATION_DAYS.get(abbr),
        })
    return pd.DataFrame(rows)
