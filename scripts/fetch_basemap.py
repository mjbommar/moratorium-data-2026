#!/usr/bin/env python3
"""Download the Census state boundary shapefile the map generators need.

The map figures are drawn over the Census cartographic boundary file
`cb_2023_us_state_5m`. It is a ~3 MB binary from a stable public URL, so it is
fetched on demand rather than vendored into the repository.

Run from repo root:
    python3 scripts/fetch_basemap.py
    python3 scripts/fetch_basemap.py --force   # re-download

Downloads to data/geo/cb_2023_us_state_5m/. That directory is ignored by git.
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GEO_DIR = REPO / "data" / "geo"
TARGET_DIR = GEO_DIR / "cb_2023_us_state_5m"
SHAPEFILE = TARGET_DIR / "cb_2023_us_state_5m.shp"
URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_5m.zip"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-download even if present")
    args = ap.parse_args()

    if SHAPEFILE.exists() and not args.force:
        print(f"Already present: {SHAPEFILE.relative_to(REPO)}")
        return 0

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL} ...")
    try:
        with urllib.request.urlopen(URL, timeout=120) as resp:
            payload = resp.read()
    except Exception as exc:
        print(f"ERROR: download failed: {exc}")
        print(f"Fetch it manually and unzip into {TARGET_DIR.relative_to(REPO)}/")
        return 1

    print(f"  {len(payload) / 1_000_000:.1f} MB, extracting ...")
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        zf.extractall(TARGET_DIR)

    if not SHAPEFILE.exists():
        print(f"ERROR: archive did not contain {SHAPEFILE.name}")
        return 1

    print(f"Ready: {SHAPEFILE.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
