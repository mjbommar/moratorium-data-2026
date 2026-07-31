#!/usr/bin/env python3
"""Regenerate data/summary_stats.json from the shipped CSVs.

This file is the machine-readable headline-numbers endpoint, and until now it
had no generator in this repository -- which is exactly why it drifted out of
agreement with the CSVs. Every value here is derived; nothing is hand-entered.

Two things are deliberately carried forward from the existing file rather than
recomputed, because they are editorial rather than derivable:

  * `state_details[<state>].activity_notes` -- qualifying context for special
    cases (New Jersey has no formal moratoria but heavy non-moratorium
    restriction activity, so a bare "None" would mislead).
  * `state_details[<state>].file` -- the per-state page filename, when the page
    exists in states/.

The two `top_states_by_*` keys use different JSON shapes (list of objects vs
list of pairs). That inconsistency predates this script; it is preserved so
existing consumers keep working.

Run from repo root:
    python3 scripts/build_summary_stats.py
    python3 scripts/build_summary_stats.py --check    # exit 1 if out of date
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"
STATS = REPO / "data" / "summary_stats.json"
SWEEP = REPO / "data" / "sweep_coverage.json"
STATES_DIR = REPO / "states"

VERIFY_RE = re.compile(r"\[VERIFY", re.IGNORECASE)

ALL_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming",
]


def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def row_has_verify(row: dict) -> bool:
    return any(VERIFY_RE.search(v or "") for v in row.values())


def build() -> dict:
    inv = load(INV)
    leg = load(LEG)
    previous = json.loads(STATS.read_text(encoding="utf-8")) if STATS.exists() else {}
    prev_details = previous.get("state_details", {})

    inv_by_state = Counter(r["state"] for r in inv)
    leg_by_state = Counter(r["state"] for r in leg)

    # activity_level is a per-state attribute repeated on every row; take the
    # value from the inventory when the state has rows, else from legislation.
    activity: dict[str, str] = {}
    for r in inv:
        activity.setdefault(r["state"], r["activity_level"])
    for r in leg:
        activity.setdefault(r["state"], r["activity_level"])

    abbrev: dict[str, str] = {}
    for r in inv + leg:
        abbrev.setdefault(r["state"], r["state_abbrev"])

    state_details = {}
    for state in ALL_STATES:
        slug = state.lower().replace(" ", "-")
        detail = {
            "abbreviation": abbrev.get(state, ""),
            "activity_level": activity.get(state, "None"),
            "local_moratoria_count": inv_by_state.get(state, 0),
            "state_bills_count": leg_by_state.get(state, 0),
        }
        page = STATES_DIR / f"{slug}.md"
        if page.exists():
            detail["file"] = f"{slug}.md"
        elif prev_details.get(state, {}).get("file"):
            detail["file"] = prev_details[state]["file"]
        # Preserve editorial qualifying context.
        notes = prev_details.get(state, {}).get("activity_notes")
        if notes:
            detail["activity_notes"] = notes
        state_details[state] = detail

    states_with = sum(1 for s in ALL_STATES if inv_by_state.get(s, 0) > 0)

    # Surface sweep coverage alongside the counts. A consumer reading
    # states_without_moratoria has no way, from the inventory alone, to tell a
    # state that was searched and found empty from one nobody searched.
    sweep = {}
    if SWEEP.exists():
        raw = json.loads(SWEEP.read_text(encoding="utf-8"))
        windows = raw.get("windows", [])
        if windows:
            latest = windows[-1]
            swept = latest.get("swept_states", [])
            sweep = {
                "window": latest.get("window"),
                "swept_state_count": len(swept),
                "swept_states": swept,
                "swept_states_with_no_adoptions_in_window": latest.get(
                    "swept_states_with_no_adoptions_in_window", []
                ),
                "unswept_state_count": len(ALL_STATES) - len(swept),
                "caveat": raw.get("unswept_caveat", ""),
            }

    return {
        "total_states": len(ALL_STATES),
        "total_local_moratoria": len(inv),
        "total_state_bills": len(leg),
        "states_by_activity_level": dict(
            Counter(state_details[s]["activity_level"] for s in ALL_STATES).most_common()
        ),
        "moratoria_with_verify_tags": sum(1 for r in inv if row_has_verify(r)),
        "moratoria_without_verify_tags": sum(1 for r in inv if not row_has_verify(r)),
        "states_with_moratoria": states_with,
        "states_without_moratoria": len(ALL_STATES) - states_with,
        # Shape preserved from the existing file: objects here, pairs below.
        "top_states_by_moratoria": [
            {"state": s, "count": c} for s, c in inv_by_state.most_common(10)
        ],
        "top_states_by_bills": [[s, c] for s, c in leg_by_state.most_common(15)],
        "state_details": state_details,
        "enacted_status_breakdown": dict(
            Counter(r["enacted_status"] for r in inv).most_common()
        ),
        "sweep_coverage": sweep,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if the file is out of date")
    args = ap.parse_args()

    fresh = build()
    rendered = json.dumps(fresh, indent=2) + "\n"

    if args.check:
        current = STATS.read_text(encoding="utf-8") if STATS.exists() else ""
        if current != rendered:
            print("summary_stats.json is OUT OF DATE - run scripts/build_summary_stats.py")
            return 1
        print("summary_stats.json is current")
        return 0

    STATS.write_text(rendered, encoding="utf-8")
    print(f"Wrote {STATS.relative_to(REPO)}")
    print(f"  {fresh['total_local_moratoria']} moratoria across {fresh['states_with_moratoria']} states")
    print(f"  {fresh['total_state_bills']} state bills")
    print(f"  enacted_status: {fresh['enacted_status_breakdown']}")
    print(f"  rows with [VERIFY]: {fresh['moratoria_with_verify_tags']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
