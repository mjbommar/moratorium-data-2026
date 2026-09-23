# QA round 3 gaps-2 — research notes

Packet: `work/packets/qa3/gaps-2.json`, 34 items across CA, KS, KY, MN, NM, VA, NJ.
Answer file: `work/answers/qa3-gaps/gaps-2.json` (31 `new_candidates`, 0 `decisions`).

## Items NOT added, with reasons

**San Joaquin County, CA (GAP_ADOPTED in packet).** The packet's assessment leaned
on a Lodi News-Sentinel article ("San Joaquin County puts data centers on hold,"
2026-09-03) whose headline and lede say the board "unanimously approved a
45-day moratorium." The county's own official press release
(sjgov.org, dated 2026-09-01/02, archived) and a matching Manteca Bulletin
article both say the Board only "voted to direct County staff to study" the
issue and that "it's expected that in October... the Board will consider an
initial 45-day moratorium." No moratorium has been adopted; the vote is
expected in October 2026. Treated the news report as inaccurate/premature
rather than the primary source. Not added.

**Monterey County, CA (BESS, GAP_PENDING_UNVERIFIED).** On 2025-10-28 the Board
of Supervisors directed staff to draft moratorium language (Supervisor Glenn
Church's proposal) after the Moss Landing/California Flats BESS fires. No
adopted or even publicly drafted ordinance was found nearly a year later; by
March 2026 the county had pivoted to a general community-meeting process for
permanent BESS regulations (comrny.us/BESS) rather than an active moratorium
proposal on a commission agenda. This does not meet the "first reading /
scheduled hearing on a drafted ordinance" bar for `pending`. Not added.

**San Diego County, CA (BESS, GAP_PENDING_UNVERIFIED).** The county is
pursuing a permanent BESS zoning ordinance (draft amendment out for public
comment 2026-08-13 through 2026-09-27, per sandiegocounty.gov), not an urgency
moratorium. No pause on applications was found. Not added.

**Wichita, KS (GAP_ADOPTED_LIKELY).** This is a misattribution/duplicate, not
a gap. The City of Wichita's own official page (wichita.gov/1915/Data-Centers,
archived) documents only the Sedgwick County Board of County Commissioners'
interim development control (already the inventory's `ks-sedgwick-county-2026`
row) — there is no separate City of Wichita ordinance. The city page's own
timeline (extended to 2026-12-24 on 2026-09-02) matches the existing row's
`current_end_date_iso` of 2026-12-25 almost exactly. The servercountry.org
source behind the packet's "City of Wichita" claim appears to have conflated
the county action (administered jointly through the Wichita-Sedgwick County
Unified Zoning Code / MAPD) with a standalone city ordinance. No decision or
candidate added; the existing row is already accurate and current.

**Washington County, MN (GAP_ADOPTED).** This is very likely a
state-misattribution, not a Minnesota gap. The packet's assessment_url
(washingtoncounty.news, "County approves one-year moratorium," 2026-08-21)
reads as Minnesota but the article body names Chipley, Wausau, and Caryville
and "Florida Power & Light" — all Washington County, **Florida** places; a
`washingtoncountytimes.com` article with a similar headline turned up in the
same search and is likely the same Florida story under a different masthead.
Checking the real Washington County, MN directly: a Star Tribune article
(2026-06-23, archived) shows the county only "considered its regulatory
options" that week, with commissioners split (Clasen for a ban, Bigham
skeptical); the county's own official board minutes for 2026-08-04 and
agenda for 2026-08-25 (both fetched from washingtoncountymn.gov and archived)
contain no data-center item at all. savrn.com's own Minnesota tracker page
lists the Washington County claim without the "[Validation ...]" annotation
it adds to confirmed items (e.g., Waite Park), suggesting it was never
independently verified. Separately, Woodbury (a city within Washington
County, MN) has its own draft ordinance dated September 2026 headed
"Washington County, Minnesota" (apparently a template/boilerplate title,
not evidence of a county-level ordinance) tied to a Sept. 23, 2026 council
meeting; that is consistent with the existing `mn-woodbury-undated` inventory
row and was not treated as new evidence for the county. Not added.

**Surry County, VA (BESS, GAP_ADOPTED_UNVERIFIED_EXPIRED).** No primary
source for a Surry County, **Virginia** BESS moratorium was found. Searches
for "Surry County battery storage moratorium" are dominated by Surry County,
**North Carolina**'s real, separate, data-center (not battery-storage)
moratorium (already correctly in the inventory as `nc-surry-county-2026`).
Virginia's Surry County did adopt a permanent BESS zoning ordinance amendment
in 2025 (unanimous, 2025-04-03, allowing BESS as an accessory/conditional use
in Agricultural-Rural, M-1 and M-2 districts), which implies a moratorium or
review period preceded it, but no dated moratorium resolution/ordinance text
could be located to support a row. The carina_bess tracker's claim itself is
nearly contentless (`"claim": "EXPIRED MORATORIUM UTILITY_SCALE expires "`,
no date). Treated as unverifiable / likely conflated with the North Carolina
county of the same name. Not added.

## Flagged for the coordinator's judgment (added as candidates, but see notes field on each)

- **Asbury Park, NJ** — added, but it was enacted by a City Council
  *resolution* (2026-264, unanimous, 2026-06-10) rather than a zoning/interim
  ordinance under enabling state law, unlike the inventory's other NJ rows
  (Galloway Township, Mullica Township, Sayreville). It is **not** a permanent
  ban (the Pinelands-Alliance-list pattern the coordinator flagged as a risk
  for NJ items does not apply here — this was the only NJ item in the
  packet, and it genuinely pauses local data-center applications/site plans,
  not merely a request to the state). Confidence set to 0.55 and the
  `notes` field asks the coordinator to confirm a resolution-based local
  pause is in scope.
- **San Juan Capistrano, CA (BESS)** — weakest-evidence candidate in the
  packet. The city's own BESS overview page and DocumentCenter ordinance PDFs
  (Ordinance Nos. 1116/1119/1124) returned 404s when fetched directly during
  this pass (the page may have been taken down or reorganized). Only
  secondary confirmation (carina.energy, updated September 2026, describing
  the moratorium as "reclassified as active" after "data verification") was
  archivable. Confidence set to 0.45; flagged for direct verification with
  the city if added.
- **Covina, CA (BESS)** — the original Ordinance 25-01 adoption date and the
  City Council's final second-reading date for the replacement Ordinance
  25-10 were not confirmed to the day (escribemeetings.com portal did not
  return a dated copy of the original ordinance). Confidence set to 0.55;
  the sequence of events (moratorium -> extension -> repeal-and-replace with
  permanent zoning) is solid, but exact dates should be double-checked if a
  precise timeline matters.

## Notable findings beyond the packet (Process B discovery)

Two additional California moratoria were discovered while researching packet
items and added as bonus candidates (both fully archived with primary
sources):

- **City of Angels (Angels Camp), Calaveras County, CA** — Ordinance 559,
  adopted 5-0 on 2026-08-18, a *separate* 45-day data-center moratorium from
  the county's own action (the packet's Calaveras County item). A follow-up
  staff report recommended extending it to 2027-08-17 at a 2026-09-15
  hearing; whether that extension actually passed was not confirmed.
- **Arcata, Humboldt County, CA** — Ordinance No. 1594, adopted 5-0 on
  2026-09-16, a 45-day data-center moratorium, distinct from Humboldt
  County's own (still-unadopted, `pending`) county-level moratorium
  directive from 2026-07-15.

Also note the packet's Sedgwick County, KS item correctly flagged a sector
gap: the county has **three** separate, currently active interim development
controls — data centers (already in the inventory as
`ks-sedgwick-county-2026`), battery storage (Resolution 049-2026, adopted
2026-03-11, new candidate), and solar (Resolution 120-2026, adopted
2026-06-17, new candidate) — each a distinct resolution with its own vote and
end date, not one moratorium covering all three sectors.

## Confidence summary

- High confidence (0.8-0.9), primary source or strong corroborating news:
  Calaveras County, Escondido, Eureka, Gilroy, Lake Elsinore, Mendocino
  County, Morgan Hill, Tulare County, City of Angels, Arcata, Sedgwick County
  (BESS and solar), Topeka, Harrison County, St. Joseph MN, Rio Communities,
  Orange County (BESS), Solano County (BESS), Vacaville (BESS), Greenup
  County, Henderson County, Allen County (BESS), Morro Bay (BESS).
- Moderate confidence (0.5-0.75): Humboldt County (pending), San Francisco
  (pending), Grant County (pending), Suffolk (pending), Pine County, Covina
  (BESS), Allen County KS.
- Lower confidence, flagged explicitly for follow-up: San Juan Capistrano
  (BESS, 0.45), Asbury Park (resolution-based, 0.55).

## Sources archived

All evidence URLs cited in `gaps-2.json` are archived under
`work/sources/{CA,KS,KY,MN,NM,VA}/` and recorded in each state's
`manifest.jsonl`. `scripts/check_evidence_archived.py work/answers/qa3-gaps/gaps-2.json`
reports 51 distinct URLs cited, 0 not archived.
`python3 scripts/apply_research.py --answers work/answers/qa3-gaps/gaps-2.json --dry-run`
reports 31 candidates added, 0 rows touched, no conflicts.
