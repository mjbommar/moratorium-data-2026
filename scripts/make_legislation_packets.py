#!/usr/bin/env python3
"""Split data/state_legislation.csv into per-state research packets.

The tracker's `status` column is free text captured mid-session (most of it
through April 2026). Nearly every 2026 regular session has adjourned since, so
each bill needs a final disposition. This emits one packet per state so the
refresh can be fanned out, keyed by '<STATE_ABBREV>:<bill>'.

Run from repo root:
    python3 scripts/make_legislation_packets.py --as-of 2026-07-31
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEG = REPO / "data" / "state_legislation.csv"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--as-of", required=True, help="reference date YYYY-MM-DD")
    ap.add_argument("--outdir", default=None, help="default: work/packets/legislation/")
    ap.add_argument("--state", default="", help="comma-separated abbreviations to restrict output")
    args = ap.parse_args()

    only = {s.strip().upper() for s in args.state.split(",") if s.strip()}
    outdir = Path(args.outdir) if args.outdir else REPO / "work" / "packets" / "legislation"
    outdir.mkdir(parents=True, exist_ok=True)

    with open(LEG, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    by_state: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        abbrev = row["state_abbrev"].upper()
        if only and abbrev not in only:
            continue
        by_state[abbrev].append({
            "bill_key": f"{abbrev}:{row['bill']}",
            "state": row["state"],
            "bill": row["bill"],
            "sponsors": row["sponsors"],
            "party": row["party"],
            "current_status_text": row["status"],
            "key_provisions": row["key_provisions"],
        })

    written = []
    for abbrev, bills in sorted(by_state.items()):
        bills.sort(key=lambda b: b["bill"])
        payload = {
            "packet": f"{abbrev}.json",
            "tag": "legislation",
            "state_abbrev": abbrev,
            "state": bills[0]["state"],
            "researched_as_of": args.as_of,
            "bill_count": len(bills),
            "answer_file": f"work/answers/legislation/{abbrev}.json",
            "schema": "work/schemas/legislation_decision.schema.json",
            "task": (
                "For each bill, determine its FINAL disposition as of "
                f"{args.as_of} from the state legislature's own bill-status page. "
                "Assign the typed fields (bill_status_category, last_action_date_iso, "
                "chamber_of_origin) and rewrite `status` as an action plus ISO date."
            ),
            "bills": bills,
        }
        (outdir / f"{abbrev}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        written.append((abbrev, len(bills)))

    total = sum(c for _, c in written)
    print(f"Wrote {len(written)} packet(s) to {outdir.relative_to(REPO)} covering {total} bill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
