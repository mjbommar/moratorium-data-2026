#!/usr/bin/env python3
"""Apply state-policy research decisions to data/state_legislation.csv.

Same discipline as apply_research.py: explicit answer files, schema validation,
a conflict guard, and an audit log. Prose never edits the CSV.

The tracker is deliberately broader than bills: a binding executive order,
agency order, regulation, or enacted statute can constrain a project just as
materially as an enacted bill.  The free-text `status` column stays as
provenance; the typed columns make the tracker filterable:

    bill_status_category   introduced | in_committee | passed_one_chamber |
                           passed_both_chambers | enacted | vetoed |
                           failed_died | carried_over | withdrawn | unknown
    last_action_date_iso   YYYY-MM-DD of the most recent recorded action
    chamber_of_origin      House | Senate | Assembly | Joint | unknown

Run from repo root:
    python3 scripts/apply_legislation.py --answers-dir work/answers/legislation --dry-run
    python3 scripts/apply_legislation.py --answers-dir work/answers/legislation
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

REPO = Path(__file__).resolve().parents[1]
LEG = REPO / "data" / "state_legislation.csv"
SCHEMA = REPO / "work" / "schemas" / "legislation_decision.schema.json"
AUDIT_DIR = REPO / "work" / "audit"

NEW_COLUMNS = [
    "bill_status_category", "last_action_date_iso", "chamber_of_origin",
    "policy_action_id",
    "policy_instrument_type", "policy_mechanism", "legal_effect_status",
    "scope_of_action", "effective_date_iso", "end_condition",
    "primary_source_url",
]
BASE_COLUMNS = [
    "state", "state_abbrev", "bill", "sponsors", "party", "status",
    "key_provisions", "activity_level",
]

STATUS_CATEGORIES = {
    "introduced", "in_committee", "passed_one_chamber", "passed_both_chambers",
    "enacted", "vetoed", "failed_died", "carried_over", "withdrawn", "unknown",
}
CHAMBERS = {"House", "Senate", "Assembly", "Joint", "unknown"}
POLICY_INSTRUMENT_TYPES = {"bill", "executive_order", "governor_directive", "agency_order", "regulation", "statute"}
POLICY_MECHANISMS = {
    "statewide_moratorium", "local_moratorium_authorization",
    "local_moratorium_preemption", "permitting_restriction",
    "utility_large_load_restriction", "incentive_restriction",
    "reporting_disclosure", "other",
}
LEGAL_EFFECT_STATUSES = {"proposed", "in_force", "expired", "superseded", "failed", "withdrawn", "unknown"}
ACTION_SCOPES = {"statewide", "state_agency", "local_government", "utility_grid", "fiscal", "mixed", "unknown"}

STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}


ABBREV_TO_STATE = {v: k for k, v in STATE_ABBREV.items()}


def action_id(state_abbrev: str, display_id: str, taken: set[str]) -> str:
    """Create a deterministic, unique stable key for a policy instrument."""
    slug = re.sub(r"[^a-z0-9]+", "-", display_id.lower()).strip("-") or "policy-action"
    base = f"{state_abbrev.lower()}-{slug}"
    candidate, suffix = base, 2
    while candidate in taken:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def resolve_state(value: str) -> tuple[str, str]:
    """Return (full name, abbreviation) accepting either form.

    Researchers supply "Pennsylvania" or "PA" interchangeably; storing the
    abbreviation in the `state` column silently corrupts every downstream join.
    """
    value = (value or "").strip()
    if value in STATE_ABBREV:
        return value, STATE_ABBREV[value]
    upper = value.upper()
    if upper in ABBREV_TO_STATE:
        return ABBREV_TO_STATE[upper], upper
    return value, ""


def rel_to_repo(path: Path) -> str:
    """Repo-relative path string, tolerant of relative CLI arguments."""
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def read_csv() -> tuple[list[dict], list[str]]:
    with open(LEG, encoding="utf-8", newline="") as f:
        src = f.read()
    reader = csv.DictReader(io.StringIO(src))
    return list(reader), list(reader.fieldnames or [])


def write_csv(rows: list[dict], fieldnames: list[str]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    with open(LEG, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--answers", nargs="+")
    src.add_argument("--answers-dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-confidence", type=float, default=0.4)
    ap.add_argument("--no-new-bills", action="store_true")
    args = ap.parse_args()

    paths = [Path(p) for p in args.answers] if args.answers else sorted(Path(args.answers_dir).glob("*.json"))
    if not paths:
        print("ERROR: no answer files found")
        return 2

    schema = None
    if jsonschema is not None and SCHEMA.exists():
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    rows, fieldnames = read_csv()
    for col in NEW_COLUMNS:
        if col not in fieldnames:
            fieldnames.append(col)
            for row in rows:
                row.setdefault(col, "")
    for row in rows:
        for col in NEW_COLUMNS:
            row.setdefault(col, "")

    action_ids = {r.get("policy_action_id", "") for r in rows if r.get("policy_action_id", "")}

    by_key = {f"{r['state_abbrev'].upper()}:{r['bill']}": r for r in rows}

    audit: list[dict] = []
    conflicts: list[str] = []
    stats: Counter = Counter()
    new_rows: list[dict] = []
    session_notes: dict[str, str] = {}

    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            conflicts.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if schema is not None:
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as exc:
                loc = "/".join(str(p) for p in exc.absolute_path)
                conflicts.append(f"{path.name}: schema violation at {loc or '<root>'}: {exc.message}")
                continue

        if data.get("session_note"):
            session_notes[data["state_abbrev"]] = data["session_note"]

        for dec in data.get("decisions", []):
            key = dec["bill_key"]
            stats[f"outcome:{dec['outcome']}"] += 1
            row = by_key.get(key)
            if row is None:
                conflicts.append(f"{path.name}: unknown bill_key {key!r}")
                stats["skipped_unknown_key"] += 1
                continue
            if dec["outcome"] == "unresolvable":
                stats["unresolvable"] += 1
                continue
            conf = dec.get("confidence")
            if conf is not None and conf < args.min_confidence:
                stats["skipped_low_confidence"] += 1
                continue

            for column, value in (dec.get("fields") or {}).items():
                if column not in fieldnames:
                    conflicts.append(f"{path.name}: {key} unknown column {column!r}")
                    continue
                if column == "bill_status_category" and value not in STATUS_CATEGORIES:
                    conflicts.append(f"{path.name}: {key} bad status category {value!r}")
                    continue
                if column == "chamber_of_origin" and value not in CHAMBERS:
                    conflicts.append(f"{path.name}: {key} bad chamber {value!r}")
                    continue
                if column == "policy_instrument_type" and value not in POLICY_INSTRUMENT_TYPES:
                    conflicts.append(f"{path.name}: {key} bad policy instrument type {value!r}")
                    continue
                if column == "policy_mechanism" and value not in POLICY_MECHANISMS:
                    conflicts.append(f"{path.name}: {key} bad policy mechanism {value!r}")
                    continue
                if column == "legal_effect_status" and value not in LEGAL_EFFECT_STATUSES:
                    conflicts.append(f"{path.name}: {key} bad legal effect status {value!r}")
                    continue
                if column == "scope_of_action" and value not in ACTION_SCOPES:
                    conflicts.append(f"{path.name}: {key} bad action scope {value!r}")
                    continue
                if row[column] == value:
                    continue
                audit.append({
                    "bill_key": key, "column": column,
                    "before": row[column], "after": value,
                    "reason": dec.get("notes", ""), "source": path.name,
                })
                row[column] = value
                stats[f"set:{column}"] += 1

        if args.no_new_bills:
            continue
        for nb in data.get("new_bills", []):
            conf = nb.get("confidence")
            if conf is not None and conf < args.min_confidence:
                stats["new_bill_low_confidence"] += 1
                continue
            state_name, abbrev = resolve_state(nb["state"])
            if not abbrev:
                conflicts.append(f"{path.name}: new bill {nb['bill']!r} has unrecognized state {nb['state']!r}")
                continue
            key = f"{abbrev}:{nb['bill']}"
            if key in by_key:
                stats["new_bill_duplicate"] += 1
                continue
            activity = next((r["activity_level"] for r in rows if r["state_abbrev"] == abbrev), "Low")
            row = {c: "" for c in fieldnames}
            row.update({
                "state": state_name,
                "state_abbrev": abbrev,
                "bill": nb["bill"],
                "sponsors": nb.get("sponsors", ""),
                "party": nb.get("party", ""),
                "status": nb.get("status", ""),
                "key_provisions": nb["key_provisions"],
                "activity_level": activity,
                "bill_status_category": nb.get("bill_status_category", "unknown"),
                "last_action_date_iso": nb.get("last_action_date_iso", ""),
                "chamber_of_origin": nb.get("chamber_of_origin", "unknown"),
                "policy_action_id": nb.get("policy_action_id") or action_id(abbrev, nb["bill"], action_ids),
                "policy_instrument_type": nb.get("policy_instrument_type", "bill"),
                "policy_mechanism": nb.get("policy_mechanism", "other"),
                "legal_effect_status": nb.get("legal_effect_status", "unknown"),
                "scope_of_action": nb.get("scope_of_action", "unknown"),
                "effective_date_iso": nb.get("effective_date_iso", ""),
                "end_condition": nb.get("end_condition", ""),
                "primary_source_url": nb.get("primary_source_url", ""),
            })
            action_ids.add(row["policy_action_id"])
            new_rows.append(row)
            by_key[key] = row
            audit.append({
                "bill_key": key, "column": "<new row>", "before": "",
                "after": nb["key_provisions"][:120], "reason": nb.get("notes", ""),
                "source": path.name,
            })
            stats["new_bills_added"] += 1

    rows.extend(new_rows)
    rows.sort(key=lambda r: (r["state"], r["bill"]))

    print("Summary")
    for key in sorted(stats):
        print(f"  {key:32s} {stats[key]}")
    coded = sum(1 for r in rows if r.get("bill_status_category"))
    print(f"  {'rows_with_typed_status':32s} {coded} / {len(rows)}")
    if session_notes:
        print(f"\nSession notes captured for {len(session_notes)} state(s)")

    if conflicts:
        print(f"\n{len(conflicts)} conflict(s) — NOT applied:")
        for c in conflicts[:25]:
            print(f"  {c}")
        if len(conflicts) > 25:
            print(f"  ... and {len(conflicts) - 25} more")

    if args.dry_run:
        print("\nDry run — nothing written.")
        return 0
    if not audit:
        print("\nNo changes to apply.")
        return 0

    write_csv(rows, fieldnames)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    audit_path = AUDIT_DIR / f"apply-legislation-{stamp}.json"
    audit_path.write_text(json.dumps({
        "applied_at": stamp,
        "answer_files": [rel_to_repo(p) for p in paths],
        "stats": dict(stats),
        "session_notes": session_notes,
        "conflicts": conflicts,
        "changes": audit,
    }, indent=2) + "\n", encoding="utf-8")

    print(f"\nWrote {LEG.relative_to(REPO)} ({len(rows)} rows, {len(fieldnames)} columns)")
    print(f"Wrote {audit_path.relative_to(REPO)} ({len(audit)} change records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
