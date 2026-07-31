#!/usr/bin/env python3
"""Validate the published dataset against the codebook.

Deterministic, stdlib-only checks over data/moratorium_inventory.csv,
data/state_legislation.csv, and data/summary_stats.json. Every check
corresponds to a rule stated in docs/codebook.md, so this script is the
executable form of the codebook.

Run from repo root:
    python3 scripts/validate_dataset.py            # human-readable report
    python3 scripts/validate_dataset.py --json     # machine-readable
    python3 scripts/validate_dataset.py --quiet    # only failures

Exit status is 0 when there are no ERRORs, 1 otherwise. WARNs never fail the
run; they flag things a human should look at (e.g. an in-force moratorium whose
computed expiration has already passed).

This gates every refresh: run it before and after any edit to the inventory.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"
STATS = REPO / "data" / "summary_stats.json"

# ---------------------------------------------------------------------------
# Closed vocabularies (docs/codebook.md)
# ---------------------------------------------------------------------------

JURISDICTION_TYPES = {
    "County", "City", "Town", "Township", "Village",
    "Parish", "Tribal", "Utility-authority", "State", "Other",
    # Non-geographic rollup rows (MD, MI) documented in docs/known-gaps.md;
    # these are the only rows legitimately missing lat/lon.
    "Aggregate meta-row",
}
ACTIVITY_LEVELS = {"None", "Low", "Medium", "High"}
ENACTED_STATUSES = {"active", "extended", "replaced", "expired", "rescinded", "pending"}
DATE_UNCERTAINTY = {"exact", "month_only", "year_only", "range", "unverified"}
DURATION_KINDS = {"fixed_days", "until_date", "until_event", "indefinite", "unknown"}
SECTORS = {"data_center", "battery_storage", "solar", "wind", "cryptocurrency_mining", "general"}
TRIGGER_CATEGORIES = {
    "specific_project", "regulatory_gap", "infrastructure_capacity", "environmental",
    "noise", "water", "grid_energy", "fire_safety", "land_use_compatibility",
    "property_values", "legal_or_litigation", "agricultural_preservation", "other",
}

INVENTORY_COLUMNS = [
    "state", "state_abbrev", "jurisdiction", "jurisdiction_type", "date_enacted",
    "duration", "legal_basis", "trigger", "current_status", "affected_projects",
    "outcome", "has_verify_tags", "verify_count", "cite_count", "activity_level",
    "enacted_status", "moratorium_id", "latitude", "longitude", "date_enacted_iso",
    "date_enacted_uncertainty", "duration_days", "duration_kind", "sectors",
    "trigger_categories",
]
LEGISLATION_COLUMNS = [
    "state", "state_abbrev", "bill", "sponsors", "party", "status",
    "key_provisions", "activity_level",
]
# Typed columns added in v2026.07. Optional so the validator still runs against
# an older release, but checked whenever present.
BILL_STATUS_CATEGORIES = {
    "introduced", "in_committee", "passed_one_chamber", "passed_both_chambers",
    "enacted", "vetoed", "failed_died", "carried_over", "withdrawn", "unknown",
}
CHAMBERS = {"House", "Senate", "Assembly", "Joint", "unknown"}

IN_FORCE = {"active", "extended"}

# Generous continental + AK/HI bounding box. Anything outside is a hard error;
# a coordinate that lands outside its own state is a warning (state centroids
# for multi-state or ambiguous jurisdictions legitimately drift).
LAT_RANGE = (18.0, 72.0)
LON_RANGE = (-180.0, -66.0)

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

VERIFY_RE = re.compile(r"\[VERIFY", re.IGNORECASE)
# <state>-<jurisdiction-slug>-<year>, where <year> is "undated" when no adoption
# date is established, optionally suffixed -pN (explicit phase) or -N (repeat).
MORATORIUM_ID_RE = re.compile(r"^[a-z]{2}-[a-z0-9-]+-(\d{4}|undated)(-p\d+|-\d+)?$")


class Report:
    """Collects findings. Errors fail the run; warnings do not."""

    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.notes: list[str] = []

    def error(self, check: str, msg: str) -> None:
        self.errors.append((check, msg))

    def warn(self, check: str, msg: str) -> None:
        self.warnings.append((check, msg))

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_iso(value: str) -> dt.date | None:
    """Parse YYYY-MM-DD / YYYY-MM / YYYY. Returns None if unparseable."""
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def iso_precision(value: str) -> str | None:
    """Return 'day' | 'month' | 'year' for a well-formed ISO value, else None."""
    value = (value or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return "day"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return "month"
    if re.fullmatch(r"\d{4}", value):
        return "year"
    return None


def load_json_array(raw: str) -> list | None:
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None


INSTRUMENT_RE = re.compile(r"\b(ordinance|resolution|ord|res)\b[\s.#no:]*([0-9][0-9a-z\-/]*)", re.IGNORECASE)


def instrument_key(legal_basis: str) -> str:
    """Normalized ordinance/resolution number, or "" when none is recoverable.

    Mirrors scripts/apply_research.py so the validator and the merge agree on
    when two rows describe distinct instruments.
    """
    m = INSTRUMENT_RE.search(legal_basis or "")
    return f"{m.group(1).lower().rstrip('.')}-{m.group(2).lower()}" if m else ""


def row_verify_count(row: dict) -> int:
    """Count [VERIFY markers across every field, per the codebook definition."""
    return sum(len(VERIFY_RE.findall(v or "")) for v in row.values())


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_inventory(rows: list[dict], fieldnames: list[str], today: dt.date, rep: Report) -> None:
    if fieldnames != INVENTORY_COLUMNS:
        missing = [c for c in INVENTORY_COLUMNS if c not in fieldnames]
        extra = [c for c in fieldnames if c not in INVENTORY_COLUMNS]
        if missing:
            rep.error("schema", f"inventory missing columns: {missing}")
        if extra:
            rep.note(f"inventory has {len(extra)} column(s) beyond the codebook: {extra}")
        if not missing and not extra:
            rep.warn("schema", "inventory column order differs from the codebook")

    seen_ids: dict[str, int] = {}
    seen_jurisdictions: dict[tuple[str, str], list[int]] = defaultdict(list)

    for i, row in enumerate(rows, start=2):  # header is line 1
        where = f"line {i} ({row.get('state_abbrev', '??')} {row.get('jurisdiction', '?')[:40]})"

        # --- closed vocabularies -------------------------------------------
        if row["jurisdiction_type"] not in JURISDICTION_TYPES:
            rep.error("vocab.jurisdiction_type", f"{where}: {row['jurisdiction_type']!r}")
        if row["activity_level"] not in ACTIVITY_LEVELS:
            rep.error("vocab.activity_level", f"{where}: {row['activity_level']!r}")
        if row["enacted_status"] not in ENACTED_STATUSES:
            rep.error("vocab.enacted_status", f"{where}: {row['enacted_status']!r}")
        if row["date_enacted_uncertainty"] not in DATE_UNCERTAINTY:
            rep.error("vocab.date_uncertainty", f"{where}: {row['date_enacted_uncertainty']!r}")
        if row["duration_kind"] not in DURATION_KINDS:
            rep.error("vocab.duration_kind", f"{where}: {row['duration_kind']!r}")

        sectors = load_json_array(row["sectors"])
        if sectors is None:
            rep.error("vocab.sectors", f"{where}: not a JSON array: {row['sectors']!r}")
        else:
            bad = [s for s in sectors if s not in SECTORS]
            if bad:
                rep.error("vocab.sectors", f"{where}: unknown {bad}")
            if not sectors:
                rep.warn("vocab.sectors", f"{where}: empty sectors list")

        triggers = load_json_array(row["trigger_categories"])
        if triggers is None:
            rep.error("vocab.trigger_categories", f"{where}: not a JSON array: {row['trigger_categories']!r}")
        else:
            bad = [t for t in triggers if t not in TRIGGER_CATEGORIES]
            if bad:
                rep.error("vocab.trigger_categories", f"{where}: unknown {bad}")

        # --- state / abbreviation agreement --------------------------------
        expected = STATE_ABBREV.get(row["state"])
        if expected is None:
            rep.error("state.name", f"{where}: unrecognized state {row['state']!r}")
        elif expected != row["state_abbrev"]:
            rep.error("state.abbrev", f"{where}: {row['state']} != {row['state_abbrev']}")

        # --- dates ----------------------------------------------------------
        iso_raw = row["date_enacted_iso"].strip()
        unc = row["date_enacted_uncertainty"]
        if iso_raw:
            prec = iso_precision(iso_raw)
            if prec is None:
                rep.error("date.format", f"{where}: date_enacted_iso {iso_raw!r} is not YYYY[-MM[-DD]]")
            else:
                parsed = parse_iso(iso_raw)
                if parsed is None:
                    rep.error("date.parse", f"{where}: date_enacted_iso {iso_raw!r} not a real date")
                elif parsed > today:
                    rep.warn("date.future", f"{where}: date_enacted_iso {iso_raw} is in the future")
                # precision must agree with the declared uncertainty
                if prec == "month" and unc not in {"month_only", "unverified", "range"}:
                    rep.error("date.precision", f"{where}: month-precision date but uncertainty={unc}")
                if prec == "year" and unc not in {"year_only", "unverified", "range"}:
                    rep.error("date.precision", f"{where}: year-precision date but uncertainty={unc}")
                if prec == "day" and unc in {"month_only", "year_only"}:
                    rep.error("date.precision", f"{where}: day-precision date but uncertainty={unc}")
        else:
            # No ISO date is expected for pending instruments.
            if row["enacted_status"] != "pending":
                rep.warn("date.missing", f"{where}: no date_enacted_iso on a non-pending row")

        # --- duration --------------------------------------------------------
        dd_raw = row["duration_days"].strip()
        kind = row["duration_kind"]
        if dd_raw:
            try:
                dd = int(float(dd_raw))
                if dd <= 0:
                    rep.error("duration.range", f"{where}: duration_days={dd}")
                elif dd > 3650:
                    rep.warn("duration.range", f"{where}: duration_days={dd} (>10 years)")
            except ValueError:
                rep.error("duration.format", f"{where}: duration_days {dd_raw!r} not numeric")
                dd = None
            if kind != "fixed_days":
                rep.error("duration.kind", f"{where}: duration_days set but duration_kind={kind}")
        else:
            dd = None
            if kind == "fixed_days":
                rep.error("duration.kind", f"{where}: duration_kind=fixed_days but duration_days empty")

        # --- expiration drift (warning, drives the worklist) ------------------
        # Only `active` rows are checked. The codebook defines duration_days as
        # the ORIGINAL term, excluding extensions, so an `extended` row is
        # *expected* to compute a past expiry -- warning on those would flag the
        # correctly-maintained rows and bury the genuinely stale ones.
        if row["enacted_status"] == "active" and dd is not None:
            start = parse_iso(iso_raw)
            if start is not None:
                expiry = start + dt.timedelta(days=dd)
                if expiry < today:
                    rep.warn(
                        "status.drift",
                        f"{where}: active but computed expiry {expiry} < {today}",
                    )

        # --- verify accounting ------------------------------------------------
        actual = row_verify_count(row)
        declared_flag = row["has_verify_tags"]
        if declared_flag not in {"True", "False"}:
            rep.error("verify.flag", f"{where}: has_verify_tags={declared_flag!r}")
        else:
            if (declared_flag == "True") != (actual > 0):
                rep.error(
                    "verify.flag",
                    f"{where}: has_verify_tags={declared_flag} but {actual} markers in row text",
                )
        try:
            declared_count = int(row["verify_count"] or 0)
        except ValueError:
            rep.error("verify.count", f"{where}: verify_count={row['verify_count']!r} not an integer")
        else:
            if declared_count != actual:
                rep.error(
                    "verify.count",
                    f"{where}: verify_count={declared_count} but {actual} markers in row text",
                )

        # --- identifier --------------------------------------------------------
        mid = row["moratorium_id"].strip()
        if not mid:
            rep.error("id.missing", f"{where}: empty moratorium_id")
        else:
            if not MORATORIUM_ID_RE.match(mid):
                rep.warn("id.format", f"{where}: moratorium_id {mid!r} off-pattern")
            if not mid.startswith(row["state_abbrev"].lower() + "-"):
                rep.error("id.prefix", f"{where}: moratorium_id {mid!r} does not match state")
            if mid in seen_ids:
                rep.error("id.duplicate", f"{where}: moratorium_id {mid!r} also on line {seen_ids[mid]}")
            else:
                seen_ids[mid] = i

        # --- geocoding ----------------------------------------------------------
        lat_raw, lon_raw = row["latitude"].strip(), row["longitude"].strip()
        if bool(lat_raw) != bool(lon_raw):
            rep.error("geo.pair", f"{where}: latitude/longitude half-populated")
        elif lat_raw:
            try:
                lat, lon = float(lat_raw), float(lon_raw)
            except ValueError:
                rep.error("geo.format", f"{where}: lat/lon not numeric ({lat_raw!r},{lon_raw!r})")
            else:
                if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1]):
                    rep.error("geo.range", f"{where}: latitude {lat} outside {LAT_RANGE}")
                if not (LON_RANGE[0] <= lon <= LON_RANGE[1]):
                    rep.error("geo.range", f"{where}: longitude {lon} outside {LON_RANGE}")

        seen_jurisdictions[(row["state_abbrev"], row["jurisdiction"].strip().lower())].append(
            (i, instrument_key(row["legal_basis"]))
        )

    # Several rows for one jurisdiction are legitimate when they are distinct
    # instruments -- a phased moratorium, or several resolutions adopted the same
    # day covering different sectors (see docs/codebook.md). Only flag rows we
    # cannot tell apart: same jurisdiction, no phase marker, and no distinguishing
    # instrument number.
    for (abbrev, juris), entries in seen_jurisdictions.items():
        if len(entries) < 2 or "phase" in juris:
            continue
        keys = [k for _, k in entries]
        if all(keys) and len(set(keys)) == len(keys):
            continue  # every row carries a distinct instrument number
        lines = [i for i, _ in entries]
        rep.warn(
            "dup.jurisdiction",
            f"{abbrev} {juris!r} appears on lines {lines} with no phase marker and "
            f"no distinguishing instrument number",
        )


def check_legislation(rows: list[dict], fieldnames: list[str], rep: Report) -> None:
    missing = [c for c in LEGISLATION_COLUMNS if c not in fieldnames]
    if missing:
        rep.error("schema.legislation", f"missing columns: {missing}")
        return
    seen: dict[tuple[str, str], int] = {}
    for i, row in enumerate(rows, start=2):
        where = f"line {i} ({row['state_abbrev']} {row['bill']})"
        expected = STATE_ABBREV.get(row["state"])
        if expected is None:
            rep.error("legislation.state", f"{where}: unrecognized state {row['state']!r}")
        elif expected != row["state_abbrev"]:
            rep.error("legislation.abbrev", f"{where}: {row['state']} != {row['state_abbrev']}")
        if row["activity_level"] not in ACTIVITY_LEVELS:
            rep.error("legislation.activity_level", f"{where}: {row['activity_level']!r}")
        if not row["bill"].strip():
            rep.error("legislation.bill", f"{where}: empty bill identifier")
        if "bill_status_category" in fieldnames:
            cat = row["bill_status_category"].strip()
            if cat and cat not in BILL_STATUS_CATEGORIES:
                rep.error("legislation.status_category", f"{where}: {cat!r}")
        if "chamber_of_origin" in fieldnames:
            ch = row["chamber_of_origin"].strip()
            if ch and ch not in CHAMBERS:
                rep.error("legislation.chamber", f"{where}: {ch!r}")
        if "last_action_date_iso" in fieldnames:
            raw = row["last_action_date_iso"].strip()
            if raw and iso_precision(raw) is None:
                rep.error("legislation.action_date", f"{where}: {raw!r} is not YYYY[-MM[-DD]]")

        key = (row["state_abbrev"], row["bill"].strip().lower())
        if key in seen:
            rep.warn("legislation.duplicate", f"{where}: also on line {seen[key]}")
        else:
            seen[key] = i


def check_summary_stats(inv: list[dict], leg: list[dict], stats: dict, rep: Report) -> None:
    """summary_stats.json must be derivable from the CSVs, not hand-maintained."""
    checks = {
        "total_local_moratoria": len(inv),
        "total_state_bills": len(leg),
        "states_with_moratoria": len({r["state"] for r in inv}),
        "moratoria_with_verify_tags": sum(1 for r in inv if row_verify_count(r) > 0),
        "moratoria_without_verify_tags": sum(1 for r in inv if row_verify_count(r) == 0),
    }
    for key, expected in checks.items():
        if key not in stats:
            rep.error("stats.missing", f"summary_stats.json has no {key!r}")
        elif stats[key] != expected:
            rep.error("stats.mismatch", f"{key}: json={stats[key]} but CSV implies {expected}")

    breakdown = stats.get("enacted_status_breakdown")
    if not isinstance(breakdown, dict):
        rep.error("stats.missing", "summary_stats.json has no enacted_status_breakdown object")
    else:
        actual = Counter(r["enacted_status"] for r in inv)
        for status in ENACTED_STATUSES:
            want, got = actual.get(status, 0), breakdown.get(status, 0)
            if want != got:
                rep.error("stats.mismatch", f"enacted_status_breakdown[{status}]: json={got} CSV={want}")


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--quiet", action="store_true", help="suppress the per-check summary")
    ap.add_argument("--today", default=None, help="reference date YYYY-MM-DD (default: system date)")
    args = ap.parse_args()

    today = dt.date.today() if args.today is None else dt.date.fromisoformat(args.today)
    rep = Report()

    inv, inv_cols = read_csv(INV)
    leg, leg_cols = read_csv(LEG)
    stats = json.loads(STATS.read_text(encoding="utf-8"))

    check_inventory(inv, inv_cols, today, rep)
    check_legislation(leg, leg_cols, rep)
    check_summary_stats(inv, leg, stats, rep)

    if args.json:
        print(json.dumps({
            "ok": rep.ok,
            "as_of": today.isoformat(),
            "inventory_rows": len(inv),
            "legislation_rows": len(leg),
            "errors": [{"check": c, "message": m} for c, m in rep.errors],
            "warnings": [{"check": c, "message": m} for c, m in rep.warnings],
            "notes": rep.notes,
        }, indent=2))
        return 0 if rep.ok else 1

    print(f"Dataset validation — {len(inv)} inventory rows, {len(leg)} legislation rows, as of {today}")
    print("-" * 72)
    for note in rep.notes:
        print(f"NOTE  {note}")

    if not args.quiet:
        for label, items in (("ERROR", rep.errors), ("WARN", rep.warnings)):
            if not items:
                continue
            by_check = defaultdict(list)
            for check, msg in items:
                by_check[check].append(msg)
            for check in sorted(by_check):
                msgs = by_check[check]
                print(f"\n{label}  {check}  ({len(msgs)})")
                for msg in msgs[:20]:
                    print(f"    {msg}")
                if len(msgs) > 20:
                    print(f"    ... and {len(msgs) - 20} more")

    print("-" * 72)
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
