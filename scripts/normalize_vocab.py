#!/usr/bin/env python3
"""Normalize closed-vocabulary columns to their codebook spellings.

Idempotent and auditable: every substitution is declared in the tables below,
the script prints exactly what it changed, and re-running it is a no-op. Values
that violate a closed vocabulary but have no declared mapping are reported and
cause a nonzero exit rather than being silently coerced.

CSV files in this repo use CRLF line endings; the round-trip preserves them
byte-for-byte so diffs show only the intended cells.

Run from repo root:
    python3 scripts/normalize_vocab.py --dry-run
    python3 scripts/normalize_vocab.py
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"

# Declared spelling fixes, keyed by (file, column) -> {wrong: right}.
#
# jurisdiction_type: the codebook spells the utility category "Utility-authority"
#   (hyphenated). One row carried the unhyphenated variant.
# activity_level (legislation): 11 New Jersey rows carried a full qualifying
#   sentence in a closed-vocab column. The closed value is "None" and the
#   qualifier already lives in summary_stats.json -> state_details -> New Jersey
#   -> activity_notes, which docs/codebook.md documents as its home.
SUBSTITUTIONS: dict[tuple[str, str], dict[str, str]] = {
    ("inventory", "jurisdiction_type"): {
        "Utility authority": "Utility-authority",
    },
    ("legislation", "activity_level"): {
        "None for formal moratoria; High for non-moratorium restrictions.": "None",
    },
}

# Vocabularies enforced after substitution, so an undeclared violation is loud.
VOCABS: dict[tuple[str, str], set[str]] = {
    ("inventory", "jurisdiction_type"): {
        "County", "City", "Town", "Township", "Village", "Parish", "Tribal",
        "Utility-authority", "State", "Other", "Aggregate meta-row",
    },
    ("inventory", "activity_level"): {"None", "Low", "Medium", "High"},
    ("inventory", "enacted_status"): {
        "active", "extended", "replaced", "expired", "rescinded", "pending",
    },
    ("legislation", "activity_level"): {"None", "Low", "Medium", "High"},
}

FILES = {"inventory": INV, "legislation": LEG}

# LaTeX escaping that leaked into the published CSVs when rows were round-tripped
# through the paper's table pipeline. These corrupt real content -- "App\_Pages"
# breaks a source URL, "\$11 million" misreads as a literal backslash. Applied to
# every column; the CSVs are data, so a backslash is never meaningful here.
LATEX_ESCAPES = {
    r"\$": "$",
    r"\_": "_",
    r"\&": "&",
    r"\%": "%",
    r"\#": "#",
}


def read_rows(path: Path) -> tuple[list[dict], list[str]]:
    # newline="" keeps the CRLF terminators intact; passing it to open() rather
    # than Path.read_text() keeps this working on Python 3.12.
    with open(path, encoding="utf-8", newline="") as f:
        src = f.read()
    reader = csv.DictReader(io.StringIO(src))
    return list(reader), list(reader.fieldnames or [])


def write_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    args = ap.parse_args()

    total_changes = 0
    unmapped: list[str] = []

    for key, path in FILES.items():
        rows, fieldnames = read_rows(path)
        changes: list[str] = []

        for (fkey, column), mapping in SUBSTITUTIONS.items():
            if fkey != key or column not in fieldnames:
                continue
            for i, row in enumerate(rows, start=2):
                current = row[column]
                if current in mapping:
                    row[column] = mapping[current]
                    changes.append(
                        f"  line {i} {row.get('state_abbrev', '??')} "
                        f"{column}: {current!r} -> {mapping[current]!r}"
                    )

        for i, row in enumerate(rows, start=2):
            for column in fieldnames:
                current = row[column]
                if "\\" not in (current or ""):
                    continue
                fixed = current
                for esc, plain in LATEX_ESCAPES.items():
                    fixed = fixed.replace(esc, plain)
                if fixed != current:
                    row[column] = fixed
                    changes.append(
                        f"  line {i} {row.get('state_abbrev', '??')} "
                        f"{column}: unescaped LaTeX ({current.count(chr(92)) - fixed.count(chr(92))} sequence(s))"
                    )

        for (fkey, column), allowed in VOCABS.items():
            if fkey != key or column not in fieldnames:
                continue
            for i, row in enumerate(rows, start=2):
                if row[column] not in allowed:
                    unmapped.append(
                        f"{path.name} line {i} {column}={row[column]!r} "
                        f"(not in vocabulary, no declared mapping)"
                    )

        if changes:
            print(f"{path.relative_to(REPO)} — {len(changes)} cell(s):")
            for line in changes:
                print(line)
            total_changes += len(changes)
            if not args.dry_run:
                write_rows(path, rows, fieldnames)
        else:
            print(f"{path.relative_to(REPO)} — no changes needed")

    if unmapped:
        print(f"\n{len(unmapped)} undeclared vocabulary violation(s):")
        for line in unmapped:
            print(f"  {line}")
        return 1

    if args.dry_run and total_changes:
        print(f"\nDry run: {total_changes} cell(s) would change. Re-run without --dry-run to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
