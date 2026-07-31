#!/usr/bin/env python3
"""Build a prioritized, state-partitioned research worklist from the inventory.

Purely deterministic: reads data/moratorium_inventory.csv and emits the set of
rows that need human or agent research as of a reference date. No network, no
LLM. The output is the contract handed to the research fan-out, and the same
file is later used to check that every item was actually resolved.

Buckets, in priority order:

  expired_in_force  in-force row whose date_enacted_iso + duration_days has
                    already passed -- status is provably stale
  until_date_stale  in-force row that ends on a calendar date we cannot compute
                    from typed columns (duration_kind=until_date)
  stale_pending     enacted_status=pending older than --pending-age days
  open_ended        in-force row with no scheduled end (until_event/indefinite/
                    unknown) and no status confirmation newer than the cutoff
  verify_backlog    row carrying one or more [VERIFY ...] markers
  unverified_date   date_enacted_uncertainty=unverified

A row can appear in several buckets; `items` is deduplicated by moratorium_id
with a merged `buckets` list, while `bucket_counts` reports raw membership.

Run from repo root:
    python3 scripts/build_worklist.py --today 2026-07-31
    python3 scripts/build_worklist.py --today 2026-07-31 --state MI --pretty
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
WORK_DIR = REPO / "work"

IN_FORCE = {"active", "extended"}

# Captures the whole marker so the research agent sees the actual question,
# e.g. "[VERIFY exact rescission timeline]".
VERIFY_MARKER_RE = re.compile(r"\[VERIFY[^\]]*\]", re.IGNORECASE)

# Priority ordering drives which states get researched first.
BUCKET_PRIORITY = {
    "expired_in_force": 1,
    "until_date_stale": 2,
    "stale_pending": 3,
    "open_ended": 4,
    "verify_backlog": 5,
    "unverified_date": 6,
}

# Fields whose free text a researcher needs to answer the question.
CONTEXT_FIELDS = [
    "date_enacted", "duration", "legal_basis", "trigger",
    "current_status", "affected_projects", "outcome",
]


def parse_iso(value: str) -> dt.date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def computed_expiry(row: dict) -> dt.date | None:
    """date_enacted_iso + duration_days, when both are usable."""
    start = parse_iso(row["date_enacted_iso"])
    raw = row["duration_days"].strip()
    if start is None or not raw:
        return None
    try:
        days = int(float(raw))
    except ValueError:
        return None
    return start + dt.timedelta(days=days)


def verify_markers(row: dict) -> list[dict]:
    out = []
    for field, value in row.items():
        for marker in VERIFY_MARKER_RE.findall(value or ""):
            out.append({"field": field, "marker": marker})
    return out


def classify(row: dict, today: dt.date, pending_age: int) -> list[str]:
    buckets: list[str] = []
    status = row["enacted_status"]
    kind = row["duration_kind"]

    if status in IN_FORCE:
        expiry = computed_expiry(row)
        if expiry is not None and expiry < today:
            buckets.append("expired_in_force")
        elif kind == "until_date":
            buckets.append("until_date_stale")
        elif kind in {"until_event", "indefinite", "unknown"}:
            buckets.append("open_ended")

    if status == "pending":
        enacted = parse_iso(row["date_enacted_iso"])
        # Pending rows usually have no ISO date; fall back to always flagging
        # them, since a proposal is only newsworthy until it is decided.
        if enacted is None or (today - enacted).days >= pending_age:
            buckets.append("stale_pending")

    if VERIFY_MARKER_RE.search(" ".join(v or "" for v in row.values())):
        buckets.append("verify_backlog")

    if row["date_enacted_uncertainty"] == "unverified":
        buckets.append("unverified_date")

    return buckets


def build_item(row: dict, buckets: list[str], today: dt.date) -> dict:
    expiry = computed_expiry(row)
    item = {
        "moratorium_id": row["moratorium_id"],
        "state": row["state"],
        "state_abbrev": row["state_abbrev"],
        "jurisdiction": row["jurisdiction"],
        "jurisdiction_type": row["jurisdiction_type"],
        "enacted_status": row["enacted_status"],
        "date_enacted_iso": row["date_enacted_iso"],
        "date_enacted_uncertainty": row["date_enacted_uncertainty"],
        "duration_days": row["duration_days"],
        "duration_kind": row["duration_kind"],
        "computed_expiry": expiry.isoformat() if expiry else None,
        "days_past_expiry": (today - expiry).days if expiry and expiry < today else None,
        "buckets": sorted(buckets, key=lambda b: BUCKET_PRIORITY[b]),
        "priority": min(BUCKET_PRIORITY[b] for b in buckets),
        "verify_markers": verify_markers(row),
        "context": {f: row[f] for f in CONTEXT_FIELDS if row.get(f)},
        "questions": [],
    }

    # Turn each bucket into an explicit question so the researcher is not
    # inferring what we want to know.
    q = item["questions"]
    if "expired_in_force" in buckets:
        q.append(
            f"This row is recorded as {row['enacted_status']}, but its original term ran out on "
            f"{expiry.isoformat() if expiry else 'an unknown date'}. As of {today.isoformat()}, was it "
            "extended (new end date?), replaced by a permanent ordinance (which one, adopted when?), "
            "allowed to expire, or rescinded?"
        )
    if "until_date_stale" in buckets:
        q.append(
            "This moratorium ends on a fixed calendar date recorded only in free text. "
            f"What is that date, and as of {today.isoformat()} has it passed? If so, what followed?"
        )
    if "stale_pending" in buckets:
        q.append(
            f"This instrument was still only proposed as of the last refresh. As of {today.isoformat()}, "
            "was it adopted (date and instrument number?), rejected, tabled, or withdrawn?"
        )
    if "open_ended" in buckets:
        q.append(
            "This moratorium has no scheduled end date. Confirm it is still in force as of "
            f"{today.isoformat()}, or identify the ordinance/event that ended it."
        )
    if "verify_backlog" in buckets:
        for marker in item["verify_markers"]:
            q.append(f"Resolve {marker['marker']} in field `{marker['field']}` with a primary source.")
    if "unverified_date" in buckets:
        q.append(
            f"The adoption date ({row['date_enacted_iso'] or 'none recorded'}) is unverified. "
            "Confirm it against minutes or the signed instrument."
        )
    return item


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", default=None, help="reference date YYYY-MM-DD (default: system date)")
    ap.add_argument("--pending-age", type=int, default=60,
                    help="days before a pending row is considered stale (default: 60)")
    ap.add_argument("--state", default="", help="comma-separated state abbreviations to restrict output")
    ap.add_argument("--out", default=None, help="output path (default: work/worklist-<today>.json)")
    ap.add_argument("--pretty", action="store_true", help="print a human-readable summary")
    args = ap.parse_args()

    today = dt.date.today() if args.today is None else dt.date.fromisoformat(args.today)
    only = {s.strip().upper() for s in args.state.split(",") if s.strip()}

    with open(INV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    items: list[dict] = []
    bucket_counts: Counter = Counter()
    for row in rows:
        if only and row["state_abbrev"].upper() not in only:
            continue
        buckets = classify(row, today, args.pending_age)
        if not buckets:
            continue
        bucket_counts.update(buckets)
        items.append(build_item(row, buckets, today))

    items.sort(key=lambda i: (i["priority"], i["state_abbrev"], i["jurisdiction"]))

    by_state: dict[str, list[str]] = defaultdict(list)
    for item in items:
        by_state[item["state_abbrev"]].append(item["moratorium_id"])

    payload = {
        "generated_for": today.isoformat(),
        "source": "data/moratorium_inventory.csv",
        "total_rows_scanned": len(rows),
        "items_needing_research": len(items),
        "bucket_counts": dict(bucket_counts.most_common()),
        "states_touched": len(by_state),
        "by_state": {k: sorted(v) for k, v in sorted(by_state.items())},
        "items": items,
    }

    out_path = Path(args.out) if args.out else WORK_DIR / f"worklist-{today.isoformat()}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {out_path.relative_to(REPO)}")
    print(f"  {len(items)} of {len(rows)} rows need research, across {len(by_state)} states")
    for bucket, count in bucket_counts.most_common():
        print(f"  {bucket:18s} {count}")

    if args.pretty:
        print("\nBy state (research fan-out units):")
        for abbrev, ids in sorted(by_state.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            print(f"  {abbrev:3s} {len(ids):3d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
