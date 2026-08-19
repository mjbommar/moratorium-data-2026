#!/usr/bin/env python3
"""Check that headline numbers quoted in prose still match the data.

The recurring failure in this repository is not wrong data — it is *stale
narrative*. README.md, docs/codebook.md, and docs/known-gaps.md all quote counts
that were true when written, and nothing detects it when the CSVs move past
them. This script does.

Each claim is matched by a pattern anchored on the words around it, capturing
exactly one number. `--fix` rewrites only the digits inside that capture span, so
the surrounding sentence is never touched; anything the patterns cannot locate is
reported for a human rather than guessed at. Adding a new headline number to the
prose means adding a claim here too, or it will silently go unchecked.

Run from repo root:
    python3 scripts/check_docs_numbers.py         # report drift, exit 1 if any
    python3 scripts/check_docs_numbers.py --fix   # update the numbers in place
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"
SWEEP = REPO / "data" / "sweep_coverage.json"

VERIFY_RE = re.compile(r"\[VERIFY", re.IGNORECASE)


def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def facts() -> dict[str, int]:
    inv, leg = load(INV), load(LEG)
    c = Counter(r["enacted_status"] for r in inv)
    # Sweep coverage drifted once already: the prose said 15 while the data said
    # 18. Check it like any other published number.
    swept = swept_empty = 0
    if SWEEP.exists():
        windows = json.loads(SWEEP.read_text(encoding="utf-8")).get("windows", [])
        if windows:
            swept = len(windows[-1].get("swept_states", []))
            swept_empty = len(windows[-1].get("swept_states_with_no_adoptions_in_window", []))
    return {
        "rows": len(inv),
        "in_force": c["active"] + c["extended"],
        "active": c["active"],
        "extended": c["extended"],
        "replaced": c["replaced"],
        "expired": c["expired"],
        "rescinded": c["rescinded"],
        "pending": c["pending"],
        "past": c["replaced"] + c["expired"] + c["rescinded"],
        "states": len({r["state"] for r in inv}),
        "states_without": 50 - len({r["state"] for r in inv}),
        "verify_rows": sum(1 for r in inv if any(VERIFY_RE.search(v or "") for v in r.values())),
        "geocoded": sum(1 for r in inv if r["latitude"].strip()),
        "bills": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill"),
        "state_policy_actions": len(leg),
        "bills_typed": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill" and r.get("bill_status_category")),
        "bills_enacted": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill" and r.get("bill_status_category") == "enacted"),
        "swept": swept,
        "unswept": 50 - swept,
        "swept_empty": swept_empty,
    }


# Each claim: (file, regex with one capturing group, fact key, human description).
# Patterns are anchored on distinctive surrounding words so they cannot drift
# onto an unrelated number.
CLAIMS: list[tuple[str, str, str, str]] = [
    ("README.md", r"As of [A-Za-z]+(?: \d{1,2},)? 2026, ([\d,]+) local moratorium instruments (?:are )?tracked", "rows", "README headline row count"),
    ("README.md", r"tracked across (\d+) states\.\*\*", "states", "README headline state count"),
    ("README.md", r"\*\*([\d,]+) currently in force\*\* \(active or extended\)", "in_force", "README headline in-force"),
    ("README.md", r"\*\*(\d+) pending or proposed\*\* \(not yet adopted\)", "pending", "README headline pending"),
    ("README.md", r"\*\*(\d+) expired, replaced, or rescinded\*\*", "past", "README headline past"),
    ("README.md", r"- \*\*([\d,]+) moratorium instruments\*\* tracked in our cleaned inventory", "rows", "README detail row count"),
    ("README.md", r"- \*\*(\d+) states\*\* have at least one moratorium", "states", "README detail state count"),
    ("README.md", r"- \*\*([\d,]+) state-level bills\*\* tracked", "bills", "README bill count"),
    ("README.md", r"\*\*(\d+) of [\d,]+ instruments geocoded\*\*", "geocoded", "README geocoded count"),
    ("README.md", r"\*\*[\d,]+ of ([\d,]+) instruments geocoded\*\*", "rows", "README geocoded denominator"),
    ("docs/methodology.md", r"cleaned inventory has \*\*([\d,]+) instruments across \d+ states\*\*", "rows", "methodology inventory rows"),
    ("docs/methodology.md", r"cleaned inventory has \*\*[\d,]+ instruments across (\d+) states\*\*", "states", "methodology inventory states"),
    ("docs/methodology.md", r"Of ([\d,]+) rows, [\d,]+ \([\d.]+%\) are successfully geocoded", "rows", "methodology geocode denominator"),
    ("docs/methodology.md", r"Of [\d,]+ rows, ([\d,]+) \([\d.]+%\) are successfully geocoded", "geocoded", "methodology geocode numerator"),
    ("docs/methodology.md", r"\*\*Inventory \(n=([\d,]+)\):\*\*", "rows", "methodology cohort comparison rows"),
    ("docs/codebook.md", r"\*\*One row per moratorium instrument\.\*\* ([\d,]+) rows total", "rows", "codebook inventory rows"),
    ("docs/codebook.md", r"`total_local_moratoria`: ([\d,]+)", "rows", "codebook total_local_moratoria"),
    ("docs/codebook.md", r"`total_state_bills`: ([\d,]+)", "bills", "codebook total_state_bills"),
    ("docs/codebook.md", r"`total_state_policy_actions`: ([\d,]+)", "state_policy_actions", "codebook total_state_policy_actions"),
    ("docs/codebook.md", r"`states_with_moratoria`: (\d+)", "states", "codebook states_with_moratoria"),
    ("docs/codebook.md", r"`states_without_moratoria`: (\d+)", "states_without", "codebook states_without_moratoria"),
    ("docs/codebook.md", r"`moratoria_with_verify_tags`: (\d+)", "verify_rows", "codebook verify row count"),
    ("docs/known-gaps.md", r"\*\*(\d+) of (?:the )?[\d,]+ inventory rows\*\* have at least one such evidence-ceiling note", "verify_rows", "known-gaps verify rows"),
    ("docs/known-gaps.md", r"\*\*[\d,]+ of (?:the )?([\d,]+) inventory rows\*\* have at least one such evidence-ceiling note", "rows", "known-gaps verify denominator"),
    ("docs/known-gaps.md", r"(\d+) of [\d,]+ instruments are geocoded", "geocoded", "known-gaps geocoded"),
    ("docs/known-gaps.md", r"[\d,]+ of ([\d,]+) instruments are geocoded", "rows", "known-gaps geocoded denominator"),
    ("CHANGELOG.md", r"\| Local moratorium instruments \| \*\*([\d,]+)\*\* \|", "rows", "CHANGELOG current rows"),
    ("CHANGELOG.md", r"\| Currently in force \(active \+ extended\) \| \*\*([\d,]+)\*\* \|", "in_force", "CHANGELOG current in-force"),
    ("CHANGELOG.md", r"\| Pending / proposed \| \*\*(\d+)\*\* \|", "pending", "CHANGELOG current pending"),
    ("CHANGELOG.md", r"\| Past \(replaced \+ expired \+ rescinded\) \| \*\*(\d+)\*\* \|", "past", "CHANGELOG current past"),
    ("CHANGELOG.md", r"\| Rows carrying `\[VERIFY\]` markers \| \*\*(\d+)\*\* \|", "verify_rows", "CHANGELOG current verify rows"),
    ("CHANGELOG.md", r"\| State bills tracked \| \*\*([\d,]+)\*\* \|", "bills", "CHANGELOG current bills"),
    ("CHANGELOG.md", r"\| State policy actions, including non-bill instruments \| \*\*([\d,]+)\*\* \|", "state_policy_actions", "CHANGELOG current policy actions"),
    ("CHANGELOG.md", r"\| States with at least one local instrument \| \*\*(\d+)\*\* \|", "states", "CHANGELOG current states"),
    ("CHANGELOG.md", r"([\d,]+) of [\d,]+ bills now\s*\ncarry a researched final disposition", "bills_typed", "CHANGELOG typed bills"),
    ("CHANGELOG.md", r"carry a researched final disposition, including \*\*(\d+) enacted\*\*", "bills_enacted", "CHANGELOG enacted bills"),
    ("CHANGELOG.md", r"\*\*All (\d+) states were swept\*\*", "swept", "CHANGELOG swept states"),
    ("CHANGELOG.md", r"\*\*(\d+) states recorded no local adoption in the window\*\*", "swept_empty", "CHANGELOG empty-sweep states"),
    ("docs/known-gaps.md", r"\*\*All (\d+) states were swept\*\*", "swept", "known-gaps swept states"),
    ("docs/known-gaps.md", r"\*\*(\d+) states recorded no local adoption during the window\*\*", "swept_empty", "known-gaps empty-sweep states"),
]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite ONLY the captured number in each matched claim, leaving the "
                         "surrounding sentence untouched")
    args = ap.parse_args()
    data = facts()
    problems: list[str] = []
    fixed: list[str] = []
    checked = 0
    missing = 0

    for filename, pattern, key, label in CLAIMS:
        path = REPO / filename
        if not path.exists():
            problems.append(f"{filename}: file not found")
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(pattern, text)
        if not m:
            missing += 1
            problems.append(f"{filename}: could not locate claim -- {label} (pattern may need updating)")
            continue
        checked += 1
        claimed = int(m.group(1).replace(",", ""))
        actual = data[key]
        if claimed == actual:
            continue
        if args.fix:
            # Replace only the digits inside the capture span, so the sentence
            # around them is never touched.
            start, end = m.span(1)
            path.write_text(text[:start] + str(actual) + text[end:], encoding="utf-8")
            fixed.append(f"{filename}: {label} {claimed} -> {actual}")
        else:
            problems.append(f"{filename}: {label} says {claimed}, data says {actual}")

    print("Data as shipped:")
    for k in ("rows", "in_force", "pending", "past", "states", "verify_rows", "geocoded", "bills", "bills_typed", "bills_enacted"):
        print(f"  {k:14s} {data[k]}")
    print()

    if fixed:
        print(f"Updated {len(fixed)} number(s):")
        for f in fixed:
            print(f"  {f}")
        print()

    if not problems:
        print(f"All {checked} documented numbers match the data.")
        return 0

    print(f"{len(problems)} problem(s) across {checked + missing} claims:")
    for p in problems:
        print(f"  {p}")
    print("\nUpdate the prose by hand -- these are sentences, not fields.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
