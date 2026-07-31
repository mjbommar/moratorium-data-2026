#!/usr/bin/env python3
"""Reconcile the canonical inventory against the sibling data-center tracker.

`datacenter-paper-2026/research/analysis/moratorium_tracker.csv` is a
state-level rollup maintained by a sibling project. It carries per-state
moratorium counts and a pipe-delimited list of jurisdiction names, alongside
columns that belong to that project's own research (zoning approach, opposition
level, incentive and project counts).

This script does NOT write to that file. Its counts were built under different
inclusion criteria, and it names jurisdictions our inventory has never had -- so
overwriting it would destroy evidence rather than propagate a correction. What
it produces instead is a reconciliation report: which jurisdictions the sibling
tracker knows about that we do not, so they can be researched and, if confirmed,
added properly through the normal decision-file path.

Run from the moratorium-data-2026 repo root:
    python3 scripts/reconcile_sibling_tracker.py
    python3 scripts/reconcile_sibling_tracker.py --out work/sibling-gaps.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
TRACKER = REPO.parent / "datacenter-paper-2026" / "research" / "analysis" / "moratorium_tracker.csv"


def norm(name: str) -> str:
    """Loose jurisdiction key: drop generic descriptors and punctuation."""
    name = re.sub(r"\(.*?\)", " ", name or "")
    name = re.sub(r"\b(city|town|village|township|county|charter|of|the|parish)\b", " ", name.lower())
    return re.sub(r"[^a-z]", "", name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="write JSON report here")
    args = ap.parse_args()

    if not TRACKER.exists():
        print(f"ERROR: sibling tracker not found at {TRACKER}")
        return 2

    with open(INV, encoding="utf-8", newline="") as f:
        inv = list(csv.DictReader(f))
    with open(TRACKER, encoding="utf-8", newline="") as f:
        trk = list(csv.DictReader(f))

    counts = Counter(r["state"] for r in inv)
    ours: dict[str, set[str]] = defaultdict(set)
    for r in inv:
        ours[r["state"]].add(norm(r["jurisdiction"]))

    missing: list[dict] = []
    for row in trk:
        state = row["state"]
        listed = [j.strip() for j in (row.get("moratorium_jurisdictions") or "").split("|") if j.strip()]
        for name in listed:
            key = norm(name)
            if not key:
                continue
            if any(key == k or (len(key) > 4 and (key in k or k in key)) for k in ours.get(state, ())):
                continue
            missing.append({
                "state": state,
                "state_abbrev": row.get("state_abbr", ""),
                "jurisdiction": name,
                "our_state_count": counts.get(state, 0),
                "tracker_state_count": int(row.get("moratorium_count") or 0),
            })

    by_state: dict[str, list[str]] = defaultdict(list)
    for m in missing:
        by_state[m["state"]].append(m["jurisdiction"])

    print(f"Canonical inventory: {len(inv)} rows across {len(counts)} states")
    print(f"Sibling tracker:     {len(trk)} state rows")
    print(f"\n{len(missing)} jurisdiction(s) named by the sibling tracker with no match in our inventory,")
    print(f"across {len(by_state)} state(s):\n")
    for state in sorted(by_state):
        print(f"  {state:18s} {', '.join(sorted(by_state[state]))}")

    print("\nThese are research leads, not confirmed omissions: the sibling tracker")
    print("may use different inclusion criteria, and some entries may be stale or")
    print("already covered under a different jurisdiction name.")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "canonical_rows": len(inv),
            "tracker_state_rows": len(trk),
            "unmatched_count": len(missing),
            "by_state": {k: sorted(v) for k, v in sorted(by_state.items())},
            "items": missing,
        }, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
