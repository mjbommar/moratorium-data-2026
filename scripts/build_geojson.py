#!/usr/bin/env python3
"""Regenerate site/moratoria.geojson from the inventory CSV.

The map layer on the site is a point FeatureCollection, one feature per
geocoded moratorium instrument. Rows without coordinates are skipped -- those
are the aggregate meta-rows documented in docs/known-gaps.md, which are not real
geographic points.

Like summary_stats.json, this artifact previously had no generator in the
repository, so it silently fell behind the CSV. Written compact (no indent),
matching the existing file, because it is fetched by the browser.

Run from repo root:
    python3 scripts/build_geojson.py
    python3 scripts/build_geojson.py --check    # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
OUT = REPO / "site" / "moratoria.geojson"

# Property order is preserved from the published file so diffs stay readable.
STRING_PROPS = [
    ("jurisdiction", "jurisdiction"),
    ("state", "state"),
    ("state_abbrev", "state_abbrev"),
    ("jurisdiction_type", "jurisdiction_type"),
    ("enacted_status", "enacted_status"),
    ("date_enacted_iso", "date_enacted_iso"),
    ("current_end_date_iso", "current_end_date_iso"),
    ("date_enacted_uncertainty", "date_enacted_uncertainty"),
]
TRAILING_STRING_PROPS = [
    ("date_enacted", "date_enacted"),
    ("duration", "duration"),
    ("trigger", "trigger"),
]


def parse_json_array(raw: str) -> list:
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def build() -> dict:
    with open(INV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    features = []
    for row in rows:
        lat, lon = row["latitude"].strip(), row["longitude"].strip()
        if not lat or not lon:
            continue
        props: dict = {"id": row["moratorium_id"]}
        for key, column in STRING_PROPS:
            props[key] = row[column]

        days = row["duration_days"].strip()
        props["duration_days"] = int(float(days)) if days else None
        props["duration_kind"] = row["duration_kind"]
        props["sectors"] = parse_json_array(row["sectors"])
        props["trigger_categories"] = parse_json_array(row["trigger_categories"])
        for key, column in TRAILING_STRING_PROPS:
            props[key] = row[column]

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": props,
        })

    return {"type": "FeatureCollection", "features": features}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if the file is out of date")
    args = ap.parse_args()

    fresh = build()
    rendered = json.dumps(fresh, separators=(",", ":"))

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current.strip() != rendered:
            print("site/moratoria.geojson is OUT OF DATE - run scripts/build_geojson.py")
            return 1
        print("site/moratoria.geojson is current")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    skipped = sum(1 for _ in open(INV, encoding="utf-8")) - 1 - len(fresh["features"])
    print(f"Wrote {OUT.relative_to(REPO)}")
    print(f"  {len(fresh['features'])} features ({skipped} row(s) without coordinates skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
