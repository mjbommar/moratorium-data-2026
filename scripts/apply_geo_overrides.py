#!/usr/bin/env python3
"""Apply declared geocoding overrides for ambiguous jurisdiction names.

Automated geocoding resolves a bare jurisdiction name to whichever match the
provider ranks first, which is wrong whenever a state has several places with
the same name. Michigan has a Lyon Township in Oakland County and another in
Roscommon County; the geocoder picked the wrong one, putting a Detroit-area
hyperscale moratorium 130 miles north.

Every override here is declared with the evidence that settles which place is
meant, so the correction is reviewable rather than a bare coordinate edit.
Overrides may also disambiguate the `jurisdiction` label itself, which the
codebook permits ("May include disambiguating context").

Entries here should be genuine ambiguities, not cases the geocoder can handle.
When geocode_inventory.py learns to resolve a class of name, retire the overrides
it supersedes so this table keeps meaning "a human had to decide this."

Idempotent. Run from repo root:
    python3 scripts/apply_geo_overrides.py --dry-run
    python3 scripts/apply_geo_overrides.py
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"

# moratorium_id -> override
OVERRIDES: dict[str, dict] = {
    "mi-lyon-township-2026": {
        "jurisdiction": "Lyon Charter Township (Oakland County)",
        "latitude": "42.476464",
        "longitude": "-83.613258",
        "why": (
            "Michigan has a Lyon Township in Oakland County and another in Roscommon "
            "County. The record's affected project, the 'Project Flex' hyperscale campus "
            "near New Hudson, is in Oakland County, so the Oakland County township is the "
            "correct referent. Automated geocoding had returned the Roscommon County "
            "township at 44.482887 / -84.792879."
        ),
    },
    "il-city-of-effingham-2026": {
        "latitude": "39.120143",
        "longitude": "-88.543480",
        "why": (
            "geocode_inventory.py now retries with the governing-body prefix stripped, "
            "which resolves most 'City of X' rows automatically -- but not this one: a bare "
            "'Effingham, Illinois' lookup returns Effingham COUNTY first. This row is the "
            "city's Ordinance 052-2026, and the county is a distinct jurisdiction that "
            "separately declined to act for want of zoning authority."
        ),
    },
    "mi-forsyth-township-2026": {
        "latitude": "46.246523",
        "longitude": "-87.428150",
        "why": (
            "Bare 'Forsyth Township, Michigan' resolved in neither geocoder. The reporting "
            "places this action in the Gwinn / K.I. Sawyer area, i.e. Forsyth Township in "
            "Marquette County, which resolves once the county is supplied."
        ),
    },
    "ky-mercer-county-fiscal-court-undated": {
        "latitude": "37.808758",
        "longitude": "-84.876084",
        "why": (
            "Both geocoders failed on 'Mercer County Fiscal Court, Kentucky'. In Kentucky "
            "the fiscal court IS the county's governing body, so the geographic referent is "
            "simply Mercer County; resolved by querying the county name alone."
        ),
    },
}


def read_rows() -> tuple[list[dict], list[str]]:
    with open(INV, encoding="utf-8", newline="") as f:
        src = f.read()
    reader = csv.DictReader(io.StringIO(src))
    return list(reader), list(reader.fieldnames or [])


def write_rows(rows: list[dict], fieldnames: list[str]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    with open(INV, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows, fieldnames = read_rows()
    by_id = {r["moratorium_id"]: r for r in rows}

    changes: list[str] = []
    missing: list[str] = []

    for mid, override in OVERRIDES.items():
        row = by_id.get(mid)
        if row is None:
            missing.append(mid)
            continue
        for column, value in override.items():
            if column == "why":
                continue
            if column not in fieldnames:
                print(f"ERROR: unknown column {column!r} in override for {mid}")
                return 2
            if row[column] == value:
                continue
            changes.append(f"  {mid}.{column}: {row[column]!r} -> {value!r}")
            row[column] = value

    if missing:
        print(f"WARNING: {len(missing)} override target(s) not present in the inventory:")
        for mid in missing:
            print(f"  {mid}")

    if not changes:
        print("All overrides already applied.")
        return 0

    print(f"{len(changes)} cell(s):")
    for line in changes:
        print(line)

    if args.dry_run:
        print("\nDry run - nothing written.")
        return 0

    write_rows(rows, fieldnames)
    print(f"\nWrote {INV.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
