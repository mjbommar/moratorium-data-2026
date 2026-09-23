# QA round 3 gaps, packet gaps-1b (NY, 48 items) — notes

`work/answers/qa3-gaps/gaps-1b.json` carries 37 `new_candidates`. The 11 packet
items below produced no row (either the packet's `state`/`jurisdiction`
column referred to a different place entirely, or 2-3 targeted searches
turned up no primary or reputable secondary source for a BESS/solar/wind
moratorium). `decisions` is empty per the process doc.

## Not added

- **Jay** (Essex County) — No adopted local law found despite four searches
  (jaynews.org, townofjayny.gov's own local-laws listing, Essex County
  filings, a Ticonderoga staff report referencing consultant work "recommended
  to the Town of Jay"). A May-2026 Adirondack Explorer roundup of 50
  Adirondack towns explicitly lists **"Jay (In discussion)"** — distinct from
  the "(moratorium)" tag it gives towns that have actually adopted one. Treated
  as unverifiable/likely-not-yet-adopted rather than added at low confidence.

- **Maine** (Broome County) — No BESS/solar/wind moratorium local law or news
  coverage located in three searches; only a February 2024 dispute over an
  unrelated proposed corporate park (Broome County IDA v. Town of Maine) and
  generic tracker listings. Unverifiable.

- **Palatine** (Montgomery County) — Only the tracker's own claim (repeated
  verbatim on a second Carina Energy page) was found; no independent primary
  or news source after three searches, including direct site searches.
  Unverifiable — note the neighboring, similarly-named "Town of Montgomery"
  (a different town, in Orange County) has real, unrelated BESS coverage that
  search engines kept surfacing instead.

- **Parishville** (St. Lawrence County) — A Facebook post references a Local
  Law 02-2026 hearing titled "SOLAR..." but the post itself is login-walled
  and could not be archived; no other primary source or news coverage of a
  BESS-specific moratorium was found in two further searches. Unverifiable.

- **Penfield** (Monroe County) — The only Penfield renewable-energy law
  located (ecode360, Chapter 250, Article XVI) is a **permanent** zoning
  ordinance ("Renewable Energy Systems Regulations"), not a temporary
  moratorium. No separate temporary BESS moratorium was found. Rejected as a
  permanent zoning rule, not a moratorium.

- **Pike** (Wyoming County) — No moratorium found; search results returned
  only a "Pike Solar I LLC" project inducement resolution (a specific solar
  farm's tax-incentive filing, not a town-wide pause) and unrelated Town of
  Clay material. Unverifiable.

- **Poland** (Chautauqua County) — Search results kept returning coverage of
  the separate Town of Dunkirk's (also Chautauqua County) BESS moratorium
  instead. Actual Poland coverage found was limited to a 2025 community-solar
  project announcement with tax incentives, no moratorium mentioned.
  Unverifiable.

- **Root** (Montgomery County) — Only a stale February 2022 Daily Gazette
  article about a **solar-only** moratorism ("Towns of Root, Canajoharie
  issue solar moratoriums") was found; no evidence of a current (2024-2026)
  BESS-specific instrument despite a second, dated search. Unverifiable as a
  currently active BESS row.

- **Sherman** (Chautauqua County) — No moratorium local law or news coverage
  located in three searches; results returned only the unrelated Town of
  Sherman, Wisconsin and generic Chautauqua-County-wide tracker text.
  Unverifiable.

- **Town of Carlisle** (Schoharie County) — A primary instrument was found
  for a *solar* moratorium (Local Law 1-2024, referenced in an ORES filing
  as the "Carlisle Solar Moratorium"), but no primary source for a
  BESS-specific moratorium; the only support for a BESS moratorium is a
  battery-installer marketing site (backwell.com) that appears to restate
  the same Carina Energy tracker claim rather than an independent source.
  Not added for lack of independent corroboration.

- **Town of Brookhaven** (Suffolk County) — Duplicate/misattribution. The
  inventory already has `ny-town-of-brookhaven-2026` (Chapter 17, Article I,
  "Data Centers," adopted 2026-07-16, 18 months) — a data-center-only
  moratorium. Searches for a separate Brookhaven BESS moratorium found only a
  non-binding "Council District 1 BESS Task Force" (a discussion body, not an
  enacted law) and a resident Facebook comment stating "Brookhaven Town has
  not implemented a moratorium on lithium battery storage units." The
  packet's eticaag_bess claim (dateless "Active Moratorium") is treated as a
  likely mismatch against the existing data-center row rather than a real,
  separate BESS instrument.

## Sector-gap items resolved as genuine new candidates (not duplicates)

Several packet items flagged the inventory already having a row for the same
jurisdiction under a different sector. In each case the underlying instrument
is a distinct, separately-numbered local law, not the same law mislabeled —
confirmed against the exact existing CSV values via `show_rows.py --id`:

- **Perth** — existing `ny-perth-2026` is a 2026-06-04 **data-center**
  moratorium; the new candidate here is a separate solar/battery/wind
  moratorium chain (Local Law 23-2024, extended by LL#3-2025 and a third
  2025 extension).
- **Lysander** — existing `ny-lysander-2026` is a 2026-05-07 **data-storage**
  moratorium (LL 4-2026); the new candidate is the Town's long-running,
  separately-numbered **Tier 2 BESS** moratorium (originally LL 8-2023,
  extended through LL 6-2026).
- **Town of Clifton Park** — existing `ny-town-of-clifton-park-2026` is a
  2026-07-07 **Data Storage Center** moratorium (LL 9-2026); the new
  candidate is an earlier, distinct **BESS-specific** moratorium (LL 5-2025,
  2025-07-21 to 2026-01-21) that was itself superseded by a permanent BESS
  ban (LL 3-2026, adopted 2026-01-20) before the data-center law existed —
  recorded with `enacted_status: replaced`.
- **Town of Sherburne** and **Town of Watson** and **Town of Day** were not
  sector-gap flags but are genuinely new (not-yet-in-inventory)
  jurisdictions.

## Other outcome notes

- **Putnam Valley**: the packet's carina_bess tracker claimed
  "ACTIVE MORATORIUM ... expires 6/30/2026," but primary Town Board minutes
  and two independent news accounts show the moratorium instead **expired
  2025-10-24** and the Town Board explicitly determined it could not extend
  it further, pivoting to drafting new zoning. Recorded with
  `enacted_status: expired`, contradicting the tracker.
- **Town of Watson**: recorded with `enacted_status: replaced` — Lewis
  County's own project timeline shows the Town adopted permanent CAES zoning
  regulations on 2025-11-12, which appears to supersede at least the
  Compressed-Air-Energy-Storage portion of the six-month moratorium (whether
  the moratorium's separate Tier-2-BESS provisions were also formally
  replaced, or simply lapsed, is unresolved).
- A handful of candidates (Norfolk, Leyden, Stockport, Root, Rose, Carlisle
  excluded above) carry confidence in the 0.45-0.55 range because only a
  single weak primary source (a proposal/hearing notice rather than a
  confirmed adoption, or a document that could not be archived as text) was
  located; flagged individually in each candidate's own `notes` field.
