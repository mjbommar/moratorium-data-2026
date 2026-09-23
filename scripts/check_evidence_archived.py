#!/usr/bin/env python3
"""Check that every evidence URL in an answer file was archived under work/sources/.

An answer file cites URLs; scripts/save_source.py archives them and records
each in work/sources/<ST>/manifest.jsonl. This reports any cited URL with no
successful manifest entry, so a decision resting on an unsaved page is caught
before merge.

Run from repo root:
    python3 scripts/check_evidence_archived.py work/answers/full/NV.json [more.json ...]
    python3 scripts/check_evidence_archived.py --answers-dir work/answers/full
Exit 1 if any URL is missing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def manifest_ok_urls(state: str) -> set[str]:
    path = ROOT / "work" / "sources" / state / "manifest.jsonl"
    ok: set[str] = set()
    if not path.exists():
        return ok
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("ok") and (e.get("text_chars") or 0) > 0:
            ok.add(e["url"])
            if e.get("final_url"):
                ok.add(e["final_url"])
    return ok


def cited_urls(answer: dict) -> list[tuple[str, str]]:
    out = []
    for d in answer.get("decisions", []):
        for ev in d.get("evidence", []):
            out.append((d["moratorium_id"], ev["url"]))
    for c in answer.get("new_candidates", []):
        for ev in c.get("evidence", []):
            out.append((f"candidate {c['jurisdiction']}", ev["url"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("answers", nargs="*")
    ap.add_argument("--answers-dir")
    args = ap.parse_args()
    paths = [Path(p) for p in args.answers]
    if args.answers_dir:
        paths += sorted(Path(args.answers_dir).glob("*.json"))
    if not paths:
        ap.error("give answer files or --answers-dir")

    missing_total = 0
    for path in paths:
        answer = json.loads(path.read_text(encoding="utf-8"))
        ok = manifest_ok_urls(answer["state_abbrev"])
        cited = cited_urls(answer)
        missing = [(who, url) for who, url in cited if url not in ok]
        seen_urls = {url for _, url in cited}
        print(f"{path.name}: {len(seen_urls)} distinct URLs cited, {len(missing)} not archived")
        for who, url in missing:
            print(f"  MISSING {who}: {url}")
        missing_total += len(missing)
    return 1 if missing_total else 0


if __name__ == "__main__":
    raise SystemExit(main())
