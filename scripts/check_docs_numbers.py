#!/usr/bin/env python3
"""Check that headline numbers quoted in prose still match the data.

The recurring failure in this repository is not wrong data — it is *stale
narrative*. README.md, docs/codebook.md, and docs/known-gaps.md all quote counts
that were true when written, and nothing detects it when the CSVs move past
them. This script does.

Each claim is matched by a pattern anchored on the words around it, capturing
exactly one number. `--fix` rewrites only the digits inside that capture span, so
the surrounding sentence is never touched; anything the patterns cannot locate is
reported for a human rather than guessed at. Adding a new headline number to the
prose means adding a claim here too, or it will silently go unchecked.

Run from repo root:
    python3 scripts/check_docs_numbers.py         # report drift, exit 1 if any
    python3 scripts/check_docs_numbers.py --fix   # update the numbers in place
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
LEG = REPO / "data" / "state_legislation.csv"
SWEEP = REPO / "data" / "sweep_coverage.json"

VERIFY_RE = re.compile(r"\[VERIFY", re.IGNORECASE)


def load(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def expanded_facts(snapshot: Path) -> dict[str, int]:
    snapshot = snapshot.resolve(strict=True)
    def records(name):
        return [json.loads(line) for line in (snapshot / (name + '.jsonl')).read_text().splitlines() if line.strip()]
    measures, results = records('ballot_measures'), records('measure_results')
    superseded = {row['supersedes_id'] for row in results if row.get('supersedes_id')}
    current = [row for row in results if row['result_observation_id'] not in superseded]
    return {'expanded_records': len(measures),
            'expanded_voted': sum(row['lifecycle'] == 'voted' for row in measures),
            'expanded_scheduled': sum(row['lifecycle'] == 'scheduled' for row in measures),
            'expanded_litigated': sum(row['lifecycle'] == 'litigated' for row in measures),
            'expanded_unknown': sum(row['lifecycle'] == 'unknown' for row in measures),
            'expanded_current_results': len(current),
            'expanded_retained_results': len(results),
            'expanded_result_measures': len({row['measure_id'] for row in current}),
            'expanded_certified_results': sum(row['certification_status'] in ('certified', 'amended_certification') for row in current)}


def facts() -> dict[str, int | float]:
    inv, leg = load(INV), load(LEG)
    from policy_scope_reviews import INFRASTRUCTURE_SCOPE, partition_reviews
    scope = partition_reviews(leg, REPO / 'data/state_policy_scope_reviews.jsonl',
                              scope=INFRASTRUCTURE_SCOPE)
    c = Counter(r["enacted_status"] for r in inv)
    dispositions = json.loads((REPO / "data/release_metadata.json").read_text())["record_dispositions"]
    verify_rows = sum(1 for r in inv if any(VERIFY_RE.search(v or "") for v in r.values()))
    # Sweep coverage drifted once already: the prose said 15 while the data said
    # 18. Check it like any other published number.
    swept = swept_empty = 0
    if SWEEP.exists():
        windows = json.loads(SWEEP.read_text(encoding="utf-8")).get("windows", [])
        if windows:
            swept = len(windows[-1].get("swept_states", []))
            swept_empty = len(windows[-1].get("swept_states_with_no_adoptions_in_window", []))
    return {
        **expanded_facts(REPO / "data/expanded"),
        "review_unresolved": dispositions["unresolved"],
        "review_corrected": dispositions["corrected_resolved"],
        "review_unchanged": dispositions["confirmed_unchanged"],
        'scope_included': len(scope['reviewed_include']),
        'scope_excluded': len(scope['reviewed_exclude']),
        'scope_unresolved': len(scope['reviewed_unresolved']),
        'scope_unreviewed': len(scope['unreviewed']),
        'scope_candidates': len(leg) - len(scope['reviewed_exclude']),
        "rows": len(inv),
        "raw_records": len(inv) + len(leg),
        "in_force": c["active"] + c["extended"],
        "active": c["active"],
        "extended": c["extended"],
        "ungeocoded": sum(not r['latitude'].strip() for r in inv),
        "geocoded_percent": round(100*sum(bool(r['latitude'].strip()) for r in inv)/len(inv),1),
        "active": c["active"],
        "extended": c["extended"],
        "replaced": c["replaced"],
        "expired": c["expired"],
        "rescinded": c["rescinded"],
        "rejected": c["rejected"],
        "unknown": c["unknown"],
        "pending": c["pending"],
        "past": c["replaced"] + c["expired"] + c["rescinded"],
        "states": len({r["state"] for r in inv}),
        "states_without": 50 - len({r["state"] for r in inv}),
        "verify_rows": verify_rows,
        "unflagged_rows": len(inv) - verify_rows,
        "geocoded": sum(1 for r in inv if r["latitude"].strip()),
        "bills": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill"),
        "state_policy_actions": len(leg),
        "policy_resolutions": sum(r.get("policy_instrument_type") == "legislative_resolution" for r in leg),
        "policy_precursors": sum(r.get("policy_instrument_type") == "legislative_precursor" for r in leg),
        "policy_amendments": sum(r.get("policy_instrument_type") == "legislative_amendment" for r in leg),
        "policy_other_actions": sum(r.get("policy_instrument_type", "bill") not in {"bill", "legislative_resolution", "legislative_precursor", "legislative_amendment"} for r in leg),
        "bills_typed": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill" and r.get("bill_status_category")),
        "bills_enacted": sum(1 for r in leg if r.get("policy_instrument_type", "bill") == "bill" and r.get("bill_status_category") == "enacted"),
        "swept": swept,
        "unswept": 50 - swept,
        "swept_empty": swept_empty,
    }


# Each claim: (file, regex with one capturing group, fact key, human description).
# Patterns are anchored on distinctive surrounding words so they cannot drift
# onto an unrelated number.
CLAIMS: list[tuple[str, str, str, str]] = [
    ('docs/known-gaps.md', r'All ([\d,]+) raw IDs now have review accounting', 'raw_records', 'known gaps full raw review population'),
    ('docs/expanded-data-contracts.md', r'records currently cover ([\d,]+) reviewed proposal', 'expanded_records', 'expanded contract measure count'),
    ('docs/refresh-operations.md', 'and ([\\d,]+) measure/proposal records', 'expanded_records', 'operations measures'),
    ('docs/refresh-operations.md', 'with ([\\d,]+) retained results', 'expanded_retained_results', 'operations retained results'),
    ('docs/refresh-operations.md', 'and ([\\d,]+) current observations', 'expanded_current_results', 'operations current observations'),
    ('docs/refresh-operations.md', 'current observations across ([\\d,]+) measures', 'expanded_result_measures', 'operations measures with results'),
    ("CHANGELOG.md", r"Current working snapshot: .*?and \*\*([\d,]+) proposal/measure records\*\*", "expanded_records", "CHANGELOG current ballot denominator"),
    ("CHANGELOG.md", r"Current working snapshot: .*?with \*\*([\d,]+) current result observations\*\*", "expanded_current_results", "CHANGELOG current result denominator"),
    ("docs/known-gaps.md", r"the current ([\d,]+) local and [\d,]+ state-policy records\.", "rows", "Known gaps current local denominator"),
    ("docs/known-gaps.md", r"the current [\d,]+ local and ([\d,]+) state-policy records\.", "state_policy_actions", "Known gaps current policy denominator"),
    ("docs/codebook.md", r"`moratoria_without_verify_tags`: ([\d,]+)", "unflagged_rows", "codebook unflagged inventory rows"),
    ("docs/ballot-results.md", r"\*\*([\d,]+) measures and proposals", "expanded_records", "Ballot view record denominator"),
    ("docs/ballot-results.md", r"proposals · ([\d,]+) current result reports", "expanded_current_results", "Ballot view current observations"),
    ("docs/ballot-results.md", r"reports · ([\d,]+) certified result reports", "expanded_certified_results", "Ballot view current certified observations"),
    ("docs/codebook.md", r"\*\*The intended grain is one moratorium instrument per row\.\*\* ([\d,]+) rows total", "rows", "codebook inventory rows"),
    ("docs/codebook.md", r"`total_local_moratoria`: ([\d,]+)", "rows", "codebook total_local_moratoria"),
    ("docs/codebook.md", r"`total_state_bills`: ([\d,]+)", "bills", "codebook total_state_bills"),
    ("docs/codebook.md", r"`total_state_policy_actions`: ([\d,]+)", "state_policy_actions", "codebook total_state_policy_actions"),
    ("docs/codebook.md", r"`states_with_moratoria`: (\d+)", "states", "codebook states_with_moratoria"),
    ("docs/codebook.md", r"`states_without_moratoria`: (\d+)", "states_without", "codebook states_without_moratoria"),
    ("docs/codebook.md", r"`moratoria_with_verify_tags`: (\d+)", "verify_rows", "codebook verify row count"),
    ("docs/known-gaps.md", r"\*\*(\d+) of (?:the )?[\d,]+ inventory rows\*\* have at least one such evidence-ceiling note", "verify_rows", "known-gaps verify rows"),
    ("docs/known-gaps.md", r"\*\*[\d,]+ of (?:the )?([\d,]+) inventory rows\*\* have at least one such evidence-ceiling note", "rows", "known-gaps verify denominator"),
    ("docs/known-gaps.md", r"(\d+) of [\d,]+ instruments have WGS84 reference points", "geocoded", "known-gaps geocoded"),
    ("docs/known-gaps.md", r"The (\d+) blanks comprise", "ungeocoded", "known-gaps coordinate gaps"),
    ("docs/known-gaps.md", r"(\d+) moratoria are classified active or extended", "in_force", "known-gaps current in-force"),
    ("docs/known-gaps.md", r"[\d,]+ of ([\d,]+) instruments have WGS84 reference points", "rows", "known-gaps geocoded denominator"),
    # CHANGELOG claims are checked against the NEWEST entry only (see
    # changelog_head below). Older entries are history: their numbers were true
    # when written and must never be "fixed" to today's data.
    ("CHANGELOG.md", r"\| Moratoria in the list \|[^\n]*\*\*([\d,]+)\*\* \|", "rows", "CHANGELOG current rows"),
    ("CHANGELOG.md", r"\| Classified active or extended \|[^\n]*\*\*([\d,]+)\*\* \|", "in_force", "CHANGELOG current in-force"),
    ("CHANGELOG.md", r"\| Pending or not yet effective \|[^\n]*\*\*(\d+)\*\* \|", "pending", "CHANGELOG current pending"),
    ("CHANGELOG.md", r"\| Ended \(replaced, expired, or rescinded\) \|[^\n]*\*\*(\d+)\*\* \|", "past", "CHANGELOG current past"),
    ("CHANGELOG.md", r"\| Rows we still want to confirm \(`\[VERIFY\]`\) \|[^\n]*\*\*(\d+)\*\* \|", "verify_rows", "CHANGELOG current verify rows"),
    ("CHANGELOG.md", r"\| States with at least one \|[^\n]*\*\*(\d+)\*\* \|", "states", "CHANGELOG current states"),
    ("docs/known-gaps.md", r"\*\*All (\d+) states were swept\*\*", "swept", "known-gaps swept states"),
    ("docs/known-gaps.md", r"\*\*(\d+) states recorded no local adoption during the window\*\*", "swept_empty", "known-gaps empty-sweep states"),
    ('README.md', '\\| Local\\ moratoria\\ and\\ proposals \\| ([\\d,]+) \\|', 'rows', 'README.md Local moratoria and proposals'),
    ('README.md', '\\| State\\ policies\\ and\\ proposals \\| ([\\d,]+) \\|', 'state_policy_actions', 'README.md State policies and proposals'),
    ('README.md', '\\| Ballot\\ measures\\ and\\ proposals \\| ([\\d,]+) \\|', 'expanded_records', 'README.md Ballot measures and proposals'),
    ('README.md', '\\| Active \\| ([\\d,]+) \\|', 'active', 'README.md Active'),
    ('README.md', '\\| Extended \\| ([\\d,]+) \\|', 'extended', 'README.md Extended'),
    ('README.md', '\\| Pending \\| ([\\d,]+) \\|', 'pending', 'README.md Pending'),
    ('README.md', '\\| Replaced \\| ([\\d,]+) \\|', 'replaced', 'README.md Replaced'),
    ('README.md', '\\| Expired \\| ([\\d,]+) \\|', 'expired', 'README.md Expired'),
    ('README.md', '\\| Rescinded \\| ([\\d,]+) \\|', 'rescinded', 'README.md Rescinded'),
    ('README.md', '\\| Rejected \\| ([\\d,]+) \\|', 'rejected', 'README.md Rejected'),
    ('README.md', '\\| Unknown \\| ([\\d,]+) \\|', 'unknown', 'README.md Unknown'),
    ('README.md', '\\| Bill \\| ([\\d,]+) \\|', 'bills', 'README.md Bill'),
    ('README.md', '\\| Legislative\\ resolution \\| ([\\d,]+) \\|', 'policy_resolutions', 'README.md Legislative resolution'),
    ('README.md', '\\| Preliminary\\ legislative\\ memo \\| ([\\d,]+) \\|', 'policy_precursors', 'README.md Preliminary legislative memo'),
    ('README.md', '\\| Legislative\\ amendment \\| ([\\d,]+) \\|', 'policy_amendments', 'README.md Legislative amendment'),
    ('README.md', '\\| Other\\ state\\ action \\| ([\\d,]+) \\|', 'policy_other_actions', 'README.md Other state action'),
    ('README.md', '\\| Included \\| ([\\d,]+) \\|', 'scope_included', 'README.md Included'),
    ('README.md', '\\| Excluded \\| ([\\d,]+) \\|', 'scope_excluded', 'README.md Excluded'),
    ('README.md', '\\| Still\\ unresolved \\| ([\\d,]+) \\|', 'scope_unresolved', 'README.md Still unresolved'),
    ('README.md', '\\| Not\\ yet\\ reviewed \\| ([\\d,]+) \\|', 'scope_unreviewed', 'README.md Not yet reviewed'),
    ('README.md', '\\| Exploratory\\ candidate\\ file \\| ([\\d,]+) \\|', 'scope_candidates', 'README.md Exploratory candidate file'),
    ('README.md', '\\| Vote\\ recorded \\| ([\\d,]+) \\|', 'expanded_voted', 'README.md Vote recorded'),
    ('README.md', '\\| Scheduled \\| ([\\d,]+) \\|', 'expanded_scheduled', 'README.md Scheduled'),
    ('README.md', '\\| In\\ litigation \\| ([\\d,]+) \\|', 'expanded_litigated', 'README.md In litigation'),
    ('README.md', '## Ballot measures[\\s\\S]*?\\| Unknown \\| ([\\d,]+) \\|', 'expanded_unknown', 'README ballot unknown stage'),
    ('data/README.md', '\\| Included \\| ([\\d,]+) \\|', 'scope_included', 'data/README.md Included'),
    ('data/README.md', '\\| Excluded \\| ([\\d,]+) \\|', 'scope_excluded', 'data/README.md Excluded'),
    ('data/README.md', '\\| Still\\ unresolved \\| ([\\d,]+) \\|', 'scope_unresolved', 'data/README.md Still unresolved'),
    ('data/README.md', '\\| Not\\ yet\\ reviewed \\| ([\\d,]+) \\|', 'scope_unreviewed', 'data/README.md Not yet reviewed'),
    ('data/README.md', '\\| Exploratory\\ candidate\\ file \\| ([\\d,]+) \\|', 'scope_candidates', 'data/README.md Exploratory candidate file'),
    ('README.md', 'local records cover ([\\d,]+) states', 'states', 'README states'),
    ('README.md', 'There are ([\\d,]+) local records with verification flags', 'verify_rows', 'README flags'),
    ('README.md', 'queue contains ([\\d,]+) open records', 'review_unresolved', 'README open reviews'),
    ('README.md', 'reviews closed ([\\d,]+) records after corrections', 'review_corrected', 'README corrected reviews'),
    ('README.md', 'and ([\\d,]+) without changes', 'review_unchanged', 'README unchanged reviews'),
    ('README.md', 'There are ([\\d,]+) current result reports', 'expanded_current_results', 'README current reports'),
    ('README.md', 'current result reports for ([\\d,]+) measures', 'expanded_result_measures', 'README measures with reports'),
    ('README.md', 'data keeps ([\\d,]+) result versions', 'expanded_retained_results', 'README all result versions'),
    ('README.md', 'has ([\\d,]+) current reports with certified results', 'expanded_certified_results', 'README certified reports'),
    ('README.md', 'map has coordinates for ([\\d,]+) of', 'geocoded', 'README coordinates'),
    ('README.md', 'map has coordinates for [\\d,]+ of ([\\d,]+) local records', 'rows', 'README map total'),
    ('docs/FAQ.md', 'local inventory has ([\\d,]+) records', 'rows', 'FAQ local records'),
    ('docs/FAQ.md', 'state tracker has ([\\d,]+) records', 'state_policy_actions', 'FAQ state records'),
    ('docs/FAQ.md', 'ballot tracker contains ([\\d,]+) proposals', 'expanded_records', 'FAQ ballot records'),
    ('docs/FAQ.md', 'There are ([\\d,]+) current result reports', 'expanded_current_results', 'FAQ result reports'),
    ('docs/FAQ.md', 'result reports for ([\\d,]+) measures', 'expanded_result_measures', 'FAQ measures with reports'),
    ('docs/FAQ.md', 'There are ([\\d,]+) local records with these flags', 'verify_rows', 'FAQ flags'),
    ('docs/methodology.md', 'local inventory has ([\\d,]+) records', 'rows', 'method local records'),
    ('docs/methodology.md', 'records from ([\\d,]+) states', 'states', 'method states'),
    ('docs/methodology.md', 'files contain ([\\d,]+) records in total', 'raw_records', 'method total records'),
    ('docs/methodology.md', 'ballot tracker contains ([\\d,]+) proposals', 'expanded_records', 'method ballot records'),
    ('docs/methodology.md', 'coordinates for ([\\d,]+) of', 'geocoded', 'method coordinates'),
    ('docs/methodology.md', 'coordinates for [\\d,]+ of ([\\d,]+) local records', 'rows', 'method map total'),
    ('data/README.md', 'local inventory has ([\\d,]+) records', 'rows', 'data local records'),
    ('data/README.md', 'state tracker has ([\\d,]+) records', 'state_policy_actions', 'data state records'),
    ('data/README.md', 'coordinates for ([\\d,]+) of', 'geocoded', 'data coordinates'),
    ('data/README.md', 'coordinates for [\\d,]+ of ([\\d,]+) records', 'rows', 'data map total'),
    ('data/README.md', 'ballot tracker has ([\\d,]+) proposals', 'expanded_records', 'data ballot records'),
    ('data/README.md', 'It keeps ([\\d,]+) result versions', 'expanded_retained_results', 'data retained results'),
    ('data/README.md', 'There are ([\\d,]+) current result reports', 'expanded_current_results', 'data current results'),
    ('data/README.md', 'result reports for ([\\d,]+) measures', 'expanded_result_measures', 'data measures with results'),
    ('states/README.md', 'inventory contains ([\\d,]+) records', 'rows', 'state index records'),
    ('states/README.md', 'records from ([\\d,]+) states', 'states', 'state index states'),
    ('states/README.md', '\\*\\*([\\d,]+) listed as active or extended', 'in_force', 'state index active extended'),
    ('states/README.md', '\\*\\*([\\d,]+) listed as pending', 'pending', 'state index pending'),
    ('states/README.md', '\\*\\*([\\d,]+) listed as past', 'past', 'state index past'),
    ('states/README.md', '\\*\\*([\\d,]+) rejected proposals retained', 'rejected', 'state index rejected'),
    ('states/README.md', '\\*\\*([\\d,]+) with unknown status', 'unknown', 'state index unknown'),
]


def changelog_head(text: str) -> str:
    """The newest CHANGELOG entry: from the first '## ' heading to the second.

    `--fix` rewrites digits in place, so letting it search the whole file once
    overwrote the 2026-08-19 entry's table with later figures. History is not a
    claim about the current data.
    """
    starts = [m.start() for m in re.finditer(r"^## ", text, re.M)]
    if not starts:
        return text
    return text[starts[0]: starts[1] if len(starts) > 1 else len(text)]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite ONLY the captured number in each matched claim, leaving the "
                         "surrounding sentence untouched")
    args = ap.parse_args()
    data = facts()
    problems: list[str] = []
    fixed: list[str] = []
    checked = 0
    missing = 0

    for filename, pattern, key, label in CLAIMS:
        path = REPO / filename
        if not path.exists():
            problems.append(f"{filename}: file not found")
            continue
        original = path.read_text(encoding="utf-8")
        text = original
        offset = 0
        if filename == "CHANGELOG.md" and not pattern.startswith("Current working snapshot:"):
            text = changelog_head(text)
            offset = original.find(text)
        m = re.search(pattern, text)
        if not m:
            missing += 1
            problems.append(f"{filename}: could not locate claim -- {label} (pattern may need updating)")
            continue
        checked += 1
        claimed = Decimal(m.group(1).replace(",", ""))
        actual = data[key]
        if claimed == Decimal(str(actual)):
            continue
        if args.fix:
            # Replace only the digits inside the capture span, so the sentence
            # around them is never touched.
            start, end = (offset + value for value in m.span(1))
            path.write_text(original[:start] + str(actual) + original[end:], encoding="utf-8")
            fixed.append(f"{filename}: {label} {claimed} -> {actual}")
        else:
            problems.append(f"{filename}: {label} says {claimed}, data says {actual}")

    print("Data as shipped:")
    for k in ("rows", "in_force", "pending", "past", "states", "verify_rows", "geocoded", "bills", "bills_typed", "bills_enacted"):
        print(f"  {k:14s} {data[k]}")
    print()

    if fixed:
        print(f"Updated {len(fixed)} number(s):")
        for f in fixed:
            print(f"  {f}")
        print()

    if not problems:
        print(f"All {checked} documented numbers match the data.")
        return 0

    print(f"{len(problems)} problem(s) across {checked + missing} claims:")
    for p in problems:
        print(f"  {p}")
    print("\nUpdate the prose by hand -- these are sentences, not fields.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
