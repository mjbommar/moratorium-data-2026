#!/usr/bin/env python3
"""Move explicitly state-level actions out of the local-moratoria inventory.

The local inventory's grain is a local-government permitting instrument.  A
state executive or agency action belongs in ``state_legislation.csv`` (the
backward-compatible state-policy tracker) instead.  Refuse a migration unless
the target policy identifier already exists there, and leave a JSON audit trail.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
POLICY = REPO / "data" / "state_legislation.csv"
AUDIT = REPO / "work" / "audit"


def read(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--moratorium-id", required=True)
    ap.add_argument("--policy-identifier", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows, fields = read(INV)
    targets = [r for r in rows if r["moratorium_id"] == args.moratorium_id]
    if len(targets) != 1:
        raise SystemExit(f"expected exactly one inventory row for {args.moratorium_id!r}; found {len(targets)}")
    target = targets[0]
    if target["jurisdiction_type"] != "State":
        raise SystemExit("refusing to remove a non-state inventory row")
    policy_rows, _ = read(POLICY)
    if not any(r["state"] == target["state"] and r["bill"] == args.policy_identifier for r in policy_rows):
        raise SystemExit("refusing migration: matching state-policy row is absent")
    if args.dry_run:
        print(f"Would migrate {args.moratorium_id} to {args.policy_identifier}.")
        return 0
    remaining = [r for r in rows if r is not target]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(remaining)
    INV.write_text(buf.getvalue(), encoding="utf-8", newline="")
    AUDIT.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    (AUDIT / f"migrate-state-action-{stamp}.json").write_text(json.dumps({
        "applied_at": stamp,
        "removed_from_local_inventory": target,
        "state_policy_identifier": args.policy_identifier,
        "reason": "State-level executive action moved to typed state-policy tracker.",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Migrated {args.moratorium_id} to state policy {args.policy_identifier}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
