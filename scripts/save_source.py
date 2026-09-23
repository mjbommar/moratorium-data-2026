#!/usr/bin/env python3
"""Fetch a source through bc-web and archive it under work/sources/<ST>/.

Every URL cited in a research answer file should pass through here, so the
evidence behind a row survives link rot and can be re-read without a network.

Saved per URL (name = first 16 hex of sha256 of the normalized URL):
  <hash>.pdf  + <hash>.txt      PDF body and its text (pdftotext; OCR fallback)
  <hash>.html + <hash>.md       HTML body and readability markdown
  <hash>.<ext>                  any other binary (docx, images)
and one line in work/sources/<ST>/manifest.jsonl with url, final_url, status,
tier/engine used, sha256 of the body, title, and the saved paths.

Run with the bc-modules interpreter (bc_web lives there):
    ~/projects/bc/bc-modules/.venv/bin/python scripts/save_source.py --state GA URL [URL ...]
    ... --print          # also print the text/markdown to stdout (first 300 lines)
    ... --mode browser   # force a browser tier (Cloudflare, JS-only portals)
    ... --engine pydoll  # the Cloudflare escalation engine

Re-fetching a URL already in the manifest is skipped unless --refresh.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "work" / "sources"

EXT_BY_TYPE = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "png",
    "image/jpeg": "jpg",
    "text/plain": "txt",
}


def url_key(url: str) -> str:
    try:
        from bc_web.urls import normalize_url  # type: ignore[import-not-found]

        norm = normalize_url(url)
    except Exception:
        norm = url.strip()
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def pdf_text(pdf: Path) -> tuple[str, str]:
    """(text, method). pdftotext per page; OCR any page that yields almost no text.

    Council packets often mix born-digital agendas with scanned minutes or a
    scanned signed resolution, so a whole-document decision would either skip
    the scan or OCR pages that already have text.
    """
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True)
    pages = out.stdout.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    thin = [i + 1 for i, pg in enumerate(pages) if len(re.sub(r"\s", "", pg)) < 120]
    if not thin:
        return out.stdout, "pdftotext"
    if not shutil.which("tesseract") or not shutil.which("pdftoppm"):
        return out.stdout, f"pdftotext ({len(thin)} pages look scanned; no OCR available)"
    max_ocr = 12
    ocred = 0
    for n in thin[:max_ocr]:
        stem = str(pdf.with_suffix("")) + f"-ocr"
        subprocess.run(
            ["pdftoppm", "-r", "200", "-gray", "-f", str(n), "-l", str(n), "-png", str(pdf), stem],
            capture_output=True,
        )
        imgs = sorted(pdf.parent.glob(pdf.stem + "-ocr-*.png"))
        text = ""
        for img in imgs:
            o = subprocess.run(["tesseract", str(img), "-"], capture_output=True, text=True)
            text += o.stdout
            img.unlink(missing_ok=True)
        if text.strip():
            pages[n - 1] = text
            ocred += 1
    method = f"pdftotext + tesseract ({ocred} of {len(thin)} thin pages OCRed"
    if len(thin) > max_ocr:
        method += f"; {len(thin) - max_ocr} not attempted, cap {max_ocr}"
    return "\n\f\n".join(pages), method + ")"


def _looks_textual(raw: bytes) -> bool:
    """CSV/JSON served as octet-stream: decodes as UTF-8 with no control bytes."""
    sample = raw[:4096]
    if not sample:
        return False
    try:
        text = sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return not any(ord(ch) < 32 and ch not in "\t\n\r\f" for ch in text)


def docx_text(path: Path) -> str:
    """Paragraph text from a .docx (WordprocessingML) without extra dependencies."""
    import zipfile
    from xml.etree import ElementTree as ET

    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    try:
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
    except Exception:
        return ""
    paras = []
    for p in root.iter(ns + "p"):
        paras.append("".join(t.text or "" for t in p.iter(ns + "t")))
    return "\n".join(paras)


def manifest_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    urls = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            urls.add(json.loads(line)["url"])
    return urls


async def save(url: str, state_dir: Path, args: argparse.Namespace) -> dict:
    from bc_web.models import FetchRequest
    from bc_web.retriever import Retriever
    from bc_web.settings import BcWebSettings

    key = url_key(url)
    req = FetchRequest(
        url=url,
        mode=args.mode,
        engine=args.engine,
        timeout_ms=args.timeout * 1000,
    )
    async with Retriever(BcWebSettings()) as r:
        result = await r.fetch(req)

    attempts = " -> ".join(f"{a.tier}:{a.engine or '-'}:{a.outcome}" for a in result.attempts)
    entry: dict = {
        "url": url,
        "final_url": result.final_url,
        "status": result.status,
        "ok": result.ok,
        "attempts": attempts,
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "key": key,
        "files": [],
        "title": result.title,
        "error": result.error,
    }
    body_text = ""
    if not result.ok:
        return entry

    content_type = ""
    for k, v in (result.headers or {}).items():
        if k.lower() == "content-type":
            content_type = v.split(";")[0].strip().lower()
    entry["content_type"] = content_type

    if result.raw is not None:
        ext = EXT_BY_TYPE.get(content_type) or (
            "pdf" if result.raw[:5] == b"%PDF-" else "bin"
        )
        raw_path = state_dir / f"{key}.{ext}"
        raw_path.write_bytes(result.raw)
        entry["sha256"] = hashlib.sha256(result.raw).hexdigest()
        entry["files"].append(str(raw_path.relative_to(ROOT)))
        if ext == "pdf":
            body_text, method = pdf_text(raw_path)
            txt_path = state_dir / f"{key}.txt"
            txt_path.write_text(body_text, encoding="utf-8")
            entry["files"].append(str(txt_path.relative_to(ROOT)))
            entry["text_method"] = method
            entry["text_chars"] = len(body_text)
        elif ext == "docx" or result.raw[:4] == b"PK\x03\x04" and b"word/" in result.raw[:4000]:
            if ext != "docx":
                raw_path.rename(state_dir / f"{key}.docx")
                entry["files"][-1] = str((state_dir / f"{key}.docx").relative_to(ROOT))
                raw_path = state_dir / f"{key}.docx"
            body_text = docx_text(raw_path)
            method = "docx paragraphs"
            txt_path = state_dir / f"{key}.txt"
            txt_path.write_text(body_text, encoding="utf-8")
            entry["files"].append(str(txt_path.relative_to(ROOT)))
            entry["text_method"] = method
            entry["text_chars"] = len(body_text)
        elif (
            content_type.startswith("text/")
            or content_type in ("application/json", "application/csv")
            or _looks_textual(result.raw)
        ):
            body_text = result.raw.decode("utf-8", errors="replace")
            method = "decoded " + content_type
            if ext == "bin":
                ext = {"text/csv": "csv", "application/csv": "csv", "application/json": "json"}.get(content_type, "csv" if url.endswith(".csv") else "txt")
                raw_path.rename(state_dir / f"{key}.{ext}")
                entry["files"][-1] = str((state_dir / f"{key}.{ext}").relative_to(ROOT))
            txt_path = state_dir / f"{key}.txt"
            txt_path.write_text(body_text, encoding="utf-8")
            entry["files"].append(str(txt_path.relative_to(ROOT)))
            entry["text_method"] = method
            entry["text_chars"] = len(body_text)
    else:
        html_path = state_dir / f"{key}.html"
        html_path.write_text(result.html or "", encoding="utf-8")
        entry["sha256"] = hashlib.sha256((result.html or "").encode()).hexdigest()
        md_path = state_dir / f"{key}.md"
        body_text = result.markdown or result.text or ""
        header = f"# {result.title or ''}\n\nsource: {url}\nfetched: {entry['fetched_at']}\n\n"
        md_path.write_text(header + body_text, encoding="utf-8")
        entry["files"] += [str(html_path.relative_to(ROOT)), str(md_path.relative_to(ROOT))]
        entry["text_chars"] = len(body_text)
    entry["_body_text"] = body_text
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--state", required=True, help="USPS abbreviation the source is evidence for")
    ap.add_argument("--mode", choices=["auto", "http", "browser"], default="auto")
    ap.add_argument("--engine", choices=["playwright", "rustwright", "pydoll", "patchright"], default=None)
    ap.add_argument("--timeout", type=int, default=45, help="seconds")
    ap.add_argument("--print", action="store_true", help="print the extracted text (first --lines lines)")
    ap.add_argument("--lines", type=int, default=300)
    ap.add_argument("--refresh", action="store_true", help="re-fetch even if already in the manifest")
    args = ap.parse_args()

    state_dir = SOURCES / args.state.upper()
    state_dir.mkdir(parents=True, exist_ok=True)
    manifest = state_dir / "manifest.jsonl"
    seen = manifest_urls(manifest)
    rc = 0
    for url in args.urls:
        if url in seen and not args.refresh:
            key = url_key(url)
            print(f"already saved: {url} -> {state_dir.relative_to(ROOT)}/{key}.*", file=sys.stderr)
            if args.print:
                for cand in (state_dir / f"{key}.txt", state_dir / f"{key}.md"):
                    if cand.exists():
                        lines = cand.read_text(encoding="utf-8").splitlines()
                        print("\n".join(lines[: args.lines]))
                        break
            continue
        entry = None
        for attempt in range(3):
            try:
                entry = asyncio.run(save(url, state_dir, args))
                break
            except (SyntaxError, ImportError, AttributeError) as exc:
                # bc-web is a live workspace; a half-written edit shows up here as an
                # import-time error. Wait and retry rather than failing the archive.
                print(f"bc_web import problem ({exc.__class__.__name__}: {exc}); retry {attempt + 1}/3 in 20 s", file=sys.stderr)
                time.sleep(20)
        if entry is None:
            print(f"FAILED (bc_web unusable) {url}", file=sys.stderr)
            rc = 1
            continue
        body = entry.pop("_body_text", "")
        with manifest.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        status = "saved" if entry["ok"] else "FAILED"
        print(
            f"{status} {entry['status']} [{entry['attempts']}] {url}\n"
            f"  -> {', '.join(entry['files']) or entry.get('error')}"
            + (f"  ({entry.get('text_chars', 0)} chars, {entry.get('text_method', 'markdown')})" if entry["ok"] else ""),
            file=sys.stderr,
        )
        if not entry["ok"]:
            rc = 1
        if args.print and body:
            print("\n".join(body.splitlines()[: args.lines]))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
