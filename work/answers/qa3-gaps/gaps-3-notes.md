# QA round 3 gaps-3 notes (FL, IN, IL, MD, TN, SC, NV, PA)

Packet: `work/packets/qa3/gaps-3.json` (34 items). Answer file:
`work/answers/qa3-gaps/gaps-3.json` (`state_abbrev: "FL"`, `decisions: []`,
30 `new_candidates`). Researched as of 2026-09-23.

## Evidence-archiving caveat for this multi-state packet

`scripts/check_evidence_archived.py` reads a single `work/sources/<state_abbrev>/manifest.jsonl`
(the file's top-level `state_abbrev`, here `FL`) and checks every cited URL
against it. Because this packet spans 8 states and the schema only allows one
`state_abbrev` per answer file, the checker reports 23 URLs as "not archived"
that are in fact archived and OK — under their own state's manifest (IN, IL,
MD, TN, SC, NV), not FL's. I independently verified all 23 by reading each
candidate's own `work/sources/<ST>/manifest.jsonl` and confirming `ok: true`
with non-zero `text_chars`. `apply_research.py --dry-run` reported no
conflicts (30 candidates added, 0 rows touched). Every URL cited as evidence
in this file was fetched with `scripts/save_source.py` this session.

## Items not added, and why

- **Collier County, FL** (`GAP_ADOPTED_LIKELY`) — Commissioners reaffirmed a
  "zoning in progress" freeze on hyperscale data center applications
  (2026-07-28, unanimous), not a moratorium ordinance or resolution. It has
  no instrument number, no fixed term, and is a discretionary administrative
  posture the board could lift at any time. Per the process doc's guidance
  that a de facto pause is only added when "the instrument itself is framed
  as a moratorium/pause," I judged a ZIP declaration too thin an instrument
  to add as a row (contrast with Tazewell County, IL, below, which is an
  adopted zoning-code *amendment* with operative legal text). Source:
  https://www.naplesnews.com/story/money/business/local/2026/07/29/collier-county-florida-updating-data-center-zoning-rules/91082660007/

- **Hendry County, FL** (`GAP_PENDING`) — WGCU reported the county was
  "expected to" halt data center proposals pending an SB 484 code update
  (2026-08-24); Municode's ordinance index shows nothing past Ordinance
  2026-02 (Jan. 27, 2026, unrelated). No formal moratorium ordinance, vote,
  or resolution was found. Left out as unresolved/unverifiable rather than
  guessed as `pending`, since even the "expected to halt" framing was never
  confirmed as an actual Board action. Source:
  https://www.wgcu.org/government-politics/2026-08-24/hendry-expected-to-halt-data-center-proposals-until-it-updates-code-to-reflect-state-law

- **Pulaski County, IN (BESS)** (`GAP_ADOPTED_UNVERIFIED_EXPIRED`) — Real
  instruments exist (an original 6-month BESS moratorium approved by the APC
  9/11 and set by the commissioners at 6 months, effective Oct. 8; a 6-month
  extension approved at an April 6 commissioners' meeting; and a later
  18-month extension recommendation, Ordinance 2025-04, that the
  commissioners *denied* on Feb. 18). None of the three Pulaski County
  Journal articles found give a year, so I could not construct a reliable
  `date_enacted_iso`/`current_end_date_iso` pair, and the sequence itself is
  ambiguous (is the Feb. 18 denial before or after the "now expired" state
  implied by the carina_bess tracker's blank `expires` field?). Given the
  tracker's own characterization is "LIFTED" with no end date and the
  instrument is clearly no longer in force, I judged the value of adding it
  with unreliable dates too low relative to the risk of a bad row. Sources
  (not cited as evidence since none supports a firm date):
  https://www.pulaskijournal.com/news/battery-energy-storage-system-moratorium-now-place-six-months ,
  https://pulaskijournal.com/news/commissioners-approve-bess-moratorium-extension-table-text-amendments ,
  https://www.pulaskijournal.com/news/commissioners-deny-battery-energy-storage-system-moratorium-recommendation

- **Olyphant, PA** (`GAP_ADOPTED_LIKELY`) — On 2026-04-14 the Borough Council
  first voted 4-3 to adopt a zoning ordinance amendment addressing data
  centers, then reversed on a re-vote (one member switched to "no"), killing
  it; council then voted instead to declare its own zoning invalid and
  pursue a curative amendment under the PA Municipalities Planning Code (the
  "Throop" precedent), giving itself roughly six months. This is a
  procedural stay of the borough's own zoning validity so it can rewrite the
  code — not a moratorium ordinance imposing a permitting freeze — and the
  packet's own tracker notes it was later "Superseded" (by a June 2026
  regulating amendment/settlement). Not added as a distinct moratorium
  instrument. Source:
  https://www.thetimes-tribune.com/2026/04/15/olyphant-invalidates-own-zoning-to-buy-more-time-to-regulate-data-centers/

## Notable corrections to tracker data found during research

- **Holmes County, FL**: all three trackers and the local news article cite
  "Ordinance No. 2026-23." The ordinance itself and the Holmes County
  Clerk's ordinance index both give the correct number as **Ordinance No.
  2026-03** (adopted 2026-06-16). Used 2026-03 in `legal_basis`.

- **Boone County, IN (BESS)**: the carina_bess tracker claims an ACTIVE
  utility-scale BESS moratorium "expires 6/15/2027." That date matches the
  *enactment* date of the existing data-center-only row
  (`in-boone-county-2026`), not a BESS instrument. The actual BESS/solar/wind
  moratorium was Ordinance 2024-06 (through 2026-04-15), which was replaced
  by permanent Energy Overlay District standards (Ordinance 2025-18,
  recorded ~January 2026) before its own stated end date. Recorded as
  `replaced`, not active.

- **Lee County, IL (BESS)**: carina_bess claims "EXPIRED ... expires
  6/1/2026." What I found instead was a March 2026 County Board resolution
  imposing an open-ended moratorium on energy-storage projects pending state
  implementing regulations under Public Act 104-0458 — i.e., apparently
  still active, not expired, as of the most recent primary source located.

## Sector-gap items (existing jurisdiction, different sector than the current row)

Six items (Boone Co. IN, Starke Co. IN, Caroline Co. MD, Jefferson Co. TN,
Lander Co. NV, Nye Co. NV) named jurisdictions that already have a
data-center-sector row in the inventory, with the tracker (mostly
`carina_bess`/`eticaag_bess`) claiming a *separate* battery-storage or
renewable-energy moratorium. In each case I found a genuine, distinct legal
instrument (different ordinance/resolution number, different sector,
usually an earlier enactment date) rather than a duplicate of the existing
row, so these were written as `new_candidates` rather than `decisions`
against the existing `moratorium_id`. Most of these are now `expired` or
`replaced` — their stated terms lapsed months before 2026-09-23 with no
confirmed renewal found — which is itself useful signal that the
BESS-tracker claims skew stale.

## Summary of new_candidates by outcome

- `active`: Holmes County FL, Levy County FL, Ormond Beach FL, Putnam County
  FL, Clark County IN, Howard County IN, Henry County IL, Utica IL,
  Tazewell County IL, Lee County IL (BESS), Ridgely MD, Moore County TN,
  Paris TN, Jasper County SC (14)
- `pending`: Alachua FL, Hillsborough County FL, Martin County FL, Minneola
  FL, Orange County FL, St. Johns County FL, Salisbury MD, Somerset County
  MD, Mount Pleasant SC (9)
- `expired`: Tippecanoe County IN (solar), Starke County IN (BESS/CSES),
  Caroline County MD (BESS), Jefferson County TN (BESS), Lander County NV
  (renewable/BESS) (5)
- `replaced`: Boone County IN (BESS/solar/wind), Nye County NV
  (renewable/BESS) (2)

30 candidates total, 4 items rejected/not added, 34 packet items covered.
