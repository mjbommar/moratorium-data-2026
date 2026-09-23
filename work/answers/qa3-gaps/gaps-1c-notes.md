# QA round 3 gaps packet 1c (NY) — research notes

Packet: `work/packets/qa3/gaps-1c.json`, 47 New York jurisdictions (mostly town/village
BESS and solar moratoria adopted as local laws, plus a few data-center/general items),
almost all sourced from the Carina Energy BESS Moratorium Monitor
(`carina.energy/bess-moratoriums/new-york/`) or the eticaag.com BESS restrictions
database. `python3 scripts/show_rows.py --state NY --list` confirmed none of the 47
jurisdictions already has a row in the inventory, so every finding below is a
`new_candidates` entry or a rejection, never a `decisions` update.

40 candidates were added to `gaps-1c.json`. 7 items were **not added**; reasons below.

## Not added

- **Fort Ann (Washington County)** — Local Law No. 2 of 2026, fetched and read in
  full, is titled "A LOCAL LAW PROHIBITING COMMERCIAL BATTERY ENERGY STORAGE
  SYSTEMS" and is a permanent ban with no term or sunset clause, not a temporary
  moratorium. Per the process doc's rule on permanent bans, this is not recorded as
  a new moratorium row. (An Adirondack Almanack roundup loosely tagged Fort Ann as
  having a "moratorium," but the only primary instrument found is the permanent
  ban.)
- **Riverhead (Suffolk County)** — A three-month BESS moratorium was proposed
  (public hearing October 2023, backed by the Suffolk County Planning Commission),
  but the Town Board never held the vote: a member was absent at the scheduled
  November 21, 2024 meeting, and Supervisor Tim Hubbard announced on January 5,
  2024 that the moratorium "is no longer necessary" and would not be acted on,
  given incoming state BESS fire-safety guidance. This is a failed/abandoned
  proposal, not an enacted instrument. (Source:
  riverheadlocal.com/2024/01/05/battery-energy-storage-moratorium-is-no-longer-necessary-hubbard-says/,
  read in full but not archived as evidence since nothing was added.)
- **Town of Ulster (Ulster County)** — No moratorium instrument was found. All
  coverage located concerns the Town Board's SEQRA/site-plan review of a specific
  proposed BESS project (Terra-Gen/Alcazar, 430 Hurley Ave.) and a request from the
  neighboring Town of Hurley that Ulster informally pause permitting on that one
  project — not a town-wide or generally applicable moratorium law. eticaag's
  "Proposed Moratorium" claim could not be corroborated.
- **Willing (Allegany County)** — The packet's own tracker claim is internally
  inconsistent ("EXPIRED MORATORIUM ALL_BESS expires " with a future date of
  6/1/2027), and no town-specific ordinance, agenda, or news coverage was found
  despite several searches (only county-level Allegany BESS context for other towns
  — Angelica, Friendship, Independence, Allegany — turned up). Treated as
  unverifiable.
- **Barker (Broome County)** — Searches repeatedly resolved to "Barker" the hamlet
  within the Town of Somerset, Niagara County (which does have a confirmed,
  separately-added moratorium, see candidate #29 Somerset), not the Town of Barker
  in Broome County that the tracker names. No Broome County primary source or news
  item was found. Treated as unverifiable/possible misattribution.
- **Florence (Oneida County)** — Only the Carina tracker entry and an unrelated 2022
  county communications document (with a fragmentary OCR mention of "Florence's")
  were found; no town ordinance, agenda, or news article located. Treated as
  unverifiable.
- **Naples (Ontario County)** — Only the Carina tracker entry ("under review") was
  found; no town-level source. Treated as unverifiable.

## Corrections to tracker claims (flagged in the candidate `current_status`/`notes` fields)

Several packet items carried tracker claims that current-dated primary or news
sources contradict; these are recorded as **active**, not expired/lifted, with an
explicit note in the candidate:

- **Busti (Chautauqua County)** — tracker said "EXPIRED 12/3/2024"; Post-Journal
  reporting from June 2025 and July 2026 shows the commercial-BESS moratorium was
  extended twice and is active through June 30, 2027 (Local Law 3 of 2026).
- **Town of Chautauqua** — tracker implied expiry ~9/3/2025 (from an earlier local
  law's term); Town notices and Post-Journal reporting show Local Laws 3-5 of 2026
  (public hearing July 8, 2026) extended the wind/BESS/commercial-solar moratoria
  further; still active as of 2026-09-23.
- **Elba (Genesee County)** — tracker said "LIFTED 10/31/2025"; a Town of Elba
  public-hearing notice shows a July 9, 2026 hearing to extend a 12-month
  moratorium on Tier 3 solar and large battery storage, implying it continued past
  the tracker's stated lift date. Recorded as active with reduced confidence (0.5)
  since only a notice-aggregator page was found, not the underlying town document.

## Other notable caveats baked into individual candidates

- **Johnstown (Fulton County)**: recorded as the Town of Johnstown (Town Board
  action), consistent with Carina's county-level listing; a separately-reported
  City of Johnstown ("Common Council") BESS moratorium exists and may be what some
  trackers actually intend — flagged in the candidate's notes for the coordinator.
- **German Flatts (Herkimer County)**: the only BESS-specific item found at the
  Herkimer County Planning Board's May 2025 review was a *permanent* BESS
  regulatory law, not a pause; the actual moratorium confirmed there covers solar
  and wind only. Recorded with `sectors: ["solar","wind"]` rather than
  `battery_storage`, contradicting the tracker's sector tag — flagged for
  coordinator review.
- **Turin (Lewis County)**: county land-use records separately list a "Town of
  Turin" battery-storage moratorium and a "Village of Turin" solar moratorium (the
  filing actually retrieved, dated June 2025, is the Village's). Recorded as Town
  per the county index wording, but this is uncertain.
- **Yorktown (Westchester County)**: has a complex history (2019 land-use
  moratorium; a separate permanent ban on new Tier 2 BESS adopted May 29, 2025).
  The tracker's claimed 2026-01-14 expiry does not clearly match either located
  instrument; recorded at reduced confidence (0.55) with both instruments
  documented in the notes.
- Several other candidates (Virgil, Carrollton, Ripley) rest on the Carina tracker
  alone — no independent primary/news source could be found despite repeated,
  variously-worded searches — and are recorded at confidence 0.45 with that
  limitation stated explicitly in `notes`.

## Process notes

- All 66 evidence URLs cited across the 40 candidates were archived with
  `scripts/save_source.py --state NY` (one dead link, a Times Hudson Valley legal
  notice for Montgomery that now 404s, was dropped from the evidence list rather
  than cited unarchived).
- `python3 scripts/apply_research.py --answers work/answers/qa3-gaps/gaps-1c.json --dry-run`
  reports 40 candidates added, 0 rows touched, 0 conflicts.
- `python3 scripts/check_evidence_archived.py work/answers/qa3-gaps/gaps-1c.json`
  reports 0 unarchived URLs.
