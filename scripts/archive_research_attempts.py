#!/usr/bin/env python3
"""Import successful bounded-client fetches into the existing evidence archive.

No refetches. Body/text hashes are checked before creating immutable versioned
files. New text stays ignored until the normal source classifier reviews it.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def import_attempts(directory, state, apply=False):
    if len(state) != 2 or not state.isalpha() or not state.isupper():
        raise ValueError("State must be two uppercase letters")
    ledger = directory / "attempts.private.jsonl"
    events = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
    dest = ROOT / "work/sources" / state
    manifest = dest / "manifest.jsonl"
    old = [json.loads(x) for x in manifest.read_text().splitlines() if x.strip()] if manifest.exists() else []
    seen = {(x["url"], x.get("sha256")) for x in old}
    added = []
    for e in events:
        if e["state"] != "finished" or e["kind"] != "fetch" or not e.get("ok") or not e.get("chars"):
            continue
        metadata_path = Path(e["artifact"])
        stem = metadata_path.with_suffix("")
        raw = stem.with_suffix(stem.suffix + ".body").read_bytes()
        text_bytes = stem.with_suffix(stem.suffix + ".txt").read_bytes()
        text = text_bytes.decode("utf-8")
        if hashlib.sha256(raw).hexdigest() != e["body_sha256"] or hashlib.sha256(text_bytes).hexdigest() != e["text_sha256"]:
            raise ValueError(f"Evidence bytes drifted: {e['attempt_id']}")
        if (e["url"], e["body_sha256"]) in seen:
            continue
        key = hashlib.sha256(e["url"].encode()).hexdigest()[:16] + "-" + e["body_sha256"][:12]
        ext = "pdf" if raw.startswith(b"%PDF-") else "bin"
        raw_path, text_path = dest / f"{key}.{ext}", dest / f"{key}.txt"
        row = {"url": e["url"], "final_url": e["final_url"], "status": e["status"], "ok": True,
               "fetched_at": e["finished_at"], "key": key, "sha256": e["body_sha256"],
               "text_sha256": e["text_sha256"], "text_chars": len(text), "title": e.get("title"),
               "text_method": "bc_research.pipeline.document_text via bounded research client",
               "files": [str(x.relative_to(ROOT)) for x in [raw_path, text_path]],
               "attempt_id": e["attempt_id"], "published": False}
        if apply:
            dest.mkdir(parents=True, exist_ok=True)
            for path, body in [(raw_path, raw), (text_path, text.encode())]:
                if path.exists() and path.read_bytes() != body:
                    raise ValueError(f"Refusing archive overwrite: {path}")
                path.write_bytes(body)
            # Default private before appending provenance; classifier can later release text.
            with (dest / ".gitignore").open("a") as f:
                f.write(f"\n/{key}.*\n")
            with manifest.open("a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        seen.add((e["url"], e["body_sha256"]))
        added.append(row)
    return {"apply": apply, "new_sources": len(added), "sources": added}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    p.add_argument("--state", required=True)
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    print(json.dumps(import_attempts(a.directory, a.state, a.apply), indent=2))
