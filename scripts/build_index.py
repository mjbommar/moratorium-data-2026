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
    """Describe the update in plain American English; keep counts tied to data."""
    return f"""{CHANGES_START}
<section class="release-notes">
  <div class="stamp">Updated {RELEASE_LABEL} &middot; v{RELEASE_VERSION}</div>
  <h2>About this update</h2>
  <p class="lede">The local inventory contains {f['rows']:,} records from {f['states']} states. It includes adopted moratoria, proposals, and actions that have ended.</p>
  <p>The status of each record reflects the sources we found. Some dates and legal details remain unconfirmed. A record listed as active may have changed since its source was published.</p>
  <p>This update adds a light and dark mode switch and clarifies the Gallatin, Tennessee, and Rice, Minnesota, records. Rice’s signed September 21 minutes confirm a 5–0 council vote. Final adopted texts, effective dates, and later actions still need review.</p>
  <h3>Local actions, state policy, and ballot measures</h3>
  <p>We count these separately. State bills can change local authority or state permit rules without creating a local moratorium. Ballot measures can ask for a temporary pause, a permanent restriction, or a zoning change. A vote in favor does not always put a restriction into effect.</p>
  <h3>What the search covers</h3>
  <p>We searched all 50 states, but the inventory is not complete. The main November search ended {SOURCE_LABEL}. Later checks have added sources and corrected records. Each record keeps its source dates.</p>
  <p>The <a href="paper/moratorium-nation-2026-04-30.pdf">April paper</a> describes the earlier dataset. Its findings have not been updated to match these records. See the <a href="docs/known-gaps.html">known gaps</a> for more detail.</p>
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
    forms = [({'legislative_precursor':'Preliminary legislative memo','governor_directive':'Governor directive'}.get(key, key.replace('_', ' ').capitalize()), count) for key, count in sorted(f['policy_forms'].items(), key=lambda item: (-item[1], item[0]))]
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
<h2 id="dashboard-heading">What the data contains</h2>
<p>The local inventory, state tracker, and ballot tracker have separate totals.</p>
<div class="dashboard-grid">
<div class="dashboard-card"><h3>Local record status</h3>{bars(status, 'Local records by status; values also appear in the table', '#3975b5')}
<p>These are the statuses listed in the data. They do not confirm that every restriction is still in effect.</p></div>
<div class="dashboard-card"><h3>Ballot results</h3>{bars(certification, 'Ballot result reports by certification status; values also appear in the table', '#3a8c72')}
<p>We track <strong>{f['ballot_records']} proposals and ballot measures</strong>. The chart counts {f['ballot_current_results']} current result reports for {f['ballot_result_measures']} measures. One measure can have reports from more than one area.</p>
<p>{certified} reports contain certified results. Certification confirms the reported vote; it does not by itself show that a restriction has taken effect. The data keeps {f['ballot_retained_results']} report versions, including earlier reports.</p>
<a href="docs/ballot-results.html">Read the results and sources</a><br><a href="data/expanded-csv/measure_results_current.csv" download>Download results CSV</a></div>
</div>
<div class="dashboard-grid" style="margin-top:24px">
{table('Local inventory', status, f['rows'], 'Each local record appears in one status category.')}
{table('State actions by type', forms, f['state_policy_actions'], 'State records by type. These are not all enacted laws or separate bills.')}
{table('Ballot certification', certification, f['ballot_current_results'], 'Latest result reports. A measure may have reports from several areas.')}
</div>
<div class="qa-note"><strong>{unresolved:,} records still have open questions.</strong>
We completed reviews of {dispositions['corrected_resolved']:,} corrected records and {dispositions['confirmed_unchanged']:,} records that needed no changes. Other records still have questions about dates, wording, or later actions.
<a href="docs/known-gaps.html">Read the limitations</a> or <a href="work/research/2026-11-09/post-release-qa/outstanding-record-questions.jsonl">download the remaining questions</a>.
The state tracker includes historical actions such as <a href="states/kentucky.html">Kentucky Executive Order 2026-494</a>. Check each record for its date and status.</div>
</section>
{DASHBOARD_END}'''


def build_edits(f: dict) -> list[tuple[str, str, str]]:
    """Update named elements so editorial changes do not break count checks."""
    def node(ident, text):
        return (ident, rf'(<[^>]+\bid="{ident}"[^>]*>).*?(</[^>]+>)', rf'\g<1>{text}\g<2>')
    def meta(kind, name, text):
        return (name, rf'(<meta {kind}="{name}" content=")[^"]*(">)', rf'\g<1>{text}\g<2>')
    description = (f"Track {f['rows']:,} local moratorium records across {f['states']} states, "
                   f"plus state policy and ballot measures. Updated {RELEASE_LABEL}.")
    share = round(sum(n for _, n in f['top']) * 100 / f['rows'])
    return [
        ('document title', r'<title>[^<]*</title>', ' <title>Moratorium Nation | Local Moratoria, State Policy, and Ballot Measures</title>'.lstrip()),
        meta('name', 'description', description),
        meta('property', 'og:description', description),
        meta('name', 'twitter:description', description),
        meta('property', 'og:image:width', f['share_width']),
        meta('property', 'og:image:height', f['share_height']),
        ('json-ld dateModified', r'("dateModified": ")[^"]*(")', rf'\g<1>{RELEASE_ISO}\g<2>'),
        ('hero eyebrow date', r'(<div class="eyebrow"><span class="dot"></span>Updated )[^<]*(</div>)', rf'\g<1>{RELEASE_LABEL}\g<2>'),
        *[node(ident, f[key]) for ident, key in [('stat-total','rows'),('stat-in-force','in_force'),('stat-pending','pending'),('stat-past','past'),('stat-states','states'),('scope-local-count','rows'),('scope-state-count','state_policy_actions')]],
        node('state-policy-description', f"{f['bills']} bills and {f['state_policy_actions']-f['bills']} other records, including executive actions, resolutions, and preliminary memos. Many are proposals or historical actions."),
        node('map-caption', f"The map shows {f['geocoded']:,} of {f['rows']:,} records. The other two describe groups of proposals rather than single places. Select a marker for details."),
        node('top-states-lead', f"These states account for {share}% of the local records. Select a state to see its records."),
        ('top-states rows', r'(<div class="top-states">\n)(?:.*?\n)*?(  </div>)', lambda: top_states_block(f['top']) + r'\n\g<2>'),
        node('historical-sample', f"An earlier analysis examined {f['cohort']} moratorium texts from {f['cohort_jurisdictions']} jurisdictions, collected before April 28, 2026. Those findings have not been updated for the full inventory."),
        node('source-dates', f"The main November search ended {SOURCE_LABEL}. Later source checks have their own dates. The current data release is v{RELEASE_VERSION}."),
        ('release link', r'(<a id="release-link" href="https://github.com/mjbommar/moratorium-data-2026/releases/tag/)v[0-9A-Za-z_.-]+(">)', rf'\g<1>v{RELEASE_VERSION}\g<2>'),
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
