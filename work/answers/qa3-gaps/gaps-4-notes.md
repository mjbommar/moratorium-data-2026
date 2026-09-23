# QA round 3 gaps-4 notes (NE, CO, TX, MI, ME, NC, LA, OH, OR)

Packet: `work/packets/qa3/gaps-4.json`, 34 items. 30 written as `new_candidates`
in `gaps-4.json` (`state_abbrev: "NE"` per instructions; each candidate carries
its own `state`). 4 items are **not added**, with reasons below.

## Not added

- **Hall County, NE** (GAP_PENDING, "Board debated a 180-day moratorium...").
  **Misattribution.** Traced the tracker chain (aigridwatch -> savrn's
  Nebraska subpage -> its cited source) to
  `https://www.yahoo.com/news/articles/hall-county-commission-debating-180-181103481.html`,
  which is a WSB-TV (Atlanta) story about **Hall County, Georgia** debating a
  180-day data-center moratorium -- not Hall County, Nebraska (Grand Island).
  Hall County, GA already has its own real moratorium activity (confirmed via
  a separate search: accessnorthga.com, gainesvilletimes.com,
  hallcounty.org), which is presumably a genuine gap for **GA**, not NE. No
  Nebraska Hall County data-center moratorium was found in any targeted
  search of Grand Island / Hall County NE sources. Recommend the coordinator
  check whether GA's inventory/packets already cover Hall County, GA.

- **Comstock (Township), MI** (BESS/renewable sector gap flagged against
  existing rows mi-comstock-charter-township-2026/-2026-2, which cover data
  centers and solar/wind respectively, both Ordinances 565/566, adopted
  2026-03-16). Comstock Charter Township's BESS-specific moratorium
  (Ordinance 552, adopted 2025-03-17, one-year term covering BESS >=50MW,
  solar >=50MW, wind >=100MW) was **superseded by permanent BESS zoning
  regulations** (Ordinance 564) adopted 2025-12-15
  (mlive.com: "Comstock Township trustees voted unanimously on Monday, Dec.
  15, to approve an ordinance governing the development of battery energy
  storage systems (BESS) in the township"). Since the county moved to
  permanent regulation rather than a renewed pause, there is no current BESS
  moratorium gap to add.

- **Lee County, NC** (GAP_PENDING, citizen petition for a moratorium set for
  Sept. 21 hearing). Checked the actual Sept. 21, 2026 Board of Commissioners
  meeting coverage (sandhills.news, published 2026-09-22): the board approved
  **incentives for the data center project itself** ("Project Paragon") that
  day; the citizen's petition approved at that meeting concerned an unrelated
  UDO amendment on animal/dog-grooming services, not the data-center
  moratorium petition. No moratorium was adopted. Recording as unresolved/not
  a row: as of 2026-09-23 Lee County has not adopted a data center
  moratorium, and the county in fact voted to move the data center project
  forward.

- **Portland, OR** (GAP_PENDING, council resolution "pursuing" a moratorium).
  Confirmed via oregonlive.com (2026-09-17): the City Council voted 11-0 on a
  resolution that (a) urges city administrators not to sign NDAs with data
  center developers, and (b) states several councilors "next want" a
  moratorium -- but no moratorium ordinance has been drafted, no first
  reading has occurred, and no hearing is scheduled. This is a step short of
  the process doc's "pending" bar (first reading, scheduled hearing, or
  planning-commission recommendation on drafted text); treating it as
  discussion/intent rather than an instrument, consistent with "a council
  member who called for one is not an instrument." Flagging for a future
  pass once Portland actually introduces an ordinance.

## Lower-confidence items worth a follow-up pass

- **NE first-wave counties** (Box Butte, Harlan, Hayes, Johnson, Kearney):
  Nebraska Public Media's two roundup articles are the only source located
  for these counties' data center moratoria (no county-government primary
  source or dated local news account was found within the research budget).
  Added at confidence 0.5 with `date_enacted_uncertainty: year_only`
  ("2026"). A future pass should search each county's own board-of-commissioners
  site (agendas/minutes) the way this pass did successfully for Custer and
  Dundy counties.
- **Furnas County, NE**: only a wind/solar moratorium (Resolution 2025-8-26,
  2025-08-26) was found; no data-center-specific instrument was located
  despite NPM listing the county as having a "data center moratorium."
  Recorded with the real sector (wind/solar) rather than the claimed sector.
- **CO BESS items** (Fremont County, La Plata County, Washington County):
  primary resolutions were found for all three, but exact original adoption
  dates for Fremont and La Plata rest on the eticaag/carina trackers rather
  than a dated primary document (durangoherald.com article was
  paywalled/nav-only; Fremont's resolution PDF has no visible date). Washington
  County's own most-recent extension resolution (2025-11-25) runs only to
  2026-06-30 -- whether it was extended again past that date (i.e., is still
  active as of 2026-09-23) is unconfirmed.
- **TX Pasadena / League City** (BESS): primary/tracker evidence found but
  original adoption dates approximate.
- **MI Wales Township / ME Palermo**: single secondary-source (carina.energy)
  evidence only; no primary ordinance located.
- **Custer County, NE BESS**: the Planning Commission "moved to place a
  12-month moratorium on battery energy storage development" on 2026-08-19
  (ruralradio.com/KRVN), but this reads as a Planning Commission action, and
  Nebraska planning commissions typically only recommend to the Board of
  Supervisors. Not added as a separate candidate for lack of confirmed Board
  adoption; worth checking the Sept./Oct. 2026 Custer County Board of
  Supervisors minutes.
- **Ironton, OH**: Ordinance 26-01 (AI data center moratorium, adopted
  2026-02-12) is written to auto-repeal once companion zoning Ordinance 26-09
  passes. Whether 26-09 has since passed (which would flip this to
  `replaced`) was not checked within budget.

## Notable corrections to packet assessments

- **Lincolnton, NC**: packet said "council delayed a decision... to a
  September hearing." Actual outcome (lincolntimesnews.com, published
  2026-09-04): Council **adopted** a moratorium at its Sept. 3, 2026 meeting
  (a divided 2-2 vote on a 6-month term was broken by the mayor against it,
  then a motion to run the moratorium through Jan. 1, 2027 passed). Written
  up as `enacted_status: active`, not pending.
- **Washington County, CO**: packet's tracker claim said "PENDING MORATORIUM
  ... expires 12/31/2025." The primary resolution found shows the moratorium
  has been in force and repeatedly extended since 2023 (Resolution 88-2023),
  most recently to 2026-06-30 -- i.e., already adopted and long-running, not
  pending.

## Process note: evidence-check tooling and multi-state packets

`scripts/check_evidence_archived.py` resolves the manifest to check against
using the answer file's single top-level `state_abbrev` (here, forced to
`"NE"` per the task instructions). Because this packet spans nine states,
each URL was archived with `save_source.py --state <the candidate's actual
state>` (e.g., CO evidence in `work/sources/CO/`), which is correct per
`work/research-process.md`'s instruction to pass `--state <ST>`, but it means
a plain `check_evidence_archived.py gaps-4.json` run reports false positives
for every non-NE candidate. Verified manually (script below) that all 30
candidates' evidence URLs are archived under their own state's manifest with
non-empty extracted text; 0 missing. Flagging this so the coordinator's merge
step doesn't rely on the single-state assumption baked into that script for
these cross-state gap packets.

```python
# verification used (per-candidate state, not file-level state_abbrev)
import json
from pathlib import Path
d = json.load(open("work/answers/qa3-gaps/gaps-4.json"))
def manifest_ok_urls(state):
    path = Path(f"work/sources/{state}/manifest.jsonl")
    ok = set()
    if not path.exists():
        return ok
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("ok") and (e.get("text_chars") or 0) > 0:
            ok.add(e["url"])
            if e.get("final_url"):
                ok.add(e["final_url"])
    return ok
missing = []
cache = {}
for c in d["new_candidates"]:
    st = c["state"]
    cache.setdefault(st, manifest_ok_urls(st))
    for ev in c["evidence"]:
        if ev["url"] not in cache[st]:
            missing.append((st, c["jurisdiction"], ev["url"]))
print(len(missing), "missing")
```

## Note on an account change (corrected by the coordinator)

Partway through this task the agent saw a system notice that the session's
account had changed. The agent took it for injected web content. It was a
genuine notice: the coordinator's session switched accounts after an API spend
limit interrupted the run. Nothing in this file depends on it.
