#!/usr/bin/env python3
"""Update per-state status counts in states/README.md and individual state pages.

Source of truth is data/moratorium_inventory.csv. The script:
- Recomputes per-state {in_force, pending, past, total} from `enacted_status`.
- Patches the headline summary line at the top of each states/<slug>.md.
- Patches the headline summary block + per-state table in states/README.md.

Run from repo root after the inventory CSV's enacted_status changes:
    python3 scripts/update_state_counts.py
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
STATES_DIR = REPO / "states"

GROUPS = {
    "active": "in_force",
    "extended": "in_force",
    "pending": "pending",
    "replaced": "past",
    "expired": "past",
    "rescinded": "past",
}


def slug_for(state: str) -> str:
    return state.lower().replace(" ", "-")


def compute_counts() -> tuple[dict, dict]:
    per_state: dict[str, dict[str, int]] = defaultdict(lambda: {"in_force": 0, "pending": 0, "past": 0, "total": 0})
    totals = {"in_force": 0, "pending": 0, "past": 0, "total": 0}
    with open(INV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            st = r["state"]
            bucket = GROUPS.get(r["enacted_status"])
            if not bucket:
                continue
            per_state[st][bucket] += 1
            per_state[st]["total"] += 1
            totals[bucket] += 1
            totals["total"] += 1
    return dict(per_state), totals


def patch_state_page(state: str, counts: dict[str, int]) -> bool:
    """Patch the **N instruments — A in force, B pending, C past.** line.

    Returns True if file was modified.
    """
    slug = slug_for(state)
    path = STATES_DIR / f"{slug}.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    new_summary = (
        f"**{counts['total']} instrument{'s' if counts['total'] != 1 else ''}** — "
        f"{counts['in_force']} in force, "
        f"{counts['pending']} pending, "
        f"{counts['past']} past"
    )
    pat = re.compile(r"\*\*\d+ instruments?\*\* — \d+ in force, \d+ pending, \d+ past")
    if pat.search(text):
        text2 = pat.sub(new_summary, text, count=1)
    else:
        return False
    if text2 != text:
        path.write_text(text2, encoding="utf-8")
        return True
    return False


def patch_states_readme(per_state: dict, totals: dict) -> None:
    path = STATES_DIR / "README.md"
    text = path.read_text(encoding="utf-8")

    # Patch the total-count line
    text = re.sub(
        r"_Updated through April 2026\. \d+ moratorium instruments tracked across \d+ states\._",
        f"_Updated through April 2026. {totals['total']} moratorium instruments tracked across {len(per_state)} states._",
        text,
    )

    # Patch the three headline bullets
    text = re.sub(
        r"- 🟢 \*\*\d+ currently in force\*\* \(active \+ extended\)",
        f"- 🟢 **{totals['in_force']} currently in force** (active + extended)",
        text,
    )
    text = re.sub(
        r"- 🟡 \*\*\d+ pending or proposed\*\* \(not yet adopted\)",
        f"- 🟡 **{totals['pending']} pending or proposed** (not yet adopted)",
        text,
    )
    text = re.sub(
        r"- ⚪ \*\*\d+ expired, replaced, or rescinded\*\* \(no longer in force\)",
        f"- ⚪ **{totals['past']} expired, replaced, or rescinded** (no longer in force)",
        text,
    )

    # Patch the per-state table
    def patch_row(match: re.Match[str]) -> str:
        state, total_old, in_force_old, pending_old, past_old = match.groups()
        c = per_state.get(state)
        if not c:
            return match.group(0)  # state not in CSV (probably "no moratoria" state)
        return (
            f"| [{state}]({slug_for(state)}.md) | {c['total']} | "
            f"{c['in_force']} | {c['pending']} | {c['past']} |"
        )

    row_pat = re.compile(r"\| \[([A-Z][A-Za-z ]+)\]\([a-z\-]+\.md\) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|")
    text = row_pat.sub(patch_row, text)

    path.write_text(text, encoding="utf-8")


def main() -> None:
    per_state, totals = compute_counts()

    print(f"Total: {totals}")
    patched_pages = 0
    for state, counts in per_state.items():
        if patch_state_page(state, counts):
            patched_pages += 1
            print(f"  Patched: states/{slug_for(state)}.md  -> "
                  f"{counts['in_force']}/{counts['pending']}/{counts['past']} (total {counts['total']})")

    patch_states_readme(per_state, totals)
    print(f"\nPatched {patched_pages} state pages")
    print(f"Patched: states/README.md")


if __name__ == "__main__":
    main()
