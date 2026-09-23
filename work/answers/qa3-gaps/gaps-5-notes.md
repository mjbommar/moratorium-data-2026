# QA round 3 gaps-5 — research notes

Packet: `work/packets/qa3/gaps-5.json` (33 jurisdictions: WA 9, MA 7, WI 6, MO 4,
GA 2, IA 2, NH 2, UT 1). Output: `work/answers/qa3-gaps/gaps-5.json`, 25
`new_candidates`, 0 `decisions` (this packet contains only gap items, no
known-row checks). `state_abbrev` is set to `WA` per the process doc even
though the packet spans eight states; evidence was archived under each URL's
own state folder (`work/sources/<ST>/...`) and checked against that state's
manifest, not just WA's.

## Dry-run duplicate flags (not actually duplicates)

`apply_research.py --dry-run` flags three candidates as duplicates of an
existing row because its `instrument_key()` logic treats any jurisdiction
match as a duplicate when either side's `legal_basis` has no parseable
ordinance/resolution number. All three are legitimately distinct instruments
covering a **different sector** than the existing row of the same name:

- **Renton, WA** (new candidate, `battery_storage`, expired 2022, Ordinance
  6061) vs. `wa-renton-2026` (existing row, `data_center`, active 2026). The
  existing row's `legal_basis` has no instrument number, so the script's
  fallback rule fires even though the sectors don't overlap.
- **Skagit County, WA** (new candidate, `battery_storage`, expired 2025,
  interim Ordinance #O20240073 on Ag-NRL farmland) vs.
  `wa-skagit-county-2026` (existing row, `data_center`, active 2026). Same
  issue.
- **Westfield, MA** (new candidate, `battery_storage`, active, Municipal Code
  Section 5-31 interim restriction) vs. `ma-westfield-2026` (existing row,
  `data_center`, active). My candidate's `legal_basis` doesn't cite a bare
  ordinance number the regex can extract ("Municipal Code Section 5-31"),
  so the fallback rule fires.

These should be merged in as additional rows for the same jurisdiction
(the inventory already has this pattern, e.g. Iowa's multi-row
Shelby/Tama/Palo Alto counties, one row per sector), not skipped as true
duplicates.

## Candidates added (25)

| Jurisdiction | State | Status | Confidence | Notes |
|---|---|---|---|---|
| Port Angeles | WA | active | 0.80 | Resolution, 2026-09-01, 6 mo, confirmed unchanged after Sept 16 hearing |
| Puyallup | WA | active | 0.70 | BESS, 12 mo, exact adoption day not confirmed |
| Lincoln County | WA | active | 0.85 | Ordinance 26-02, data center + BESS, 6 mo |
| Bonney Lake | WA | active | 0.75 | BESS, Ordinance 1754, 2026-04-14, 6 mo |
| Renton | WA | expired | 0.60 | BESS, 2022 (pre-2026, inventory missed); distinct sector from existing row |
| Skagit County | WA | expired | 0.70 | BESS, 2024 interim Ag-NRL ordinance; distinct sector from existing row |
| Agawam | MA | active | 0.85 | TOR-2026-4, 270 days, 2026-09-08 |
| Northampton | MA | pending | 0.60 | Hearing scheduled 2026-09-24 (day after this research pass) |
| Plymouth | MA | pending | 0.65 | Fall Town Meeting Article 16, vote 2026-10-17 |
| Southbridge | MA | pending | 0.65 | Hearing held 2026-09-16; council readings not complete |
| Westfield | MA | active | 0.80 | BESS, interim restriction through 2026-09-30, distinct sector from existing row |
| Middleton | WI | active | 0.85 | Ordinance O1689, 2026-06-16, corrects packet's July 1 date |
| Polk County | WI | active | 0.90 | Resolution 29-26, 2026-08-18, county's own resolution register |
| Beetown | WI | active | 0.90 | Ordinance 04172026, interim zoning, up to 2 years |
| Sawyer County | WI | active | 0.75 | 18-month moratorium, county resolution 2026-31 |
| Hampden | WI | active | 0.85 | Ordinance No. 13, 12 mo (+6 possible) |
| Janesville (Rock County town) | WI | active | 0.70 | Upgrades packet's GAP_PENDING: board approved ~2026-08-03 |
| Oak Grove | MO | active | 0.80 | 1-year administrative delay, 2026-08-03 |
| Pacific | MO | active | 0.85 | 1-year stay, waiver mechanism, 2026-08-04 |
| Palmyra | MO | active | 0.80 | Resolution 2026-06, 2026-09-03, no stated term |
| Heard County | GA | expired | 0.60 | 180 days, 2026-03-17 to 2026-09-12; no extension found |
| Buchanan County | IA | extended | 0.75 | 3 sectors combined, extended to 2027-12-31 |
| Jackson County | IA | extended | 0.90 | BESS, full resolution chain 2024-2027-08-31; distinct sector from existing row |
| Bow | NH | active | 0.55 | 1-year, ~2026-09-17; primary town minutes unreadable (JS stub) |
| Milford | UT | active | 0.85 | Ordinance 4-2026, 2026-06-16, 180 days |

## Items rejected / not added (8)

- **Thurston County, WA** — Board of Commissioners unanimously *directed
  staff* to return with a one-year data-center moratorium proposal
  (Commissioner Clouse's motion, amended by Commissioner Mejia to require
  staff to bring back a formal proposal before any vote). No drafted
  ordinance, no scheduled hearing, no vote. Too preliminary per the process
  doc's "discussion/direction is not an instrument" rule. aigridwatch's claim
  of adoption on 2026-08-20 is not substantiated by any source found.
- **Klickitat County, WA** — The tracked 2024 temporary BESS moratorium was
  replaced by a permanent "Industrial-Scale BESS & Solar Ordinance" adopted
  2025-12-17 (confirmed via the county's own BESS/Solar project page and a
  detailed local report on the ordinance's Planning Commission process).
  Carina's "ACTIVE MORATORIUM ... expires 3/4/2027" claim is stale; the
  county has permanent regulations now, not a pause. Per the process doc,
  permanent regulations adopted instead of / after a pause, with no existing
  row, are not recorded as a new candidate.
- **Whatcom County, WA** — Could not verify any temporary BESS moratorium.
  The only Whatcom County BESS-related instrument found is a 2021 *permanent*
  zoning ordinance (AB2021-424) allowing and regulating BESS, not a
  moratorium. carina's claim carries no date at all. Treated as
  unverifiable/likely tracker error.
- **Northfield, MA** — 2024 town-meeting-adopted "moratorium" bylaws on
  large-scale solar/BESS were disapproved by the Massachusetts Attorney
  General's Office in November 2024 for lacking an articulated public
  health/safety/welfare justification. A bylaw the AGO disapproves does not
  take legal effect, so there is no valid enacted moratorium to record as
  either active or expired.
- **Wendell, MA** — Similar pattern: the town's BESS-related general bylaw
  was disapproved by the AGO, and the state Land Court upheld that
  disapproval in March 2026 (four-year "Home Rule" legal fight). No valid
  enacted moratorium currently exists. carina's identical "expires
  5/31/2026" claim for both Northfield and Wendell looks like a
  copy/duplication error in the tracker.
- **Franklin County, MO** — On 2026-01-20 the county's Planning & Zoning
  *Commission* (an advisory recommending body, not the County Commission)
  voted to table its own proposed data-center zoning regulations and two
  pending rezoning requests for six months, after members were told a
  one-year moratorium recommendation would trigger a new public-notice
  requirement. This is a procedural tabling of the P&Z's own recommendation
  process, not an enacted county ordinance/resolution halting applications.
  The Sierra Club's press-release headline calls it a "six-month pause" that
  the county "lifted" around March 16-17, 2026, but the timeline evidence
  (a March 17, 2026 11-hour public meeting, and an April 21, 2026 P&Z
  vote on the rezonings) doesn't cleanly support a clean "adopted then
  rescinded" instrument. Excluded as too ambiguous/procedural to record
  confidently as a moratorium row.
- **Columbia County, GA** — A commission-chair candidate proposed a 180-day
  moratorium at a public meeting; no vote was taken. Meanwhile the county has
  continued approving data center deals (approved a $17B MOU for a Google/
  Kinetic Infrastructure project on 2026-08-26; a Sept. 23, 2026 story
  touts economic-impact projections for the same project). Failed/never-voted
  proposal, contradicted by the county's own active approvals.
- **Keene, NH** — A councilor's request for an ordinance was referred to
  committee and discussed at the Sept. 9, 2026 PLD Committee meeting, but per
  the minutes the city was still at the stage of debating whether to use a
  resolution vs. an ordinance, what definition of "data center" to use, and
  which stakeholders to hear from before drafting anything. No drafted text,
  no scheduled public hearing on specific language. Discussion/referral only,
  not an instrument under the process doc's test.

## Other things worth flagging to the coordinator

- **Town of Janesville (Rock County), WI** — upgrades the packet's
  `GAP_PENDING` verdict to adopted; two independent local papers
  (gazettextra.com, beloitdailynews.com) confirm the Town Board approved the
  moratorium the Monday after the Planning & Zoning Committee's July 28/29
  recommendation. Exact calendar date (2026-08-03) is inferred from "the
  following Monday," not stated verbatim in either source.
- **Bow, NH** — the only candidate at a real-but-lower confidence (0.55): the
  town's own Planning Board minutes PDF returned an empty CivicPlus JS-portal
  stub both times it was fetched (plain and `--mode browser`), and the
  supporting NHPR article's retrieved full text does not itself contain the
  sentence confirming the vote (which appeared only in the search-engine
  snippet of the same URL, suggesting the live page was edited after
  indexing). A contemporaneous Instagram post independently states the same
  outcome. Recommend re-verifying against Bow's primary minutes in a later
  pass once the portal is reachable.
- Several other city/county DocumentCenter and AgendaCenter links (CivicPlus
  JS portals) returned 0-char HTML stubs even in `--mode browser`
  (Bonney Lake, Sawyer County, Oak Grove, Middleton's Azure ordinance
  function, Klickitat County). Where a usable secondary source existed, that
  was cited instead and the stub link was dropped from `evidence` (it would
  have failed `check_evidence_archived.py`); where noted in a candidate's
  `notes`, no working alternative fetch was attempted beyond what's listed.
