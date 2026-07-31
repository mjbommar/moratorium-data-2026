#!/usr/bin/env python3
"""Push the published inventory back to the private working repository.

Direction of flow, which had drifted and is worth stating plainly:

    moratorium-paper/research/   -- original research corpus, agentic pipeline
             |                      (document collection, classification,
             |                       structured extraction)
             v
    moratorium-data-2026/data/   -- THE CANONICAL INVENTORY
             |                      cleaning, dedup, typed columns, geocoding,
             |                      status refresh, and validation all happen
             |                      here, and only here
             v
    moratorium-paper/research/analysis/moratorium_inventory.csv  (mirror)

The paper repository's copy is a *mirror for paper builds*, not a second source
of truth. Before this script existed it had fallen to 108 rows on the original
15-column schema while the published file had moved to 295 rows and 25 columns,
so any figure regenerated from it silently used year-old data.

The published schema is a strict superset of the paper's, so consumers that read
by column name keep working.

Run from the moratorium-data-2026 repo root:
    python3 scripts/sync_upstream.py --dry-run
    python3 scripts/sync_upstream.py
"""

from __future__ import annotations

import argparse
import csv
import io
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "data" / "moratorium_inventory.csv"
LEG_SOURCE = REPO / "data" / "state_legislation.csv"

UPSTREAM = REPO.parent / "moratorium-paper"
TARGET = UPSTREAM / "research" / "analysis" / "moratorium_inventory.csv"
LEG_TARGET = UPSTREAM / "research" / "analysis" / "state_legislation.csv"

PAIRS = [(SOURCE, TARGET), (LEG_SOURCE, LEG_TARGET)]


def describe(path: Path) -> str:
    if not path.exists():
        return "absent"
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return f"{len(rows)} rows x {len(reader.fieldnames or [])} cols"


def superset_ok(src: Path, dst: Path) -> tuple[bool, list[str]]:
    """True when the source schema contains every column the target has."""
    if not dst.exists():
        return True, []
    with open(src, encoding="utf-8", newline="") as f:
        src_cols = set(csv.DictReader(f).fieldnames or [])
    with open(dst, encoding="utf-8", newline="") as f:
        dst_cols = set(csv.DictReader(f).fieldnames or [])
    lost = sorted(dst_cols - src_cols)
    return not lost, lost


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-backup", action="store_true", help="skip writing .bak files")
    args = ap.parse_args()

    if not UPSTREAM.exists():
        print(f"ERROR: upstream repository not found at {UPSTREAM}")
        return 2

    plan = []
    for src, dst in PAIRS:
        if not src.exists():
            print(f"ERROR: source missing: {src}")
            return 2
        ok, lost = superset_ok(src, dst)
        if not ok:
            print(f"REFUSING to sync {dst.name}: target has columns the source lacks: {lost}")
            print("Reconcile the schemas by hand rather than losing data.")
            return 1
        plan.append((src, dst))
        print(f"{dst.relative_to(UPSTREAM.parent)}")
        print(f"    {describe(dst)}  ->  {describe(src)}")

    if args.dry_run:
        print("\nDry run - nothing written.")
        return 0

    for src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not args.no_backup:
            backup = dst.with_suffix(dst.suffix + ".bak")
            shutil.copy2(dst, backup)
            print(f"Backed up {backup.name}")
        shutil.copy2(src, dst)
        print(f"Wrote {dst}")

    print("\nThe canonical inventory now lives in moratorium-data-2026/data/.")
    print("Regenerate any paper figures from the refreshed mirror before citing them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
