#!/usr/bin/env python3
"""Split a worklist into per-state research packets.

Each packet is a self-contained unit of work for one researcher (agent or
person): the rows to investigate, the questions to answer, and the path where
the answer file must be written. Splitting by state matches how the sources are
organized -- one state's municipal portals, minutes, and legislature.

Run from repo root:
    python3 scripts/make_packets.py --worklist work/worklist-2026-07-31.json \\
        --buckets expired_in_force,until_date_stale,stale_pending --tag status
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worklist", required=True, help="path to a worklist JSON from build_worklist.py")
    ap.add_argument("--buckets", default="", help="comma-separated buckets to include (default: all)")
    ap.add_argument("--tag", required=True, help="short label for this pass, e.g. 'status' or 'verify'")
    ap.add_argument("--max-items", type=int, default=None, help="cap items per packet (splits into -part2, ...)")
    ap.add_argument("--outdir", default=None, help="default: work/packets/<tag>/")
    ap.add_argument("--exclude-dir", default=None,
                    help="skip items already present in packets under this directory, so a "
                         "second pass does not re-research what a first pass already covers")
    args = ap.parse_args()

    excluded: set[str] = set()
    if args.exclude_dir:
        for path in Path(args.exclude_dir).glob("*.json"):
            prior = json.loads(path.read_text(encoding="utf-8"))
            excluded.update(i["moratorium_id"] for i in prior.get("items", []))

    worklist = json.loads(Path(args.worklist).read_text(encoding="utf-8"))
    wanted = {b.strip() for b in args.buckets.split(",") if b.strip()}
    as_of = worklist["generated_for"]

    outdir = Path(args.outdir) if args.outdir else REPO / "work" / "packets" / args.tag
    outdir.mkdir(parents=True, exist_ok=True)

    by_state: dict[str, list[dict]] = defaultdict(list)
    for item in worklist["items"]:
        if wanted and not (wanted & set(item["buckets"])):
            continue
        if item["moratorium_id"] in excluded:
            continue
        by_state[item["state_abbrev"]].append(item)

    written = []
    for abbrev, items in sorted(by_state.items()):
        items.sort(key=lambda i: (i["priority"], i["jurisdiction"]))
        chunks = [items]
        if args.max_items:
            chunks = [items[i:i + args.max_items] for i in range(0, len(items), args.max_items)]
        for n, chunk in enumerate(chunks, start=1):
            suffix = "" if len(chunks) == 1 else f"-part{n}"
            name = f"{abbrev}{suffix}.json"
            answer_path = f"work/answers/{args.tag}/{abbrev}{suffix}.json"
            payload = {
                "packet": name,
                "tag": args.tag,
                "state_abbrev": abbrev,
                "researched_as_of": as_of,
                "item_count": len(chunk),
                "answer_file": answer_path,
                "schema": "work/schemas/research_decision.schema.json",
                "items": chunk,
            }
            (outdir / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            written.append((name, len(chunk)))

    total = sum(c for _, c in written)
    print(f"Wrote {len(written)} packet(s) to {outdir.relative_to(REPO)} covering {total} item(s)")
    for name, count in written:
        print(f"  {name:14s} {count:3d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
