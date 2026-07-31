#!/usr/bin/env python3
"""Reconcile the inventory's typed columns against the codebook's rules.

Two invariants, both of which researchers routinely half-satisfy:

  1. duration_days is populated if and only if duration_kind is fixed_days.
  2. date_enacted_uncertainty agrees with the precision of date_enacted_iso --
     a day-precision date cannot be flagged month_only or year_only.

For (2) the fix keeps the day and downgrades the flag to `unverified`, because a
researcher writing "adopted ~2026-02-26" has real information about the day and
is expressing doubt, not month-level granularity. Discarding the day to match the
flag would throw away the more specific fact.

Researchers reliably record the *duration text* correctly but are inconsistent
about the two typed columns derived from it. The codebook is explicit:

  fixed_days   a fixed time period  -> duration_days REQUIRED
  until_date   ends on a specific calendar date with no fixed length
  until_event  ends when permanent regulations are adopted
  indefinite   no scheduled end
  unknown      undetermined
                                    -> duration_days EMPTY for all four

So exactly one combination is valid: duration_days is populated if and only if
duration_kind is fixed_days. This script enforces that, deriving the missing
value from the free-text `duration` column where it can and reporting anything
it cannot resolve rather than guessing.

Conversion convention (docs/codebook.md): "6 months" -> 180, "1 year" /
"12 months" -> 365. Months are 30 days except that a whole year is 365.

Run from repo root:
    python3 scripts/reconcile_durations.py --dry-run
    python3 scripts/reconcile_durations.py
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"

# Ordered so the most specific pattern wins.
DURATION_PATTERNS: list[tuple[re.Pattern, callable]] = [
    (re.compile(r"\b(\d+)\s*(?:calendar\s*)?days?\b", re.I), lambda m: int(m.group(1))),
    (re.compile(r"\bone\s+year\b|\b1\s*year\b|\b12\s*months?\b", re.I), lambda m: 365),
    (re.compile(r"\btwo\s+years?\b|\b2\s*years?\b|\b24\s*months?\b", re.I), lambda m: 730),
    (re.compile(r"\beighteen\s*\(?18\)?\s*months?\b|\b18\s*months?\b", re.I), lambda m: 548),
    (re.compile(r"\bsix\s*\(?6\)?\s*months?\b|\b6\s*months?\b", re.I), lambda m: 180),
    (re.compile(r"\bnine\s*\(?9\)?\s*months?\b|\b9\s*months?\b", re.I), lambda m: 270),
    (re.compile(r"\bthree\s*\(?3\)?\s*months?\b|\b3\s*months?\b", re.I), lambda m: 90),
    (re.compile(r"\b(\d+)\s*months?\b", re.I), lambda m: int(m.group(1)) * 30),
    (re.compile(r"\b(\d+)\s*years?\b", re.I), lambda m: int(m.group(1)) * 365),
]

# A duration text stating an explicit fixed term, even when it also mentions an
# early-exit condition ("up to one year, or earlier if regulations are adopted").
# The stated maximum term is the instrument's duration.
FIXED_TERM_HINT = re.compile(
    r"\b(\d+\s*(days?|months?|years?)|one\s+year|two\s+years|six\s+months|"
    r"eighteen\s*\(?18\)?\s*months?|twelve\s+months)\b", re.I,
)

# Text that clearly indicates the pause ends on a named calendar date.
UNTIL_DATE_HINT = re.compile(r"\b(through|until|expires?\s+on|ending)\s+\d{4}-\d{2}-\d{2}", re.I)


def parse_days(text: str) -> int | None:
    for pattern, convert in DURATION_PATTERNS:
        m = pattern.search(text or "")
        if m:
            try:
                return convert(m)
            except (ValueError, IndexError):
                continue
    return None


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
    changes: list[str] = []
    unresolved: list[str] = []

    for i, row in enumerate(rows, start=2):
        kind = row["duration_kind"]
        days = row["duration_days"].strip()
        text = row["duration"]
        label = f"line {i} {row['state_abbrev']} {row['jurisdiction'][:32]}"

        if kind == "fixed_days" and not days:
            derived = parse_days(text)
            if derived is not None:
                row["duration_days"] = str(derived)
                changes.append(f"  {label}: fixed_days had no duration_days -> {derived} (from {text[:40]!r})")
            else:
                # A fixed_days claim we cannot substantiate is really unknown.
                row["duration_kind"] = "unknown"
                changes.append(f"  {label}: fixed_days but no parseable term -> duration_kind=unknown")

        elif kind != "fixed_days" and days:
            if UNTIL_DATE_HINT.search(text) or kind in {"until_date", "indefinite"}:
                # An end date is not a term length; the codebook says drop it.
                row["duration_days"] = ""
                changes.append(f"  {label}: {kind} carried duration_days={days} -> cleared (ends on a date)")
            elif FIXED_TERM_HINT.search(text):
                # An explicit maximum term with an early-exit condition is still
                # a fixed term for our purposes.
                row["duration_kind"] = "fixed_days"
                changes.append(f"  {label}: {kind} with explicit term {text[:40]!r} -> duration_kind=fixed_days")
            else:
                row["duration_days"] = ""
                changes.append(f"  {label}: {kind} carried duration_days={days} -> cleared (no stated term)")

    # --- date precision vs declared uncertainty ------------------------------
    iso_day = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    iso_month = re.compile(r"^\d{4}-\d{2}$")
    iso_year = re.compile(r"^\d{4}$")
    for i, row in enumerate(rows, start=2):
        iso = row["date_enacted_iso"].strip()
        unc = row["date_enacted_uncertainty"]
        label = f"line {i} {row['state_abbrev']} {row['jurisdiction'][:32]}"
        if not iso:
            continue
        if iso_day.match(iso) and unc in {"month_only", "year_only"}:
            row["date_enacted_uncertainty"] = "unverified"
            changes.append(f"  {label}: day-precision date flagged {unc} -> unverified")
        elif iso_month.match(iso) and unc not in {"month_only", "unverified", "range"}:
            row["date_enacted_uncertainty"] = "month_only"
            changes.append(f"  {label}: month-precision date flagged {unc} -> month_only")
        elif iso_year.match(iso) and unc not in {"year_only", "unverified", "range"}:
            row["date_enacted_uncertainty"] = "year_only"
            changes.append(f"  {label}: year-precision date flagged {unc} -> year_only")

    for i, row in enumerate(rows, start=2):
        if (row["duration_kind"] == "fixed_days") != bool(row["duration_days"].strip()):
            unresolved.append(f"line {i} {row['state_abbrev']} {row['jurisdiction'][:32]}: "
                              f"kind={row['duration_kind']} days={row['duration_days']!r}")

    if changes:
        print(f"{len(changes)} row(s) reconciled:")
        for line in changes:
            print(line)
    else:
        print("No duration inconsistencies found.")

    if unresolved:
        print(f"\n{len(unresolved)} row(s) STILL inconsistent:")
        for line in unresolved:
            print(f"  {line}")
        return 1

    if changes and not args.dry_run:
        write_rows(rows, fieldnames)
        print(f"\nWrote {INV.relative_to(REPO)}")
    elif args.dry_run:
        print("\nDry run - nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
