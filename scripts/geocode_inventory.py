#!/usr/bin/env python3
"""Geocode every jurisdiction in moratorium_inventory.csv.

Strategy:
  1. Try Census Geocoder OneLine API (free, no API key, fast bulk endpoint).
  2. Fall back to Nominatim (OSM) for jurisdictions Census can't resolve
     (counties without a defined city, tribal land, etc.).
  3. For jurisdictions that fail both, leave lat/lon empty and report.

Adds two columns to the inventory CSV:
  - latitude  (float, WGS84)
  - longitude (float, WGS84)

Idempotent: re-runs only fill in empty lat/lon cells. Pass --force to refetch.

Usage:
    uv run scripts/geocode_inventory.py
    uv run scripts/geocode_inventory.py --force
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
INV = ROOT / "data" / "moratorium_inventory.csv"

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NOM_URL = "https://nominatim.openstreetmap.org/search"

UA = "moratorium-data-2026/1.0 (https://github.com/mjbommar/moratorium-data-2026)"

# Strip these from jurisdiction strings to improve match rate
PREFIX_RX = re.compile(
    r"^(city|town|village|township|county|borough|parish|charter\s+township)\s+of\s+",
    re.I,
)
SUFFIX_RX = re.compile(r"\s*[\(\[].*$")  # parenthetical context
DESC_RX = re.compile(r"\s+-\s+.*$")  # "Name - description"


def clean_jurisdiction(j: str) -> str:
    s = (j or "").strip()
    s = SUFFIX_RX.sub("", s)
    s = DESC_RX.sub("", s)
    return s.strip()


def census_geocode(jurisdiction: str, state: str) -> tuple[float, float] | None:
    """Census OneLine endpoint. Free, no API key."""
    j = clean_jurisdiction(jurisdiction)
    address = f"{j}, {state}, USA"
    params = {"address": address, "benchmark": "Public_AR_Current", "format": "json"}
    url = CENSUS_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            c = matches[0].get("coordinates", {})
            x, y = c.get("x"), c.get("y")
            if x is not None and y is not None:
                return float(y), float(x)  # (lat, lon)
    except Exception:
        pass
    return None


def nominatim_geocode(jurisdiction: str, state: str) -> tuple[float, float] | None:
    """OSM Nominatim. Rate-limited to 1 req/sec by usage policy."""
    j = clean_jurisdiction(jurisdiction)
    # Try a structured query first
    params = {
        "q": f"{j}, {state}, USA",
        "format": "json",
        "limit": "1",
        "countrycodes": "us",
    }
    url = NOM_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="Re-geocode all rows (default: skip rows that already have lat/lon)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only process the first N rows (for testing)")
    args = parser.parse_args()

    rows = list(csv.DictReader(INV.open()))
    fields = list(rows[0].keys()) if rows else []
    if "latitude" not in fields:
        fields.append("latitude")
    if "longitude" not in fields:
        fields.append("longitude")

    n_total = len(rows)
    n_skip = n_census = n_nom = n_fail = 0
    failed_jurisdictions = []

    for i, r in enumerate(rows):
        if args.limit and i >= args.limit:
            break
        if not args.force and r.get("latitude") and r.get("longitude"):
            n_skip += 1
            continue
        if r.get("jurisdiction_type", "").lower() == "state":
            # State-level entries — geocode the state itself
            jur = r.get("state", "")
        else:
            jur = r.get("jurisdiction", "")
        st = r.get("state", "")
        if not jur or not st:
            n_fail += 1
            r["latitude"] = ""
            r["longitude"] = ""
            continue

        # Try Census first
        result = census_geocode(jur, st)
        if result:
            n_census += 1
        else:
            # Nominatim fallback
            time.sleep(1.1)  # respect 1 req/sec
            result = nominatim_geocode(jur, st)
            if result:
                n_nom += 1
            else:
                n_fail += 1
                failed_jurisdictions.append(f"{jur}, {st}")

        if result:
            r["latitude"] = f"{result[0]:.6f}"
            r["longitude"] = f"{result[1]:.6f}"
        else:
            r["latitude"] = ""
            r["longitude"] = ""

        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{n_total}] census={n_census} nominatim={n_nom} failed={n_fail}",
                  file=sys.stderr)

    # Save
    with INV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"=== Geocoding complete ===")
    print(f"  Total rows:           {n_total}")
    print(f"  Already had lat/lon:  {n_skip}")
    print(f"  Census matched:       {n_census}")
    print(f"  Nominatim matched:    {n_nom}")
    print(f"  Failed both:          {n_fail}")
    if failed_jurisdictions:
        print(f"\nFailed jurisdictions (manual review needed):")
        for j in failed_jurisdictions[:30]:
            print(f"  - {j}")
        if len(failed_jurisdictions) > 30:
            print(f"  ... and {len(failed_jurisdictions) - 30} more")


if __name__ == "__main__":
    main()
