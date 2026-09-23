# Notes on gaps-1a.json (New York, 48-item packet)

Packet: `work/packets/qa3/gaps-1a.json`. New York had zero rows in the
inventory before this pass. Confirmed absence with
`python3 scripts/show_rows.py --state NY --list` (empty) before starting.

## Summary

- 48 packet items; 47 produced at least one `new_candidates` row (50 rows
  total -- Byron, Islip, and Concord each split into two rows because they
  turned out to be two separate local laws adopted by the same board, per
  the codebook's "several instruments adopted at once are separate rows"
  rule).
- 1 item rejected outright: **Duanesburg** (see below).
- 1 item recorded as **expired**, contradicting its tracker claim:
  **Angelica** (see below).
- 2 items recorded as **replaced** by a permanent ban rather than an
  ongoing moratorium: **Carmel** and **Gloversville** (see below).
- Confidence ranges from 0.85 (primary ordinance/minutes in hand, dates
  cross-checked) down to 0.45 (tracker-only corroboration, no dedicated
  primary or news source located within the research budget). Nothing
  below 0.4 was included.

## Rejected: Duanesburg (not added as a candidate)

Carina Energy lists Duanesburg, Schenectady County as an "ACTIVE,
indefinite" BESS moratorium. A Daily Gazette headline instead reads
"Duanesburg bans battery-energy storage systems," describing "a trio of
laws this month prohibiting the construction of commercial-scale
battery-energy storage systems in town" -- i.e., a **permanent** zoning
prohibition, not a temporary pause. The codebook explicitly excludes "a
permanent prohibition or zoning ban (not a pause)" from the inventory. I
could not confirm within the research budget whether an earlier, genuinely
temporary moratorium preceded this permanent ban (the way Carmel's and
Gloversville's permanent bans were each preceded by a documented six-month
moratorium, which *are* recorded below as `replaced`). Given the ambiguity,
I left Duanesburg out entirely rather than guess at an original moratorium
that may not exist. A follow-up pass should pull the actual Duanesburg
local-law text to check for a preceding temporary instrument.

## Corrected against its tracker claim: Angelica

The packet's assessment (based on Carina/EticaAG) says "ACTIVE MORATORIUM
UTILITY_SCALE expires 9/30/2026." An Allegany Hope Community News FOIL
investigation (archived) instead shows the Town of Angelica's BESS/solar/
wind moratorium was filed with the NYS Department of State on 2024-10-31,
extended twice by a Town Board *motion* (not resolution) on 2025-02-10 for
the two additional six-month periods the original law allowed, and expired
2026-04-30 without further extension or permanent regulation. A public
hearing on a **new, separate, permanent** "Local Law No. 1 of 2026...
Creating Regulations for Battery Energy Storage Systems" (not a
moratorium) was noticed for 2026-08-24. Recorded as `enacted_status:
expired` with the original 2024-10-31 date, not as an active 2026 row.

## Replaced by a permanent ban rather than ongoing: Carmel, Gloversville

Both towns are listed "ACTIVE" by Carina Energy, but in both cases the
underlying six-month temporary moratorium was superseded by a **permanent**
zoning law (Carmel: Tier-2 BESS ban, reported 2024-10-30; Gloversville:
outright ban on industrial solar and BESS, Common Council vote). Per the
codebook, a permanent ban is not itself a row-worthy moratorium. Recorded
each as the original temporary instrument with `enacted_status: replaced`,
rather than as an ongoing active moratorium (which is what a literal
reading of the tracker's "ACTIVE" status would suggest).

## Lower-confidence rows (tracker-only, no dedicated source found)

For these packet items, a Carina Energy live-tracker line (archived as
`https://carina.energy/bess-moratoriums/new-york/`) was the only evidence
located within the research budget, despite at least one targeted search
each: **Campbell, Collins, Corning, Essex County (county-wide instrument,
as distinct from the Town of Ticonderoga's own BESS moratorium, which *is*
well-sourced), Freedom, Gainesville, Glen Cove, Greenwood, Halfmoon,
Allen**. Confidence 0.45-0.55. A longer pass should try each town's own
.gov site and the relevant county Planning Board/Commission for primary
filings (as worked well for Lewis County, Suffolk County, and Erie County
towns in this same pass).

Two further items (**Amsterdam**, **Chester**) have real news/legal-notice
evidence establishing they exist, but the underlying pages were paywalled
(Amsterdam, Daily Gazette) or 404 on direct fetch despite appearing in
search snippets (Chester's chester-ny.gov notice pages, apparently
restructured since being indexed) -- so only the archived page's headline
or a tracker line could be cited as quoted evidence, and confidence was
kept at 0.5-0.6 rather than the 0.8+ used for rows with full primary text
in hand.

## Ambiguous jurisdictions worth flagging

- **Aurora**: disambiguated as the Town of Aurora, Erie County (confirmed
  via a December 22, 2025 Town Board minutes PDF matching Carina's
  2026-06-09 expiration exactly), not the separate Village of East Aurora,
  which independently passed its own energy-storage moratorium in 2024 and
  is a different jurisdiction.
- **Allen**: Allegany County has several similarly-named towns with their
  own separate BESS moratoria (Allegany, Alfred, Friendship, Angelica,
  Wellsville). No source specific to the Town of Allen itself was
  confirmed; flagged in the candidate's notes for a sanity check before
  relying on it.
- **Dunkirk**: recorded as the Town of Dunkirk (matches Carina's "Dunkirk,
  Chautauqua County"), not the separate City of Dunkirk, whose Common
  Council apparently considered its own six-month moratorium per an
  unverified Facebook post -- not included.
- **LeRay**: not to be confused with Carina's separate, older, EXPIRED
  LeRay BESS moratorium (Jefferson County) -- a different, unrelated
  instrument from the data-center moratorium recorded here.

## Two-search, no-instrument items

None -- every packet item either produced a candidate row (weak or strong)
or was affirmatively rejected/corrected as described above.
