#!/usr/bin/env python3
"""Stage an archived Ballotpedia table into unreviewed discovery seeds, never facts.

Requires bs4 and bc-spec in the bc-modules runtime. Does not fetch or overwrite
canonical data; retained source snapshots can be independently replayed.
"""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin


def stage(source, output):
    from bs4 import BeautifulSoup
    raw = source.read_bytes()
    soup = BeautifulSoup(raw, "html.parser")
    source_hash = hashlib.sha256(raw).hexdigest()
    seeds = []
    for table in soup.find_all("table"):
        heading = table.find_previous(["h2", "h3"])
        label = heading.get_text(" ", strip=True).replace("[ edit ]", "").strip() if heading else ""
        try:
            day = dt.datetime.strptime(label + " 2026", "%B %d %Y").date().isoformat()
        except ValueError:
            continue
        for tr in table.find_all("tr"):
            cells = tr.find_all("td", recursive=False)
            if len(cells) < 5:
                continue
            title_anchor = cells[3].find("a", href=True)
            url = urljoin("https://ballotpedia.org/", title_anchor["href"]) if title_anchor else None
            identity = url or "|".join([day, cells[0].get_text(), cells[1].get_text(), cells[3].get_text()])
            seeds.append({"seed_id": "bp-" + hashlib.sha256(identity.encode()).hexdigest()[:16],
                "election_date_reported": day, "jurisdiction_reported": cells[0].get_text(" ", strip=True),
                "state_abbrev_reported": cells[1].get_text(" ", strip=True),
                "placement_reported": cells[2].get_text(" ", strip=True),
                "title_reported": cells[3].get_text(" ", strip=True), "measure_url": url,
                "source_url": "https://ballotpedia.org/Data_center-related_ballot_measures,_2026",
                "source_body_sha256": source_hash, "review_status": "unreviewed",
                "disposition": "not_attempted", "candidate_only": True})
    ids = [x["seed_id"] for x in seeds]
    if not seeds or len(ids) != len(set(ids)):
        raise ValueError("Empty or duplicate seed extraction: inspect archived markup")
    output.mkdir(parents=True, exist_ok=True)
    (output / "ballot-seeds.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in seeds))
    summary = {"source_body_sha256": source_hash, "records": len(seeds),
               "by_election_date": dict(sorted(Counter(x["election_date_reported"] for x in seeds).items())),
               "by_state": dict(sorted(Counter(x["state_abbrev_reported"] for x in seeds).items())),
               "limitation": "Discovery list from one source, not a complete or verified census; no result/legal-effect acceptance."}
    (output / "seed-manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(stage(a.source, a.output), indent=2))
