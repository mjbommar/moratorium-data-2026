#!/usr/bin/env python3
"""Refresh the number-bearing parts of index.html from the shipped data.

index.html is the GitHub Pages landing page -- the most public-facing artifact in
this repository -- and until now it had no generator. Its headline counts were
hand-maintained, so they silently kept saying 222 while the inventory grew.

This does NOT regenerate the page. The layout and copy are hand-tuned and worth
keeping; rewriting them from a template would lose that. Instead it performs
anchored replacements on exactly the spans that state a number, leaving
everything else byte-identical. Anything it cannot locate is reported rather
than guessed at, the same discipline as scripts/check_docs_numbers.py.

Run from repo root:
    python3 scripts/build_index.py --check   # report drift, exit 1 if any
    python3 scripts/build_index.py           # apply
"""

from __future__ import annotations

import argparse
import csv
import json
import html as html_lib
import re
import sys
import struct
from collections import Counter
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "index.html"
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"
SWEEP = REPO / "data" / "sweep_coverage.json"

VERIFY_RE = re.compile(r"\[VERIFY", re.IGNORECASE)

# Publication and source clocks are distinct; derive both from release metadata.
_RELEASE = json.loads((REPO / "data/release_metadata.json").read_text())
_RELEASE_DAY = date.fromisoformat(_RELEASE["release_date"])
_SOURCE_DAY = date.fromisoformat(_RELEASE["research_cutoff"].split("T", 1)[0])
RELEASE_VERSION = _RELEASE["version"]
RELEASE_CONTEXT = "Qualified release" if _RELEASE.get("update_status") in {
    "published_qualified_patch_pending_qa", "qualified_release_with_ongoing_qa",
} else "Working QA after"
RELEASE_LABEL = f"{_RELEASE_DAY:%B} {_RELEASE_DAY.day}, {_RELEASE_DAY.year}"
RELEASE_DATE = f"{_RELEASE_DAY.day} {_RELEASE_DAY:%B %Y}"
RELEASE_ISO = _RELEASE_DAY.isoformat()
SOURCE_DATE = f"{_SOURCE_DAY.day} {_SOURCE_DAY:%B %Y}"
SOURCE_LABEL = f"{_SOURCE_DAY:%B} {_SOURCE_DAY.day}, {_SOURCE_DAY.year}"

NUMBER_WORDS = {
    10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen",
    14: "Fourteen", 15: "Fifteen",
}

SLUG = {
    "District of Columbia": "district-of-columbia",
}


def slug_for(state: str) -> str:
    return SLUG.get(state, state.lower().replace(" ", "-"))


def facts() -> dict:
    with open(INV, encoding="utf-8", newline="") as f:
        inv = list(csv.DictReader(f))
    with open(LEG, encoding="utf-8", newline="") as f:
        leg = list(csv.DictReader(f))
    c = Counter(r["enacted_status"] for r in inv)
    by_state = Counter(r["state"] for r in inv)
    swept = []
    if SWEEP.exists():
        w = json.loads(SWEEP.read_text(encoding="utf-8")).get("windows", [])
        if w:
            swept = w[-1].get("swept_states", [])
    # Clause-taxonomy cohort: reported alongside the inventory on the landing
    # page, and easy to mistake for a subset of it. Derive both numbers so the
    # caveat sentence stays true.
    cohort, cohort_j = 0, 0
    analysis = REPO / "data" / "clause_extraction_analysis.json"
    if analysis.exists():
        a = json.loads(analysis.read_text(encoding="utf-8"))
        cohort = a.get("total_records", 0)
        cohort_j = a.get("geographic", {}).get("total_unique_jurisdictions", 0)

    import datetime as _dt
    def _d(v):
        v=(v or "").strip()
        for fmt in ("%Y-%m-%d","%Y-%m","%Y"):
            try: return _dt.datetime.strptime(v, fmt).date()
            except ValueError: pass
        return None
    window_adoptions = sum(
        1 for r in inv
        if (x := _d(r["date_enacted_iso"])) and _dt.date(2026,5,1) <= x <= _dt.date(2026,7,31)
    )
    august_adoptions = sum(
        1 for r in inv
        if (x := _d(r["date_enacted_iso"])) and _dt.date(2026, 8, 1) <= x <= _dt.date(2026, 8, 19)
    )

    expanded = REPO / 'data/expanded'
    measures = [json.loads(line) for line in (expanded / 'ballot_measures.jsonl').read_text().splitlines() if line.strip()]
    results = [json.loads(line) for line in (expanded / 'measure_results.jsonl').read_text().splitlines() if line.strip()]
    superseded = {row['supersedes_id'] for row in results if row.get('supersedes_id')}
    current_results = [row for row in results if row['result_observation_id'] not in superseded]
    share_width, share_height = struct.unpack('>II', (REPO / 'figures/png/map-moratorium-counts.png').read_bytes()[16:24])
    return {
        "share_width": share_width,
        "share_height": share_height,
        "local_status_counts": dict(c),
        "policy_forms": dict(Counter(r['policy_instrument_type'] for r in leg)),
        "ballot_lifecycle": dict(Counter(r['lifecycle'] for r in measures)),
        "ballot_records": len(measures),
        "ballot_current_results": len(current_results),
        "ballot_result_measures": len({r['measure_id'] for r in current_results}),
        "ballot_retained_results": len(results),
        "ballot_certification": dict(Counter(r['certification_status'] for r in current_results)),
        "rows": len(inv),
        "window_adoptions": window_adoptions,
        "august_adoptions": august_adoptions,
        "dated": sum(1 for r in inv if _d(r["date_enacted_iso"])),
        # The chart bins by month, so a year-only date cannot be plotted.
        "plotted": sum(
            1 for r in inv
            if len((r["date_enacted_iso"] or "")[:7]) == 7 and (r["date_enacted_iso"] or "")[4:5] == "-"
        ),
        "fl_rows": by_state.get("Florida", 0),
        "bills_enacted": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill" and r.get("bill_status_category") == "enacted"),
        "cohort": cohort,
        "cohort_jurisdictions": cohort_j,
        "in_force": c["active"] + c["extended"],
        "active": c["active"],
        "extended": c["extended"],
        "pending": c["pending"],
        "replaced": c["replaced"],
        "expired": c["expired"],
        "rescinded": c["rescinded"],
        "rejected": c["rejected"],
        "unknown": c["unknown"],
        "past": c["replaced"] + c["expired"] + c["rescinded"],
        "states": len(by_state),
        "geocoded": sum(1 for r in inv if r["latitude"].strip()),
        "bills": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill"),
        "state_policy_actions": len(leg),
        "top": by_state.most_common(13),
        "swept_count": len(swept),
    }


def top_states_block(top: list[tuple[str, int]]) -> str:
    rows = [
        f'    <div class="row"><a href="states/{slug_for(s)}.html">'
        f"<strong>{s}</strong></a><strong>{n}</strong></div>"
        for s, n in top
    ]
    return "\n".join(rows)


CHANGES_START = "<!-- BEGIN whats-changed (generated by scripts/build_index.py) -->"
CHANGES_END = "<!-- END whats-changed -->"


def changes_section(f: dict) -> str:
    """The release-notes block.

    Delimited by HTML comments so it regenerates in place. Copy follows the
    house style in ../book-template/docs/guides/STYLE.md: front-loaded claims,
    active voice, varied sentence length, no filler transitions.
    """
    return f"""{CHANGES_START}
<section class="release-notes">
  <div class="stamp">{RELEASE_CONTEXT} v{RELEASE_VERSION} &middot; original cohort cutoff {SOURCE_LABEL} &middot; QA continues</div>
  <h2>The November dataset update</h2>
  <p class="lede">The inventory tracks {f['rows']} local inventory records across {f['states']} states.
  Recorded classifications include {f['active']} active and {f['extended']} extended records,
  {f['pending']} pending, {f['replaced']} replaced, {f['expired']} expired, {f['rescinded']} rescinded, {f['rejected']} rejected proposals and {f['unknown']} unknown.
  Source dates vary by record; these totals do not establish freshly verified current legal force.</p>
  <h3>Ballots and state policy have separate denominators</h3>
  <p><a href="docs/ballot-results.html">Reviewed ballot results</a> distinguish vote observations,
  certification and legal effect. Proposed initiatives and intended election dates do not establish
  ballot appearance; recorded litigation is distinct from electoral defeat. Advisory questions, permanent prohibitions and site-specific
  rezoning votes are not added to the local moratorium total merely because they concern data centers.
  <a href="docs/known-gaps.html">Known gaps</a> retains unresolved candidates and instrument histories.</p>
  <p>The state-policy tracker contains {f['state_policy_actions']} records spanning several mechanisms.
  It is not a count of enacted state moratoria or a deduplicated count of independent bills.
  Reviewed precursor memos and legislative resolutions have separate legal-form types; memo links
  to numbered bills do not merge their identities. Compound rows and unresolved identity grains remain.
  Read the typed mechanism, scope, legal-effect fields and documented identity gaps.</p>
  <h3>Coverage and historical material</h3>
  <p>Searches across all states do not establish a complete census. Later discovery found instruments
  missed in earlier searches, including the May–July window. The April 2026 paper and older graphics
  retain their own historical cohorts; they are not evidence of synchronization with this working data.
  A published release and verified deployment remain separate deliverables.</p>
</section>
{CHANGES_END}"""


DASHBOARD_START = '<!-- BEGIN dashboard-summaries -->'
DASHBOARD_END = '<!-- END dashboard-summaries -->'


def dashboard_section(f: dict) -> str:
    def table(title, rows, total, caption):
        body = ''.join(f'<tr><th scope="row">{html_lib.escape(label)}</th><td>{count:,}</td></tr>' for label, count in rows)
        return f'<div class="dashboard-card"><h3>{title}</h3><table><caption>{caption}</caption><thead><tr><th scope="col">Classification</th><th scope="col">Records</th></tr></thead><tbody>{body}</tbody><tfoot><tr><th scope="row">Total</th><td>{total:,}</td></tr></tfoot></table></div>'

    def bars(rows, title, color):
        maximum = max((count for _, count in rows), default=1) or 1
        height = 32 * len(rows) + 26
        content = []
        for i, (label, count) in enumerate(rows):
            y = i * 32 + 15
            width = 235 * count / maximum
            content.append(f'<text x="0" y="{y + 14}" fill="currentColor" font-size="13">{html_lib.escape(label)}</text><rect x="155" y="{y}" width="{width:.2f}" height="19" rx="3" fill="{color}"/><text x="{163 + width:.2f}" y="{y + 14}" fill="currentColor" font-size="13">{count:,}</text>')
        return f'<svg viewBox="0 0 445 {height}" role="img" aria-label="{html_lib.escape(title)}" style="width:100%;height:auto"><title>{html_lib.escape(title)}</title>{"".join(content)}</svg>'

    status = [(label, f['local_status_counts'].get(key, 0)) for key, label in [('active', 'Active'), ('extended', 'Extended'), ('pending', 'Pending'), ('replaced', 'Replaced'), ('expired', 'Expired'), ('rescinded', 'Rescinded'), ('rejected', 'Rejected'), ('unknown', 'Unknown')]]
    certification = [(label, f['ballot_certification'].get(key, 0)) for key, label in [('certified', 'Certified'), ('unofficial', 'Unofficial'), ('unknown', 'Unknown')]]
    amended = f['ballot_certification'].get('amended_certification', 0)
    if amended:
        certification.append(('Amended certification', amended))
    forms = [(key.replace('_', ' ').capitalize(), count) for key, count in sorted(f['policy_forms'].items(), key=lambda item: (-item[1], item[0]))]
    life = ', '.join(f"{count} {key.replace('_', ' ')}" for key, count in sorted(f['ballot_lifecycle'].items()))
    dispositions = _RELEASE['record_dispositions']
    unresolved = dispositions['unresolved']
    certified = f['ballot_certification'].get('certified', 0) + amended
    return f'''{DASHBOARD_START}
<section class="dashboard-summary" aria-labelledby="dashboard-heading">
<style>
.dashboard-summary {{ margin:32px 0; padding:26px 0; border-top:1px solid var(--line); }}
.dashboard-grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:24px; }}
.dashboard-card {{ min-width:0;padding:18px;border:1px solid var(--line);border-radius:10px; }}
.dashboard-card table {{ border-collapse:collapse;width:100%;font-size:14px; }}
.dashboard-card caption {{ text-align:left;color:var(--ink-soft);font-size:13px;padding-bottom:10px; }}
.dashboard-card th,.dashboard-card td {{ text-align:left;padding:7px 3px;border-bottom:1px solid var(--line); }}
.dashboard-card td:last-child,.dashboard-card thead th:last-child {{ text-align:right; }}
.dashboard-card tbody th {{ font-weight:400; }}
.dashboard-card svg {{ margin-bottom:12px; }}
.qa-note {{ padding:16px;border-left:4px solid var(--accent);margin-top:22px; }}
</style>
<h2 id="dashboard-heading">Current data at a glance</h2>
<p>The three trackers count different things. Local records are not added to policy observations or ballot measures.</p>
<div class="dashboard-grid">
<div class="dashboard-card"><h3>Recorded local status</h3>{bars(status, 'Local status counts; tabulated below', '#3975b5')}
<p>{f['rows']:,} inventory records; classifications do not certify current legal force.</p></div>
<div class="dashboard-card"><h3>Ballot result observations</h3>{bars(certification, 'Certification status of current result observations; tabulated below', '#3a8c72')}
<p><strong>{f['ballot_records']} proposal and measure records</strong>: {life}. There are {f['ballot_current_results']} current result observations across {f['ballot_result_measures']} measures and {f['ballot_retained_results']} retained result versions. {certified} current observations are certified.</p>
<p>Multiple reporting scopes can belong to one measure. Certification is separate from approval and operative legal effect.</p>
<a href="docs/ballot-results.html">Read every reviewed result and source →</a><br><a href="data/expanded-csv/measure_results_current.csv" download>Download current results CSV →</a></div>
</div>
<div class="dashboard-grid" style="margin-top:24px">
{table('Local inventory', status, f['rows'], 'Recorded status, one category per local row.')}
{table('State-policy forms', forms, f['state_policy_actions'], 'Raw observations, not a count of enacted restrictions or unique bills.')}
{table('Ballot certification', certification, f['ballot_current_results'], 'Current result observations, including distinct reporting scopes.')}
</div>
<div class="qa-note"><strong>{unresolved:,} record reviews remain unresolved.</strong>
{dispositions['corrected_resolved']:,} are corrected/resolved and {dispositions['confirmed_unchanged']:,} confirmed unchanged within their recorded review scopes. Searches do not establish a complete nationwide census. Original cohort cutoff: {SOURCE_LABEL}; targeted later captures have their own dates.
<a href="docs/known-gaps.html">Read the limitations</a> and <a href="work/research/2026-11-09/post-release-qa/outstanding-record-questions.jsonl">download the remaining questions</a>.
The newly recovered <a href="work/research/2026-11-10/post-release-qa/kentucky-incentive-implementation-review.json">Kentucky executive-order candidate</a> awaits independent review and canonical integration; it is outside the policy count above.</div>
</section>
{DASHBOARD_END}'''


def build_edits(f: dict) -> list[tuple[str, str, str]]:
    """(label, regex, replacement). Each regex must match exactly once."""
    top_n = len(f["top"])
    share = round(sum(n for _, n in f["top"]) * 100 / f["rows"])
    # Prose reads better as a fraction than a percentage at this precision.
    share_phrase = (
        "four in five" if share >= 78 else
        "three in four" if share >= 72 else
        "two in three" if share >= 63 else
        f"{share} percent"
    )
    return [
        ("document title",
         r'(<title>Moratorium Nation \| )\d+(?: Local Moratorium Records \+ State Data Center Restrictions| Local Records, State Policy &amp; Ballot Measures)</title>',
         rf"\g<1>{f['rows']} Local Records, State Policy &amp; Ballot Measures</title>"),
        ("share image width",
         r'(<meta property="og:image:width" content=")\d+(">)',
         rf"\g<1>{f['share_width']}\g<2>"),
        ("share image height",
         r'(<meta property="og:image:height" content=")\d+(">)',
         rf"\g<1>{f['share_height']}\g<2>"),
        ("meta description",
         r'(<meta name="description" content="Open data and a 116-page working paper on )\d+( local-government moratorium records)',
         rf"\g<1>{f['rows']}\g<2>"),
        ("meta description date",
         r'(cryptocurrency mining across the United States\. Updated )[A-Z][a-z]+(?: \d{1,2},)? \d{4}(\.")',
         rf"\g<1>{RELEASE_LABEL}\g<2>"),
        ("og:description",
         r'(<meta property="og:description" content=")\d+( local moratorium records across )\d+( states)',
         rf"\g<1>{f['rows']}\g<2>{f['states']}\g<3>"),
        ("og:description date",
         r'(state policy actions\. Open data, working cohort through )[A-Z][a-z]+ \d{1,2}, \d{4}(\.")',
         rf"\g<1>{SOURCE_LABEL}\g<2>"),
        ("twitter description date",
         r'(state policy actions\. Updated )[A-Z][a-z]+ \d{1,2}, \d{4}(\.")',
         rf"\g<1>{RELEASE_LABEL}\g<2>"),
        ("json-ld dateModified",
         r'("dateModified": ")\d{4}-\d{2}-\d{2}(")',
         rf"\g<1>{RELEASE_ISO}\g<2>"),
        ("og state-policy count",
         r'(<meta property="og:description" content="[^\n]+, plus )\d+( state policy actions\.)',
         rf"\g<1>{f['state_policy_actions']}\g<2>"),
        ("twitter description",
         r'(<meta name="twitter:description" content=")\d+( local moratorium records across )\d+( states, plus )\d+( state policy actions\.)',
         rf"\g<1>{f['rows']}\g<2>{f['states']}\g<3>{f['state_policy_actions']}\g<4>"),
        # The date lives in the hero eyebrow now, not the subtitle.
        ("hero eyebrow date",
         r'(<div class="eyebrow"><span class="dot"></span>Updated )[^<]*(</div>)',
         rf"\g<1>{RELEASE_DATE}\g<2>"),
        ("stat-total",
         r'(<div class="num" id="stat-total">)\d+(</div>)',
         rf"\g<1>{f['rows']}\g<2>"),
        ("stat-in-force",
         r'(<div class="num" id="stat-in-force">)\d+(</div>)',
         rf"\g<1>{f['in_force']}\g<2>"),
        ("stat-pending",
         r'(<div class="num" id="stat-pending">)\d+(</div>)',
         rf"\g<1>{f['pending']}\g<2>"),
        ("stat-total delta",
         r'(<div class="num" id="stat-total">\d+</div>)(?:\s*<div class="delta">[^<]*</div>)?',
         rf'\g<1>\n    <div class="delta">was 222 in April</div>'),
        ("stat-past",
         r'(<div class="num" id="stat-past">)\d+(</div>)',
         rf"\g<1>{f['past']}\g<2>"),
        # This tile carries no id, so anchor on its label instead.
        ("stat-states",
         r'(<div class="num">)\d+(</div>\s*\n\s*<div class="label">States with at least one</div>)',
         rf"\g<1>{f['states']}\g<2>"),
        ("scope local count",
         r'(<strong class="scope-number" id="scope-local-count">)\d+(</strong>)',
         rf"\g<1>{f['rows']}\g<2>"),
        ("scope state count",
         r'(<strong class="scope-number" id="scope-state-count">)\d+(</strong>)',
         rf"\g<1>{f['state_policy_actions']}\g<2>"),
        ("state-policy form description",
         r'(<strong class="scope-number" id="scope-state-count">\d+</strong>\s*)<p>[^<]*</p>',
         rf"\g<1><p>{f['bills']} bills and {f['state_policy_actions'] - f['bills']} other policy observations, including executive actions, resolutions and precursor memos. These are not all enacted or binding.</p>"),
        ("map caption",
         r"(Map shows )\d+( of )\d+( records\.)",
         rf"\g<1>{f['geocoded']}\g<2>{f['rows']}\g<3>"),
        ("top-states heading",
         r"(<h2>Top )\d+( states by moratorium count</h2>)",
         rf"\g<1>{top_n}\g<2>"),
        ("top-states lead",
         r"(?:These|Thirteen|\w+) states hold roughly [\w -]+ of the records we have found\.",
         f"{NUMBER_WORDS.get(top_n, str(top_n))} states hold roughly {share_phrase} of the "
         f"records we have found."),
        ("top-states rows",
         r'(<div class="top-states">\n)(?:.*?\n)*?(  </div>)',
         lambda: top_states_block(f["top"]) + r"\n\g<2>"),
        ("all-states link",
         r"(All )\d+( states with moratoria)",
         rf"\g<1>{f['states']}\g<2>"),
        ("csv row count",
         r"(The )\d+(-row inventory as a CSV)",
         rf"\g<1>{f['rows']}\g<2>"),
        ("timeline caption",
         r'<p class="caption">[^<]*</p>\s*<p class="source">.*?</p>',
         '<p class="caption">Recorded dates in the current inventory, including unverified or scheduled dates. '
         'Each row is counted once by its first recorded sector; dates do not establish adoption or current legal force.</p>\n'
         '  <p class="source">Source: current <code>moratorium_inventory.csv</code>; see '
         '<a href="docs/known-gaps.html">coverage and date limitations</a>.</p>'),
        ("timeline alt text",
         r'alt="Monthly (?:moratorium adoptions|recorded moratorium dates)[^"]*"',
         'alt="Monthly recorded moratorium dates, stacked by first recorded sector, with cumulative dated-record total. Dates may be unverified or scheduled."'),
        # The clause cohort is NOT the inventory -- it was collected before
        # 2026-04-28 and covers 211 jurisdictions. Stating that inline stops the
        # two numbers on this page being read as one.
        ("clause cohort caveat",
         r"\d+ moratorium texts have been read line by line against a 44-clause taxonomy; that "
         r"sample predates 28 April 2026 and covers \d+ jurisdictions, so it describes what "
         r"moratoria contain rather than all \d+ of them\.",
         f"{f['cohort']} moratorium texts have been read line by line against a 44-clause "
         f"taxonomy; that sample predates 28 April 2026 and covers "
         f"{f['cohort_jurisdictions']} jurisdictions, so it describes what moratoria contain "
         f"rather than all {f['rows']} of them."),
        ("status snapshot",
         r'This working snapshot (?:uses a|retains an original) cohort cutoff of <strong>[^<]+</strong>\. '
         r'(?:Later additions retain their own observation and review dates\. )?'
         r'(?:The latest tagged release remains|The latest qualified release is) <strong>v[0-9A-Za-z_.-]+</strong>\.',
         f'This working snapshot retains an original cohort cutoff of <strong>{SOURCE_DATE}</strong>. '
         'Later additions retain their own observation and review dates. '
         f'The latest qualified release is <strong>v{RELEASE_VERSION}</strong>.'),
        ("release qualifications link",
         r'(<a href="https://github.com/mjbommar/moratorium-data-2026/releases/tag/)v[0-9A-Za-z_.-]+(">release qualifications</a>)',
         rf'\g<1>v{RELEASE_VERSION}\g<2>'),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report drift without writing")
    args = ap.parse_args()

    f = facts()
    html = INDEX.read_text(encoding="utf-8")
    original = html
    applied, missing = [], []

    # Insert or refresh the generated "what changed" section.
    block = changes_section(f)
    if CHANGES_START in html:
        start = html.index(CHANGES_START)
        end = html.index(CHANGES_END) + len(CHANGES_END)
        if html[start:end] != block:
            html = html[:start] + block + html[end:]
            applied.append("whats-changed section")
    else:
        anchor = '<main>'
        if anchor in html:
            html = html.replace(anchor, anchor + "\n\n" + block, 1)
            applied.append("whats-changed section (inserted)")
        else:
            missing.append("whats-changed anchor")

    dashboard = dashboard_section(f)
    if DASHBOARD_START in html:
        start = html.index(DASHBOARD_START)
        end = html.index(DASHBOARD_END) + len(DASHBOARD_END)
        if html[start:end] != dashboard:
            html = html[:start] + dashboard + html[end:]
            applied.append('dashboard summaries')
    else:
        html = html.replace(CHANGES_END, CHANGES_END + '\n\n' + dashboard, 1)
        applied.append('dashboard summaries (inserted)')

    for label, pattern, repl in build_edits(f):
        if label == "top-states rows":
            m = re.search(r'(<div class="top-states">\n)((?:.*?\n)*?)(  </div>)', html)
            if not m:
                missing.append(label)
                continue
            new_block = m.group(1) + top_states_block(f["top"]) + "\n" + m.group(3)
            if m.group(0) != new_block:
                html = html[: m.start()] + new_block + html[m.end():]
                applied.append(label)
            continue
        new_html, n = re.subn(pattern, repl, html, count=1)
        if n == 0:
            missing.append(label)
        elif new_html != html:
            html = new_html
            applied.append(label)

    print(f"Data: {f['rows']} records, {f['in_force']} classified active or extended, {f['pending']} classified pending, "
          f"{f['states']} states, {f['geocoded']} geocoded, {f['bills']} bills")

    if missing:
        print(f"\n{len(missing)} anchor(s) NOT FOUND -- update the patterns in this script:")
        for label in missing:
            print(f"  {label}")

    if not applied:
        print("\nindex.html is already current.")
        return 1 if missing else 0

    if args.check:
        print(f"\nindex.html is OUT OF DATE -- {len(applied)} span(s) would change:")
        for label in applied:
            print(f"  {label}")
        return 1

    INDEX.write_text(html, encoding="utf-8")
    print(f"\nWrote index.html ({len(applied)} span(s) updated):")
    for label in applied:
        print(f"  {label}")
    print(f"  bytes {len(original)} -> {len(html)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
