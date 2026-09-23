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
    "mi-caledonia-township-undated": {
        "latitude": "42.812169",
        "longitude": "-85.487564",
        "why": (
            "Michigan has a Caledonia Township in Alcona County and Caledonia Charter Township "
            "in Kent County. The moratorium is the Kent County township's (its minutes and the "
            "Grand Rapids-area coverage); automated geocoding had returned the Alcona County "
            "township. Found in QA round 3 (2026-09-23)."
        ),
    },
    "mi-lincoln-township-2026": {
        "latitude": "42.0178900",
        "longitude": "-86.5049670",
        "why": (
            "Same-name township: the row's evidence places it in Berrien County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Lincoln Township (Berrien County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-porter-township-2026": {
        "latitude": "41.8311645",
        "longitude": "-85.8183348",
        "why": (
            "Same-name township: the row's evidence places it in Cass County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Porter Township (Cass County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-washington-township-2026": {
        "latitude": "42.7570924",
        "longitude": "-83.0373036",
        "why": (
            "Same-name township: the row's evidence places it in Macomb County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Washington Township (Macomb County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "oh-richfield-township-2026": {
        "latitude": "41.6905055",
        "longitude": "-83.8301363",
        "why": (
            "Same-name township: the row's evidence places it in Lucas County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Richfield Township (Lucas County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "oh-scioto-township-2026": {
        "latitude": "39.7567168",
        "longitude": "-83.0802156",
        "why": (
            "Same-name township: the row's evidence places it in Pickaway County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Scioto Township (Pickaway County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-buffalo-township-2026": {
        "latitude": "40.7149082",
        "longitude": "-79.7385009",
        "why": (
            "Same-name township: the row's evidence places it in Butler County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Buffalo Township (Butler County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-butler-township-2026": {
        "latitude": "41.0395791",
        "longitude": "-75.9880458",
        "why": (
            "Same-name township: the row's evidence places it in Luzerne County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Butler Township (Luzerne County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-center-township-2026": {
        "latitude": "40.9329281",
        "longitude": "-79.9265663",
        "why": (
            "Same-name township: the row's evidence places it in Butler County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Center Township (Butler County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-smithfield-township-2026": {
        "latitude": "41.0073171",
        "longitude": "-75.1324962",
        "why": (
            "Same-name township: the row's evidence places it in Monroe County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Smithfield Township (Monroe County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-warrington-township-2026": {
        "latitude": "40.0656653",
        "longitude": "-76.9368682",
        "why": (
            "Same-name township: the row's evidence places it in York County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Warrington Township (York County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-howard-charter-township-cass-county-undated": {
        "latitude": "41.855143",
        "longitude": "-86.165948",
        "why": (
            "'Howard Charter Township' is not how the gazetteer names the Cass County "
            "township (it is plain 'Howard Township'), so the county-qualified query still "
            "fell through to a Grand Traverse County match. Resolved by hand with Nominatim "
            "on 2026-09-23 (QA round 1)."
        ),
    },
    "ak-houston-undated": {
        "latitude": "61.630278",
        "longitude": "-149.818055",
        "why": (
            "Neither geocoder resolved bare 'Houston, Alaska' (Texas wins the name). The instrument is the City of Houston in the Matanuska-Susitna Borough (Ordinance 26-20). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ca-patterson-2026": {
        "latitude": "37.471623",
        "longitude": "-121.129695",
        "why": (
            "Bare 'Patterson, California' failed both geocoders. The row is the City of Patterson, Stanislaus County (its council adopted the 2026-07-16 urgency ordinance). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ga-chatham-county-2026": {
        "latitude": "31.966889",
        "longitude": "-81.062601",
        "why": (
            "'Chatham County, Georgia' failed the Census geocoder (it resolves places, not counties) and Nominatim ranked North Carolina's Chatham County first in bulk mode. The instrument is the Savannah-area county. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ga-toccoa-2026": {
        "latitude": "34.577437",
        "longitude": "-83.332881",
        "why": (
            "Bare 'Toccoa' failed both geocoders; the row is the City of Toccoa, Stephens County. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ky-boyd-county-fiscal-court-2026": {
        "latitude": "38.360893",
        "longitude": "-82.694593",
        "why": (
            "'Fiscal Court' is the Kentucky county legislative body, not a place, and defeated both geocoders. The referent is Boyd County (Ashland area). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "oh-swancreek-township-fulton-county-2026": {
        "latitude": "41.537719",
        "longitude": "-83.940839",
        "why": (
            "The township spells itself 'Swancreek' but the gazetteer entry is 'Swan Creek Township, Fulton County'; neither geocoder bridged the spelling. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "mi-park-township-2026": {
        "jurisdiction": "Park Township (St. Joseph County)",
        "latitude": "42.016737",
        "longitude": "-85.586519",
        "why": (
            "Michigan has a Park Township in Ottawa County (Holland area) and another in "
            "St. Joseph County. The moratorium's own record is park-township.org, whose "
            "May 13 and September 9, 2026 board minutes carry St. Joseph County reports, so "
            "the St. Joseph County township is the referent. Automated geocoding had "
            "returned the Ottawa County township at 42.812025 / -86.174118 (2026-09-23 refresh)."
        ),
    },
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
    "pa-brookville-borough-2026": {
        "latitude": "41.160435",
        "longitude": "-79.079470",
        "why": (
            "The 'Borough' suffix defeated both geocoders. Pennsylvania boroughs are "
            "incorporated municipalities, so the referent is simply the place: Brookville, "
            "Jefferson County."
        ),
    },
    "tn-unincorporated-hamilton-county-2026": {
        "latitude": "35.175564",
        "longitude": "-85.194079",
        "why": (
            "'Unincorporated Hamilton County' has no gazetteer entry -- it is the part of the "
            "county outside its municipalities, which is the moratorium's actual scope. The "
            "county centroid is the honest representative point; it is not a municipal boundary."
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
