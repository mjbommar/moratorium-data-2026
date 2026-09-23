#!/usr/bin/env python3
"""Decide which archived sources may be published, and keep the rest out of git.

`scripts/save_source.py` saves a copy of every page or document an answer file
cites, under work/sources/<ST>/. Many of those are news articles. The text of a
news article belongs to its publisher, so it must not be committed to this
public repository. Public records -- ordinances, resolutions, minutes, agendas,
staff reports posted by a government -- may be.

Every manifest line keeps its URL, fetch date and sha256 either way, so a
private copy can still be matched against the live page. Only the saved text
of a private source stays on the researcher's machine.

A source is PUBLIC only when one of these holds:
  1. its host is a government domain (.gov, .us, .mil) or a municipal records
     platform (CivicClerk, Legistar, Granicus, Municode, eCode360, ...), or
  2. an answer file cites it as a primary record (ordinance, resolution,
     minutes, agenda, staff_report, legislature, court_filing), it was never
     cited as news, and its host does not look like a news outlet.
Everything else, including sources that were saved but never cited, is PRIVATE.
When in doubt the rule says private.

For each state it writes work/sources/<ST>/.gitignore listing the private
files, and sets `"published": true|false` on each manifest line.

Run from repo root:
    python3 scripts/classify_sources.py            # classify and write
    python3 scripts/classify_sources.py --check    # fail if a private file is tracked by git
    python3 scripts/classify_sources.py --report   # list public hosts that rely on rule 2
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "work" / "sources"
ANSWERS = ROOT / "work" / "answers"

PRIMARY_TYPES = {"ordinance", "resolution", "minutes", "agenda", "staff_report", "legislature", "court_filing"}

GOV_HOST = re.compile(
    r"(\.gov$|\.gov\.|\.us$|\.mil$"
    r"|civicclerk\.com$|legistar\.com$|granicus\.com$|municode\.com$|ecode360\.com$"
    r"|civicplus\.com$|boarddocs\.com$|civicweb\.net$|codepublishing\.com$|amlegal\.com$"
    r"|municipalcodeonline\.com$|generalcode\.com$|iqm2\.com$|novusagenda\.com$"
    r"|agendalink\.com$|primegov\.com$|diligent\.community$|townweb\.com$"
    r"|laserfiche\.com$|edocs|egov)",
    re.I,
)

# Hosts that name a place ("chisagocountypress.com") can be newspapers. Any of
# these fragments marks a host as news-like, which blocks rule 2.
NEWS_HOST = re.compile(
    r"(news|press|times|herald|journal|tribune|gazette|post\b|courier|observer|dispatch"
    r"|sentinel|record|daily|weekly|reporter|register|leader|citizen|independent|ledger"
    r"|star|sun\b|patch|tv|radio|fm\b|am\b|echo|messenger|chronicle|bulletin|enterprise"
    r"|review|banner|mail|express|voice|guardian|examiner|telegraph|democrat|republican"
    r"|beacon|standard|advocate|argus|pilot|progress|current|mirror|monitor|times"
    r"|media|magazine|report|wire|today|online|blog|substack|medium\.com|facebook"
    r"|instagram|twitter|x\.com|youtube|reddit|linkedin|yahoo|msn|google|apple"
    r"|bizjournals|al\.com|mlive|nj\.com|cleveland\.com|syracuse\.com|pennlive|masslive"
    r"|silive|oregonlive|lehighvalleylive|wral|wbrc|wtoc|wsaz|wkrn|kare|kcra|wnep|fox\d*"
    r"|abc\d*|nbc\d*|cbs\d*|npr|pbs|public ?media|kunr|kunc|wbhm|wgcu|wink|wcti)",
    re.I,
)


# Reviewed by hand on 2026-09-23: hosts the two rules would publish that are in
# fact news outlets, their CDNs, legal-notice resellers, or other groups'
# trackers and summaries. Their saved text stays private.
PRIVATE_HOSTS = {
    "wnky.com", "wreg.com", "wwmt.com", "kesq.b-cdn.net", "zeta.creativecirclecdn.com",
    "theonefeather.com", "grantcountybeat.com", "nny360.com", "ashlandsource.com",
    "aberdeeninsider.com", "citizenjournal.us", "marketplace.twincities.com",
    "noticeregistry.com", "mytownview.com", "roswellconnections.com", "dcmap.us",
    "mrsc.org", "mml.org",
}


def cited_types() -> dict[str, set[str]]:
    types: dict[str, set[str]] = defaultdict(set)
    for path in ANSWERS.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for item in data.get("decisions", []) + data.get("new_candidates", []):
            if not isinstance(item, dict):
                continue
            for ev in item.get("evidence", []):
                if isinstance(ev, dict) and ev.get("url"):
                    types[ev["url"]].add(ev.get("source_type", "other"))
    return types


def classify(entry: dict, types: dict[str, set[str]]) -> tuple[bool, str]:
    host = urlparse(entry.get("final_url") or entry["url"]).netloc.lower().removeprefix("www.")
    if host in PRIVATE_HOSTS:
        return False, "news or third-party host (reviewed)"
    if GOV_HOST.search(host):
        return True, "government host"
    t = types.get(entry["url"], set()) | types.get(entry.get("final_url") or "", set())
    if t and (t & PRIMARY_TYPES) and "news" not in t and not NEWS_HOST.search(host):
        return True, "cited as a public record"
    return False, ("cited as news" if "news" in t else "not a public record" if t else "never cited")


def tracked_files() -> set[str]:
    out = subprocess.run(["git", "ls-files", "work/sources"], cwd=ROOT, capture_output=True, text=True)
    return set(out.stdout.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if git tracks any private file")
    ap.add_argument("--report", action="store_true", help="list public hosts that rely on rule 2")
    args = ap.parse_args()

    types = cited_types()
    reasons: Counter[str] = Counter()
    rule2_hosts: Counter[str] = Counter()
    private_files: list[str] = []
    for manifest in sorted(SOURCES.glob("*/manifest.jsonl")):
        lines = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
        private_here: list[str] = []
        for entry in lines:
            public, why = classify(entry, types)
            entry["published"] = public
            reasons[why] += 1
            if public and why == "cited as a public record":
                rule2_hosts[urlparse(entry.get("final_url") or entry["url"]).netloc.lower()] += 1
            if not public:
                # Ignore every file derived from this source (<key>.md, .txt,
                # and helper copies such as <key>.md.dec), not only those listed.
                key = entry.get("key") or (Path(entry["files"][0]).name.split(".")[0] if entry.get("files") else "")
                if key:
                    private_here.append(f"{key}.*")
                    private_files.extend(str(p.relative_to(ROOT)) for p in manifest.parent.glob(f"{key}.*"))
        if args.check:
            continue
        manifest.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in lines), encoding="utf-8")
        ignore = manifest.parent / ".gitignore"
        header = (
            "# Written by scripts/classify_sources.py -- do not edit by hand.\n"
            "# Saved copies of news articles and other non-public-record pages stay local;\n"
            "# their URL, fetch date and sha256 remain in manifest.jsonl.\n"
        )
        ignore.write_text(header + "".join(f"/{n}\n" for n in sorted(set(private_here))), encoding="utf-8")

    print("Sources by decision:")
    for why, n in reasons.most_common():
        print(f"  {n:5}  {why}")
    if args.report:
        print("\nPublic under rule 2 (review these hosts):")
        for host, n in rule2_hosts.most_common():
            print(f"  {n:4}  {host}")
    if args.check:
        leaked = sorted(set(private_files) & tracked_files())
        if leaked:
            print(f"\n{len(leaked)} private file(s) are tracked by git, for example:")
            for f in leaked[:10]:
                print(f"  {f}")
            print("Run scripts/classify_sources.py, then `git rm --cached` the files above.")
            return 1
        print("\nNo private source text is tracked by git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
