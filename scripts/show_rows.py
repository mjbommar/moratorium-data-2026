#!/usr/bin/env python3
"""Print inventory rows for a state (or one moratorium_id) as JSON.

Research answer files must copy the existing value of every changed field
verbatim into `changes.<column>.from`; apply_research.py refuses a change
whose `from` no longer matches the CSV. Reading the CSV by eye is where those
mismatches come from, so this prints the row exactly as the CSV holds it.

Run from repo root:
    python3 scripts/show_rows.py --state NV            # every NV row, full
    python3 scripts/show_rows.py --state NV --list     # id, jurisdiction, status only
    python3 scripts/show_rows.py --id nv-reno-2026
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

INVENTORY = Path(__file__).resolve().parents[1] / "data" / "moratorium_inventory.csv"
LIST_COLUMNS = (
    "moratorium_id", "jurisdiction", "jurisdiction_type", "enacted_status",
    "date_enacted_iso", "duration_days", "duration_kind", "current_end_date_iso", "sectors",
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", help="USPS abbreviation, e.g. NV")
    ap.add_argument("--id", help="a single moratorium_id")
    ap.add_argument("--list", action="store_true", help="compact one-line-per-row listing")
    args = ap.parse_args()
    if not args.state and not args.id:
        ap.error("give --state or --id")

    with INVENTORY.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if args.state:
        rows = [r for r in rows if r["state_abbrev"] == args.state.upper()]
    if args.id:
        rows = [r for r in rows if r["moratorium_id"] == args.id]
    if not rows:
        print("no rows matched", file=sys.stderr)
        return 1
    if args.list:
        for r in rows:
            print(json.dumps({c: r[c] for c in LIST_COLUMNS}, ensure_ascii=False))
    else:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
