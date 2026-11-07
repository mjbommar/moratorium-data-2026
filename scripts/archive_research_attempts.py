#!/usr/bin/env python3
"""Import successful bounded-client fetches into the existing evidence archive.

No refetches. Body/text hashes are checked before creating immutable versioned
files. New text stays ignored until the normal source classifier reviews it.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]


def public_source_url(url):
    parts=urlsplit(url)
    if (parts.hostname or '').endswith(('.blob.core.windows.net','.blob.core.usgovcloudapi.net')) and 'sig' in parse_qs(parts.query):
        return urlunsplit((parts.scheme,parts.netloc,parts.path,'',''))
    return url


def import_attempts(directory, state, apply=False, raw_root=None, attempt_ids=None):
    if len(state) != 2 or not state.isalpha() or not state.isupper():
        raise ValueError("State must be two uppercase letters")
    ledger = directory / "attempts.private.jsonl"
    events = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
    selected = None if attempt_ids is None else set(attempt_ids)
    if selected is not None:
        available = {e['attempt_id'] for e in events if e.get('state') == 'finished'
                     and e.get('kind') == 'fetch' and e.get('ok') is True}
        if not selected or selected - available:
            raise ValueError('Explicit selection requires known successful fetch attempt IDs')
    dest = ROOT / "work/sources" / state
    manifest = dest / "manifest.jsonl"
    old = [json.loads(x) for x in manifest.read_text().splitlines() if x.strip()] if manifest.exists() else []
    seen = set()
    body_versions = {}
    for previous in old:
        body_key = (previous["url"], previous.get("sha256"))
        body_versions.setdefault(body_key, []).append(previous["key"])
        text_hash = previous.get("text_sha256")
        if not text_hash:
            for filename in previous.get("files", []):
                candidate = ROOT / filename
                if candidate.suffix == ".txt" and candidate.is_file():
                    text_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
                    break
        if text_hash:
            seen.add((*body_key, text_hash))
    added = []
    derivations_path=directory/'reviewed-derivations.json'
    derivations={x['attempt_id']:x for x in json.loads(derivations_path.read_text())} if derivations_path.exists() else {}
    for e in events:
        if e["state"] != "finished" or e["kind"] != "fetch" or not e.get("ok"):
            continue
        if selected is not None and e['attempt_id'] not in selected:
            continue
        metadata_path = Path(e["artifact"])
        stem = metadata_path.with_suffix("")
        raw = stem.with_suffix(stem.suffix + ".body").read_bytes()
        text_bytes = stem.with_suffix(stem.suffix + ".txt").read_bytes()
        text = text_bytes.decode("utf-8")
        if hashlib.sha256(raw).hexdigest() != e["body_sha256"]:
            raise ValueError(f"Evidence bytes drifted: {e['attempt_id']}")
        derivation=derivations.get(e['attempt_id'])
        if derivation:
            derived=Path(derivation['text_artifact']).resolve()
            if (not derived.is_relative_to(directory.resolve()) or derivation['review_status']!='accepted_derivation'
                or derivation['source_body_sha256']!=e['body_sha256']):
                raise ValueError('Invalid extraction lineage: '+e['attempt_id'])
            text_bytes=derived.read_bytes();text=text_bytes.decode('utf-8')
            if hashlib.sha256(text_bytes).hexdigest()!=derivation['derived_text_sha256']:
                raise ValueError('Derived text drift: '+e['attempt_id'])
        elif hashlib.sha256(text_bytes).hexdigest()!=e['text_sha256']:
            raise ValueError(f"Evidence text drifted without reviewed derivation: {e['attempt_id']}")
        if not text.strip():continue
        public_url=public_source_url(e['url']);final_url=public_source_url(e['final_url'])
        text_hash = hashlib.sha256(text_bytes).hexdigest()
        body_key = (public_url, e["body_sha256"])
        if (*body_key, text_hash) in seen:
            continue
        key = hashlib.sha256(public_url.encode()).hexdigest()[:16] + "-" + e["body_sha256"][:12]
        prior_keys = body_versions.get(body_key, [])
        if prior_keys:
            key += "-" + text_hash[:12]
        ext = "pdf" if raw.startswith(b"%PDF-") else "bin"
        raw_path, text_path = dest / f"{key}.{ext}", dest / f"{key}.txt"
        row = {"url": public_url, "final_url": final_url, "status": e["status"], "ok": True,
               "fetched_at": e["finished_at"], "key": key, "sha256": e["body_sha256"],
               "text_sha256": hashlib.sha256(text_bytes).hexdigest(), "text_chars": len(text), "title": e.get("title"),
               "text_method": "bc_research.pipeline.document_text via bounded research client",
               "files": [str(x.relative_to(ROOT)) for x in [raw_path, text_path]],
               "attempt_id": e["attempt_id"], "published": False}
        if 'from_cache' in e or 'revalidated' in e or 'body_observed_at' in e:
            row['retrieval_observation']={
                'from_cache':e.get('from_cache'), 'origin_revalidated':e.get('revalidated'),
                'body_observed_at':e.get('body_observed_at'),
                'origin_attempt_statuses':e.get('origin_attempt_statuses',[]),
                'scope':'Retrieval/cache lineage only; not renewed factual or legal-force acceptance.'}
        if public_url!=e['url'] or final_url!=e['final_url']:
            row['retrieval_url_sha256']=hashlib.sha256(e['url'].encode()).hexdigest()
            row['access_note']='Retrieved through a publicly linked signed download; refresh via its public portal. The unsigned resource identifier may not be directly retrievable.'
            context=directory/'source-link-provenance.json'
            if context.exists():
                supplied=json.loads(context.read_text()).get(e['attempt_id'],{})
                row['source_link_context']={k:supplied[k] for k in ('portal_url','document_label') if k in supplied}
        if prior_keys: row['extraction_variant_of'] = list(prior_keys)
        if derivation:
            row['text_derivation']=derivation
            row['text_method']=derivation.get('method', 'reviewed extraction; see text_derivation')
        if apply:
            dest.mkdir(parents=True, exist_ok=True)
            for path, body in [(raw_path, raw), (text_path, text.encode())]:
                if path.exists() and path.read_bytes() != body:
                    raise ValueError(f"Refusing archive overwrite: {path}")
                if path == raw_path and raw_root is not None and not path.exists():
                    blob=raw_root.resolve()/(e['body_sha256']+'.'+ext)
                    blob.parent.mkdir(parents=True,exist_ok=True)
                    if blob.exists() and blob.read_bytes()!=body:raise ValueError('Raw blob hash conflict')
                    if not blob.exists():blob.write_bytes(body)
                    path.symlink_to(blob)
                elif not path.exists():
                    path.write_bytes(body)
            # Default private before appending provenance; classifier can later release text.
            with (dest / ".gitignore").open("a") as f:
                f.write(f"\n/{key}.*\n")
            with manifest.open("a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        seen.add((*body_key, text_hash))
        body_versions.setdefault(body_key, []).append(key)
        added.append(row)
    return {"apply": apply, "new_sources": len(added), "sources": added,
            "selected_attempt_ids": sorted(selected) if selected is not None else None}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    p.add_argument("--state", required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument('--raw-root',type=Path,help='Durable mounted content-addressed body archive; working raw paths become ignored symlinks')
    p.add_argument('--attempt-id',action='append',help='Archive only these successful original fetches; repeat for explicit cross-state routing')
    a = p.parse_args()
    print(json.dumps(import_attempts(a.directory, a.state, a.apply, a.raw_root, a.attempt_id), indent=2))
