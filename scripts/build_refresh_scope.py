#!/usr/bin/env python3
"""Freeze every legacy ID into state packets; no inference of refreshed status."""
import argparse
from collections import defaultdict
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build(as_of, out):
    dt.date.fromisoformat(as_of)
    packets = defaultdict(lambda: {"inventory": [], "state_policy": []})
    sources = {}
    for table, rel, key in [("inventory", "data/moratorium_inventory.csv", "moratorium_id"),
                             ("state_policy", "data/state_legislation.csv", "policy_action_id")]:
        path = ROOT / rel
        with path.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        ids = [r[key] for r in rows]
        if any(not x for x in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"Missing or duplicate source IDs: {rel}")
        sources[table] = {"path": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "records": len(rows)}
        for row in rows:
            packets[row["state_abbrev"]][table].append({"id": row[key], "record_sha256": digest(row),
                "baseline": row, "disposition": "not_attempted", "last_supported_as_of": None})
    out.mkdir(parents=True, exist_ok=True)
    manifests = []
    for state, tables in sorted(packets.items()):
        payload = {"state_abbrev": state, "as_of": as_of, "sources": sources, **tables}
        path = out / (state + ".json")
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        path.write_text(text)
        manifests.append({"state": state, "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                          "sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "counts": {k: len(v) for k, v in tables.items()}})
    manifest = {"as_of": as_of, "sources": sources, "packets": manifests,
                "freshness": {k: {"total": s["records"], "not_attempted": s["records"],
                                  "confirmed": 0, "changed": 0, "unresolved": 0} for k,s in sources.items()},
                "new_discovery_required": {"states": 50, "sectors": ["data_center", "battery_storage", "solar", "wind", "cryptocurrency_mining"]},
                "limitations": ["Packet generation is not research.", "Coverage does not imply all jurisdictions were searched."]}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    m = build(a.as_of, a.output.resolve())
    print(json.dumps({"packets": len(m["packets"]), "freshness": m["freshness"]}, indent=2))
