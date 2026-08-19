#!/usr/bin/env python3
"""Add typed state-policy fields to the historical bill tracker.

This is a one-time, conservative migration for v2026.08.  It never guesses
that an enacted temporary measure remains in force: enacted rows begin as
``unknown`` until a current primary source establishes their operative status.
Newly researched executive, agency, regulatory, and statutory actions are
then added through ``apply_legislation.py`` like any other state instrument.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PATH = REPO / "data" / "state_legislation.csv"
NEW_COLUMNS = [
    "policy_action_id",
    "policy_instrument_type", "policy_mechanism", "legal_effect_status",
    "scope_of_action", "effective_date_iso", "end_condition",
    "primary_source_url",
]


def action_id(state_abbrev: str, display_id: str, taken: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", display_id.lower()).strip("-") or "policy-action"
    base = f"{state_abbrev.lower()}-{slug}"
    candidate, suffix = base, 2
    while candidate in taken:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def classify(text: str) -> tuple[str, str]:
    text = text.lower()
    if "moratorium" in text:
        if "municipalit" in text or "local moratorium" in text or "local government" in text:
            return "local_moratorium_authorization", "local_government"
        return "statewide_moratorium", "statewide"
    if "preempt" in text:
        return "local_moratorium_preemption", "local_government"
    if any(term in text for term in ("interconnection", "large load", "ratepayer", "utility", "ercot", "grid")):
        return "utility_large_load_restriction", "utility_grid"
    if any(term in text for term in ("tax exemption", "sales/use tax", "incentive", "ad valorem")):
        return "incentive_restriction", "fiscal"
    if any(term in text for term in ("reporting", "disclosure", "nondisclosure", "nda")):
        return "reporting_disclosure", "statewide"
    if any(term in text for term in ("permit", "siting", "zoning", "land use")):
        return "permitting_restriction", "statewide"
    return "other", "unknown"


def legal_status(category: str) -> str:
    return {
        "failed_died": "failed", "vetoed": "failed", "withdrawn": "withdrawn",
        "enacted": "unknown",
    }.get(category, "proposed")


def main() -> int:
    with PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        names = list(reader.fieldnames or [])
    added = [c for c in NEW_COLUMNS if c not in names]
    names.extend(added)
    changed = 0
    taken = {r.get("policy_action_id", "") for r in rows if r.get("policy_action_id", "")}
    for row in rows:
        for col in NEW_COLUMNS:
            row.setdefault(col, "")
        mechanism, scope = classify(f"{row.get('bill', '')} {row.get('key_provisions', '')}")
        values = {
            "policy_action_id": row.get("policy_action_id") or action_id(row["state_abbrev"], row["bill"], taken),
            "policy_instrument_type": "bill",
            "policy_mechanism": mechanism,
            "legal_effect_status": legal_status(row.get("bill_status_category", "")),
            "scope_of_action": scope,
        }
        for col, value in values.items():
            if not row[col]:
                row[col] = value
                changed += 1
        taken.add(row["policy_action_id"])
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=names, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    PATH.write_text(buf.getvalue(), encoding="utf-8", newline="")
    print(f"Migrated {len(rows)} state-policy rows; added {len(added)} columns; populated {changed} fields.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
