#!/usr/bin/env python3
"""Add the current operative fixed-end-date field to the local inventory.

``duration_days`` deliberately describes the original instrument.  An extension
therefore cannot overwrite it without losing history.  ``current_end_date_iso``
records the independently sourced endpoint that the worklist should monitor.
This migration adds the blank field only; researchers populate it through
``apply_research.py`` with auditable decisions.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PATH = REPO / "data" / "moratorium_inventory.csv"
NEW = "current_end_date_iso"


def main() -> int:
    with PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows, fields = list(reader), list(reader.fieldnames or [])
    if NEW in fields:
        print(f"{NEW} already present; no migration needed.")
        return 0
    fields.insert(fields.index("sectors"), NEW)
    for row in rows:
        row[NEW] = ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    PATH.write_text(buf.getvalue(), encoding="utf-8", newline="")
    print(f"Added {NEW} to {len(rows)} inventory rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
