#!/usr/bin/env python3
"""Refresh data/sweep_coverage.json from the research repository's sweep output.

`sweep_coverage.json` is what lets a reader tell "we searched this state and found
nothing" from "nobody has searched this state". That distinction is only honest if
the list of swept states actually tracks the sweep, so this derives it rather than
leaving it hand-maintained.

A state counts as swept for a window when the private research repository holds a
chronology note for every month in that window. The notes themselves are not
published (they are working research), but which states have them is a fact about
coverage that belongs in the public release.

The `swept_states_with_no_adoptions_in_window` list is NOT derived: a state can be
swept, find activity, and still have that activity turn out to be out of scope --
Arizona is exactly that case, where the only hit was a tax-incentive freeze. That
list stays curated, and this script only warns when it contradicts the inventory.
The warning compares against adoptions DATED INSIDE the window, not mere row
presence: Idaho belongs on the list despite carrying a 2025 Kootenai County row,
because it adopted nothing new during the window.

Run from repo root (requires the sibling research repo):
    python3 scripts/update_sweep_coverage.py --window 2026-05-01/2026-07-31
    python3 scripts/update_sweep_coverage.py --check
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SWEEP = REPO / "data" / "sweep_coverage.json"
INV = REPO / "data" / "moratorium_inventory.csv"
CHRONOLOGY = REPO.parent / "moratorium-paper" / "research" / "sections" / "chronology"

FILENAME_RE = re.compile(r"^([a-z]{2})-(\d{4}-\d{2})\.md$")


def months_in_window(window: str) -> list[str]:
    start, end = window.split("/")
    sy, sm = int(start[:4]), int(start[5:7])
    ey, em = int(end[:4]), int(end[5:7])
    out, y, m = [], sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def swept_states(window: str) -> list[str]:
    if not CHRONOLOGY.exists():
        return []
    have: dict[str, set[str]] = defaultdict(set)
    for path in CHRONOLOGY.glob("*.md"):
        m = FILENAME_RE.match(path.name)
        if m:
            have[m.group(1).upper()].add(m.group(2))
    wanted = set(months_in_window(window))
    return sorted(s for s, got in have.items() if wanted <= got)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--window", default=None, help="YYYY-MM-DD/YYYY-MM-DD; default: the latest window on file")
    ap.add_argument("--check", action="store_true", help="report drift without writing")
    args = ap.parse_args()

    payload = json.loads(SWEEP.read_text(encoding="utf-8"))
    windows = payload.get("windows", [])
    if not windows:
        print("ERROR: sweep_coverage.json has no windows")
        return 2

    target = windows[-1]
    if args.window:
        match = [w for w in windows if w.get("window") == args.window]
        if not match:
            print(f"ERROR: no window {args.window!r} in sweep_coverage.json")
            return 2
        target = match[0]

    if not CHRONOLOGY.exists():
        print(f"Research repository not available at {CHRONOLOGY}; cannot derive coverage.")
        print("This is expected outside the maintainer's environment; the committed list stands.")
        return 0

    derived = swept_states(target["window"])
    recorded = target.get("swept_states", [])
    added = [s for s in derived if s not in recorded]
    dropped = [s for s in recorded if s not in derived]

    print(f"Window {target['window']}")
    print(f"  recorded: {len(recorded)} state(s)")
    print(f"  derived:  {len(derived)} state(s)")
    if added:
        print(f"  newly complete: {', '.join(added)}")
    if dropped:
        print(f"  recorded but not derivable: {', '.join(dropped)} (left in place)")

    # Sanity-check the curated empty list against the inventory.
    with open(INV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    have_rows = {r["state_abbrev"] for r in rows}
    claimed_empty = target.get("swept_states_with_no_adoptions_in_window", [])
    # A state can legitimately appear here and still have inventory rows: the
    # claim is about adoptions IN THE WINDOW, not about the state ever having a
    # moratorium. So check adoptions dated inside the window, not row presence.
    lo, hi = target["window"].split("/")
    adopted_in_window = {
        r["state_abbrev"] for r in rows
        if lo <= (r["date_enacted_iso"] or "9999") <= hi
    }
    contradicted = [s for s in claimed_empty if s in adopted_in_window]
    if contradicted:
        print(f"  WARNING: listed as having no adoptions in the window but the inventory "
              f"has one dated inside it: {', '.join(contradicted)} -- review before publishing")

    if args.check:
        return 1 if (added or dropped or contradicted) else 0

    if not added and not dropped:
        print("  already current")
        return 0

    # Union: never drop a state that was genuinely swept just because its notes moved.
    target["swept_states"] = sorted(set(recorded) | set(derived))
    SWEEP.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {SWEEP.relative_to(REPO)} ({len(target['swept_states'])} swept states)")
    print("Re-run scripts/build_summary_stats.py to propagate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
