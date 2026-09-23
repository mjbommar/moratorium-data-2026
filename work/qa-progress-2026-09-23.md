# QA/QC rounds after the 2026-09-23 refresh

User's concern: 281 of the 520 new rows carry adoption dates before 2026-08-01. Are they genuine misses, duplicates, mis-dated, or out of scope?

## Deterministic checks (coordinator, before agents)
- Name/geo overlap of new vs pre-existing rows: 47 pairs reviewed; nearly all are city-vs-county or different townships. Real questions: Plain Township OH (existing row geocoded to Stark County; new row is Wood County; which one adopted in March 2026?), Lake Township (Stark) OH new row geocoded to the Wood County township.
- Evidence quotes vs archived text: 1,845 found, 52 missing (paywall stubs, ellipsis joins, obfuscated text), 117 evidence entries had no quote. Misses passed to Round 1 auditors via `quote_mismatch`.
- Reverse-geocode county check of 123 same-name/county-qualified rows: 26 mismatches (24 new, 2 pre-existing: Calhoun GA placed in Calhoun County instead of Gordon; Jackson Township (Franklin) OH placed in Clermont). Root cause: `geocode_inventory.py` stripped the parenthetical county before querying. Fixed to query county-qualified forms first; all 26 re-geocoded and re-checked, one (Howard Charter Township, Cass County MI) needed a manual override.
- Sibling tracker reconcile: only 3 leads (Wichita KS, Smithfield RI [permanent ban], Hampden WI).

## Round 1 — audit every new row (12 agents; Opus on OH x3, MI x2)
Packets `work/packets/qa1/`, procedure `work/qa-process.md`, answers `work/answers/qa1/`. REMOVE / DUPLICATE_OF verdicts are unresolvable-outcome notes the coordinator applies by hand.

## Round 2 — blind re-verification sample (running)
40 rows (26 new, 14 pre-existing) given to two agents as bare jurisdiction names; procedure `work/qa-blind-process.md`; outputs `work/answers/qa1/blind-*.json`; key in coordinator scratchpad.
## Round 3 — completeness vs external trackers (running)
Opus agent cross-checking savrn, interconnectedcapital, aigridwatch, OCJ map, NC sheet, cleanpowerdaily and others in both directions; outputs `work/answers/qa1/tracker-*.json`.
## Round 4 — label consistency and rebuild (planned)

### Round 1 results by packet
| Packet | Items | Confirmed | Corrected | Status chg | Remove/Dup | Unresolvable | Auditor's read on OLDER items |
|---|---|---|---|---|---|---|---|
| OH-part3 | 34 (12 older) | 30 | 3 | 0 | 0 | 1 | genuine misses; one date error (Waynesville, packet filename read as vote date); leads: Athens County Commissioners row missing, Fairborn earlier crypto ban |
| MI-part2 | 38 (23 older) | 27 | 11 (all end-date fills) | 0 | 0 | 0 | genuine misses; every date is the adoption vote; leads: Zeeland Charter Twp March instrument (replaced Sept 1) lacks a row. Packet-builder note: same-name rows got each other's evidence in the QA packet (matched by name); auditor re-verified from the original answer files. |
| NC | 30 (4 older) | 26 | 4 (VERIFY resolved, Whitakers date filled) | 0 | 0 | 0 | genuine misses (primary docs or the town's own paper); two quote_mismatch flags were false alarms (paywall banner, garbled PDF font) |
| OH-part2 | 36 (36 older) | 31 | 4 (end-date fills) | 0 | 0 | 1 (Washington Twp, Logan Co: map-only, Google Drive source needs sign-in; treat as REMOVE if unreadable) | genuine misses; agent had avoided the map's misleading dates in 5 cases. Leads: Perry Village now active (News-Herald 09-23); Richfield Twp coords point to Summit not Lucas; Paris Twp (Union) permanent ban 04-07 may make it replaced |
| OH-part1 | 36 (36 older) | 32 | 4 (3 end-date fills, 1 instrument number) | 0 | 0 | 0 | genuine misses; 28/36 on primary sources; three first-reading traps already avoided. Watch: Wood County trio (Freedom/Henry/Liberty) at 0.5 on one roundup; Carrollton/Barberton open-ended |
| MI-part1 | 39 (39 older) | 34 | 5 (Dorr exact date, Casco term, end dates) | 0 | 0 | 0 | genuine misses; every date traced to the adopting vote; if anything a few (Freedom, Chikaming, Bowne) start later than the pause did. Lead: Cascade Twp Res. 024-2026 may deserve its own row |

### Round 2 blind set A (20 rows: 13 new, 7 old)
18/20 agree on adoption month and status (16 exact dates, 2 one day apart: Newberry SC 06-05 vs 06-03, Pinson AL 08-06 vs 08-07). Disagreements: North Branch MN — verifier found the July 31 Chisago County Press adoption report our pass missed; corrected to active (coordinator-MN.json). Rittman OH — verifier found nothing, but our row rests on the city's own minutes and agenda (verifier false negative). No row was found to be a non-moratorium.
| NY IN ME SC NE CA MO | 51 (11 older) | 47 | 4 (evidence upgrades, Clay NY exact date, Grant County IN end date) | 0 | 0 | 0 | all OLDER items genuine misses; quote mismatches were formatting, one paywall gap covered by a second source |
| WA WI IL MN | 63 (19 older) | 58 | 4 | 1 (Mount Vernon WA 2025: expired -> extended, renewal missed) | 0 | 0 | genuine misses; pattern flagged: extension chains of older instruments sometimes garbled (Enumclaw, Mount Vernon 2025). Two evidence copy-paste errors found and replaced (Mount Vernon 2026, Blue Earth MN) |

### Round 2 blind set B (20 rows: 13 new, 7 old)
16/20 agree on adoption month and status; two more agree on status with the verifier unable to date the row. Real discrepancies, resolved against archived sources: Putnam County GA vote was 08-07 (row had the 08-18 effective date) -> corrected; West Chicago IL (pre-existing row) vote was 07-20 per the City's own release, not 07-06 -> corrected; Clinton Township PA: the local paper gives both April 8 and April 30 -> flagged as a range with VERIFY. Milliken CO and Norvell Township MI: our rows are better sourced than the verifier's (Municode index; OCR'd Resolution 2026-06); no change. Across both blind sets: 40 rows, 0 non-moratoria, 3 date corrections, 1 status correction in our favor, 0 phantom rows.
| AL CO FL KS MD | 55 (24 older) | 44 | 10 (6 end-date fills, Calvert ordinance no., VERIFY resolutions, Lake County FL date 09-09 -> 09-08) | 0 | 0 | 1 (Helena AL: sources conflict on instrument and date) | genuine misses; AL.com roundup dates matched local sources; Calera's "minutes" PDF was a blank agenda cover, confidence capped at 0.55 |
| 20 small states | 40 (17 older) | 37 | 0 | 0 | 2 REMOVE (Fallon Paiute-Shoshone, Pyramid Lake Paiute: permanent bans, not pauses) | 1 (Turner County SD: Aug 2026 extension hearing outcome not found) | all OLDER dates held against primary sources; two ROT47-paywall quote flags were false positives |
| TN KY PA | 52 (30 older) | 49 | 2 (Sparta TN 2026-06 -> 07-16, Butler County KY 2026-06 -> 07-13: first readings mistaken for adoption) | 1 (Sevierville TN pending -> active, third reading 08-17 found) | 0 | 0 | genuine misses; first-reading-as-adoption is the failure mode, seen in 2 of 30 |

### Round 4a — same-name township disambiguation (done)
25 township rows without a county qualifier whose name exists in several counties: all 25 resolved and renamed with "(X County)"; 10 had coordinates in the wrong county (3 pre-existing: Richfield Twp OH -> Lucas, Scioto Twp OH -> Pickaway, Warrington Twp PA -> York; 7 new) and now carry declared overrides. Combined with the 26 geocoder fixes earlier, 36 rows were mapped to the wrong county before this QA. Remaining unarchived evidence in these files is Nominatim/GitHub self-reference URLs, accepted.
| IA GA | 46 (29 older) | 38 | 7 (exact dates for Ball Ground, Madison Co; evidence swaps fixed for Emmet 2026 and the Palo Alto pair; Palo Alto crypto row lost a wrong data_center sector) | 1 (Louisa Co IA crypto pending -> active, 0.6) | 0 | 0 | genuine misses; risk is evidence-citation hygiene (two IA rows had the wrong instrument's evidence attached). Leads: Emmet County IA solar/BESS chain (Res. 25-36/26-13/26-28) not in inventory; Fairfax IA may be a no-sunset ban |

### Round 1 totals
All 520 new rows audited by 12 agents: 0 duplicates; 2 REMOVE (Nevada tribal permanent bans); 5 adoption-date corrections on the 281 pre-August rows (Waynesville OH, Dorr Twp MI precision, Sparta TN, Butler County KY, plus Lake County FL among newer rows); ~50 field corrections, mostly end-date fills and evidence fixes; 4 unresolvable. Every auditor independently concluded the pre-August rows are genuine misses of small jurisdictions, not a dating artifact. Specific failure mode found (rare): a first-reading news story mistaken for adoption (2 of ~280).

## Merge of Round 1 (done)
174 QA decisions applied (audit `work/audit/apply-20260923T100902.json`), 0 conflicts; 2 tribal permanent-ban rows removed (recorded in `work/answers/rejected/`); 11 geo overrides applied; inventory 1051 rows. Validator: 0 errors apart from stale stats (rebuild pending), 20 warnings.

## Round 4 — label consistency (running)
133 rows flagged deterministically: 67 sector-vs-text checks, 44 extended rows without an end date, 25 duration_days/text disagreements, 5 duplicate-name markers, 5 in-force rows past their term, 1 pending row with a date. Three agents (`work/packets/qa4/group*.json`, procedure `work/qa4-process.md`, answers `work/answers/qa4/`). A fourth agent chases the 14 leads raised by Rounds 1-3 (`work/packets/qa4/leads.json`).

## Round 3 — completeness vs external trackers (cross-check done; gap research running)
Nine trackers with usable lists (savrn 1,041 entries, aigridwatch 830, interconnectedcapital 428, OCJ Ohio map 195, NC newsletter sheet 55, dcmap 28, Carina 174 and EticaAG 73 for battery storage, CleanPowerDaily 62). Outputs `work/answers/qa3/tracker-{gaps,extras}.json`, `tracker-summary.md`.
- We are the largest list; savrn matches 650 of our rows and lacks 355 of them.
- Trackers name ~65 adopted data-center pauses and ~33 formal proposals we lack, plus ~150 unverified listings (mostly New York battery-storage/solar local laws; we had none for NY). All 278 non-battery-tracker-only gaps are now being researched by 7 agents (`work/packets/qa3/gaps-*.json`, procedure `work/qa3-gaps-process.md`).
- 32 high-priority contradictions (adopted vs pending; lifted vs in force; permanent bans recorded as pauses) assigned to an Opus reconciliation agent (`work/packets/qa4/contradictions.json`).
- On the user's question: 176 of the 282 pre-August new rows (62%) appear in at least one tracker, 156 with a pre-August date there too; trackers list ~34 further pre-August pauses we lacked. The 106 pre-August rows no tracker lists (41 MI, 12 IA, 10 GA) have only our own evidence; Round 1 audited all of them against archived primary sources.
- Caveats: savrn and aigridwatch share text (one source, not two); 61 of our Ohio rows cite the OCJ map, so its agreement is partly circular; gridcensus.com republishes this dataset.

### Interruption (10:10-10:20)
Seven of the twelve Round 3/4 agents died mid-task on an API spend-limit error; the account was switched and all seven were resumed with their context intact. One of the dead agents had left nine empty files with ROT47-decoded names in the repo root (an unquoted shell redirect); they were deleted.

### Round 3 contradictions (done)
32 high-priority tracker contradictions on 20 rows: we were right in 20 cases, trackers in 12. Net changes: 4 REMOVE as permanent bans (Calipatria CA: moratorium never adopted, live proposal is a ban; Clay County NC; Eastern Band of Cherokee, borderline; Hawkins County TN), Mercer County ND -> replaced (lifted ~2026-08-05), small text fixes (Kingsland GA legal_basis, Urbana OH outcome). Trackers' errors: WCTV headline misread (Leon County FL), unamended draft read (Kingsland), wrong-township matches (Liberty, Monroe OH), planning-commission recommendation read as adoption (Hamblen, Roane TN). White County TN kept at 0.5 as borderline. Caledonia Township MI coordinates were in Alcona County; override declared for Kent County.

### Round 3 gap research: packets 4 and 5 (done)
- gaps-4 (NE CO TX MI ME NC LA OH OR, 34 leads): 30 candidates, 4 rejected (Hall County NE was Hall County GA; Comstock Twp MI replaced 2025; Lee County NC approved incentives instead; Portland OR only urged). Lincolnton NC adopted 09-03 (tracker said delayed).
- gaps-5 (WA MA WI MO GA IA NH UT, 33 leads): 25 candidates, 8 rejected (two MA bylaws disapproved by the Attorney General; Thurston WA staff direction only; Klickitat replaced; Whatcom unverifiable; Franklin MO tabled; Columbia GA never voted; Keene NH discussion only).
- Tool fixes from these packets: `check_evidence_archived.py` now checks each citation against its own state's manifest (multi-state files falsely failed); `apply_research.py` accepts two-letter codes in candidate `state`, and its no-instrument-number dedup now compares sectors, so a battery-storage pause is not dropped as a duplicate of the same body's data-center pause (Renton WA, Skagit County WA, Westfield MA).
- gaps-4's notes flagged the session's genuine account-change notice as an injection; corrected in the notes file.
- gaps-3 (FL IN IL MD TN SC NV PA, 34 leads): 30 candidates (14 active, 9 pending, 5 expired, 2 replaced), 4 rejected (Collier FL administrative freeze; Hendry FL unconfirmed; Pulaski IN undatable; Olyphant PA curative-amendment stay). Holmes County FL's real ordinance is 2026-03, not the 2026-23 all trackers repeat.
- gaps-2 (CA KS KY MN NM VA NJ, 34 leads): 31 candidates (22 in force, 5 replaced, 4 pending), 6 rejected (San Joaquin CA still in study; Monterey/San Diego BESS on permanent-zoning tracks; Wichita = Sedgwick County action already tracked; "Washington County MN" was Washington County FL; Surry County VA unverifiable). The NJ Pinelands entries mostly fell out as permanent bans; Asbury Park kept as a resolution-based pause.

### Round 4 label consistency: group 3 (OH IA NY IN MA CO NE ME NM UT) done
44 flagged rows: 27 confirmed, 14 corrected (end dates filled on extended rows; duration_days reset to the ORIGINAL term for Dryden NY 548 and Sanford ME 91; sectors fixed for Adair IA +battery, Putnam IN +wind, Red Willow NE general->data_center), 1 status change (Seward County NE -> extended), 2 unresolvable (Mount Orab OH renewal, Washington Twp OH Sept 22 minutes). Most SECTOR_CHECK flags were context mentions, not scope.

### Round 4 label consistency: group 2 (GA NC CA IL KS AR KY LA MN TX) done
44 flagged rows: 26 corrected, 11 confirmed, 1 status change (South Fulton GA -> replaced by ORD2026-024 before its end date), 6 unresolvable (Cedartown, East Point, Hogansville, Lamar GA; Troy, Robinson IL). Systematic find: six NC rows (Kings Mountain, Mount Airy, Durham, Surry, Hillsborough) plus Baldwin Park CA, Harlingen TX and Milton GA stored the extended total in duration_days instead of the original term. Coweta County GA rows now distinguished by instrument in legal_basis.
- gaps-1c (NY, 47 leads from the Carina/EticaAG battery-storage trackers): 40 candidates (15 active, 12 replaced, 12 expired, 1 pending), 7 rejected (Fort Ann permanent ban; Riverhead never voted; Ulster SEQRA only; Willing, Barker, Florence, Naples unverifiable). Tracker staleness: Busti and Chautauqua listed expired but were extended.
- gaps-1a (NY, 48 leads): 50 candidates (Byron, Islip, Concord each two same-day local laws), Duanesburg rejected as a permanent ban; Angelica recorded expired (tracker said active); Carmel and Gloversville replaced by permanent bans.

### QA leads (14) done
Helena AL settled (Ord. 1043-2026 adopted 2026-06-22, 180 days); Turner County SD -> extended to 2027-08-25; Paris Twp (Union) OH -> replaced by 04-07 zoning ban; Washington Twp (Logan) OH REMOVE (no record beyond a map pin to a private Drive file); Cascade Charter Twp MI split into two rows; new rows for Fairborn OH 2022 crypto pause (expired), Zeeland Charter Twp MI Res. 1027 (rescinded 09-01), Emmet County IA solar/BESS chain (extended), Town of Hampden WI (Ord. 18). Not rows: Athens County OH (non-binding), Wichita KS (mis-cited notice). Still open: Perry Village OH (pending, re-check after 09-24), Bruce Twp MI (Cloudflare-blocked minutes), Fairfax IA (no-sunset question).
- gaps-1b (NY, 48 leads): 37 candidates, 11 rejected (Jay in discussion; Penfield permanent zoning; Brookhaven has no BESS pause; seven unverifiable or stale). Tracker wrong on Putnam Valley (expired 2025-10-24).

## Merge of Rounds 3 and 4 (done)
- Order: coordinator Zeeland fix, leads, contradictions, then label files (so the label pass's stale Cascade end date was refused by the conflict guard, as intended), then the 7 gap files.
- 243 gap candidates added (127 NY, 116 elsewhere); 116 carry an automatic VERIFY marker for news-only or low-confidence evidence. 5 more rows removed as permanent bans or never-adopted (Calipatria CA, Clay County NC, Eastern Band of Cherokee, Hawkins County TN, Washington Twp (Logan) OH), bringing the QA removals to 7.
- New dedup rule in apply_research: an ended candidate dated before an existing row is its predecessor, not a duplicate (Zeeland). Validator: same-name rows with distinct sector scopes or adoption dates are no longer flagged (all 15 such pairs were legitimate separate instruments).
- Inventory: 1,294 rows, 47 states. Validator 0 errors. Geocoding: all new rows resolved; reverse-geocode county check of new county rows found no misplacements.

## Round 5 (final accuracy pass, running)
Validator still flags 19 rows marked in force past their term (15 new NY battery-storage rows labelled from a tracker) and 35 non-pending rows with no adoption date (22 new NY). Two agents: `work/packets/qa5/{drift,dates}.json`, answers `work/answers/qa5/`.

## Round 5 results and final state (done)
- Past-term rows (19): 11 settled (Baldwin Park CA, Glenville, Oswego, Mayville NY extended; Appling GA, Newfane, Cairo NY expired; Leyden NY replaced; Waterford MI, Westfield NY, East Whiteland PA already correct), 8 unresolvable and marked [VERIFY].
- Missing dates (35): 12 dated, 3 removed as never adopted (Lansing NY withdrawn 2025-11; St. Charles Parish LA voted down 04-06; Lowell Twp MI failed 2-5), 20 unresolvable (16 are tracker-only New York battery-storage local laws with no findable filing), all marked [VERIFY].
- Correction to the premise: 5 of the 281 "pre-August" rows were month-only August dates ("2026-08" sorts before "2026-08-01"); the true count was 276.

## Final numbers
1,291 rows, 47 states; 897 active, 166 extended, 77 pending, 93 replaced, 50 expired, 8 rescinded; 300 rows with [VERIFY]. 14 rows removed during QA (reasons in `work/answers/rejected/`). About 640 QA field changes across 7 audit files. 37 rows re-geocoded. Validator: 0 errors; warnings are the 20 undatable rows and 11 status-drift rows described in docs/known-gaps.md. All 40 documented numbers match the data.

## Answer to the user's question
The pre-August rows are overwhelmingly genuine: 274 of 276 survived an adversarial audit (2 removed as permanent bans), 10 had their dates adjusted, and 62% also appear in at least one independent tracker with a pre-August date. The blind sample matched on 34 of 40. The earlier coverage missed them because the month-by-month sweep reached counties and cities but not townships and villages; the trackers themselves list more such rows we still lacked, which the QA then added.
