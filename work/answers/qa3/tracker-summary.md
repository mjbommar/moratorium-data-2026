# QA1: cross-check against independent trackers (as of 2026-09-23)

Auditor: Claude Opus 5.5, QA1 tracker cross-check. Detail files:
- `work/answers/qa1/tracker-gaps.json` lists 439 tracker jurisdiction groups we lack, each with a verdict.
- `work/answers/qa1/tracker-extras.json` lists 272 inventory rows that no tracker lists, plus 281 contradictions sorted by priority.

## Method

- **Parsing.** I parsed every tracker that publishes a jurisdiction-level list into one table (3,381 entries).
- **Matching.** Each entry was matched to the inventory by state and normalized name. The normalizer strips City/Town/Village/Borough/Charter Township/County qualifiers and parentheticals, with a fuzzy fallback for consolidated names such as Augusta-Richmond, Nashville-Davidson and Lexington-Fayette. Matches are sector-aware: a BESS tracker entry does not count as matched by a data-center-only row.
- **Absence check.** For every unmatched group I confirmed absence with `scripts/show_rows.py --state XX --list`.
- **Verification search.** I ran one web search (`bc-web search --fuse`) for each data-center gap and for 14 BESS/renewable spot checks. A second search was used for 16 ambiguous cases.
- **Archiving.** New tracker pages are archived under `work/sources/US/`; the rest were already archived.

**Excluded as non-independent: gridcensus.com/dc-moratoria.** It republishes this dataset ("Source: Bommar, *Moratorium Nation*, as of 2026-09-17").

**savrn and aigridwatch are one source family.** Their entry text is verbatim-identical for most rows, so agreement between them is not two confirmations.

**Circularity with OCJ.** 61 research candidates in the 2026-09-23 pass cited the OCJ map as evidence.

## Per-tracker results

"Matched" counts tracker entries that match an inventory row. "Unmatched mor." counts the tracker's adopted or proposed moratorium entries with no inventory row, before verification. The next column shows how those unmatched groups came out after verification. "We have, it lacks" counts our in-scope rows that the tracker does not list; scope is data_center/general rows for the DC trackers, OH-only for OCJ, NC-only for the NC sheet, and battery/solar/wind rows for the BESS and renewable trackers.

| Tracker | Entries (local) | Adopted/proposed moratoria | Matched to our rows | Unmatched mor. | Real after verification (confirmed + likely + pending) | We have, it lacks |
|---|---|---|---|---|---|---|
| savrn.com (all 51 state pages in one national page) | 1,041 | 824 | 721 entries → 650 rows | 144 | 44 + 6 + 28 (50 ban/out of scope, 6 failed, 5 misattributed, 3 uncertain) | 355 of 1,005 |
| aigridwatch.com (`/data/moratoriums.json`) | 830 | 720 | 594 → 600 rows | 147 | 43 + 10 + 24 (62 out of scope, mostly NJ Pinelands bans) | 405 of 1,005 |
| interconnectedcapital.com (dashboard.html, updated 2026-09-14) | 428 | 365 | 321 → 318 rows | 51 | 15 + 2 + 10 (16 out of scope, 5 failed, 2 misattributed) | 687 of 1,005 |
| Ohio Capital Journal map, 2026-09-18 (Flourish data) | 195 | 149 | 151 → 142 rows | 10 | 0. Nine are Butler or Fayette County townships covered by our county rows; 1 uncertain (Wayne Twp) | 16 of 158 OH rows |
| NC Data Center Newsletter sheet | 55 | 50 | 53 → 52 rows | 0 | 0 | 13 of 65 NC rows |
| dcmap.us (34 notable local actions) | 28 | 21 | 26 → 25 rows | 0 | 0 | n/a (curated) |
| Carina Energy BESS map | 174 | 165 | 8 | 158 | 5 confirmed + 3 likely; 92 active and 46 expired unverified listings, 11 pending | 102 of 110 BESS rows |
| EticaAG BESS database | 73 | 52 | 2 | 50 | 4 + 1; 24 active and 13 expired unverified | 108 of 110 |
| CleanPowerDaily (solar/wind/BESS) | 62 (with locality) | 54 | 13 | 42 | 10 confirmed; 17 proposals (pending, unverified); 3 are covered by our multi-sector rows | all 112 non-DC rows (its entries match only our DC rows) |

Trackers I found but could not use at the jurisdiction level:
- Data Center Watch has project-level reports only.
- Programs.com, GatherGov/AI-for-CRE and ElectricChoice publish aggregate counts only.
- datacenterbans.com is state-level only.
- suedatacenters.org is a curated subset.
- datacentertracker.org renders its table with JavaScript and came back empty.
- Pinelands Alliance is the NJ ban list that feeds the savrn/aigridwatch NJ entries.

## Gaps: what the trackers have that we lack (439 groups)

| Verdict | Count |
|---|---|
| GAP_ADOPTED (one search confirmed an adopted temporary pause) | 65 |
| GAP_ADOPTED_LIKELY | 13 |
| GAP_PENDING (formally proposed, first reading, or directed to draft) | 33 |
| UNCERTAIN | 8 |
| BESS/renewable listings not individually searched: active / expired / pending | 103 / 52 / 32 |
| NOT_GAP_MISATTRIBUTED (tracker used the wrong state, or split one of our aggregate rows) | 19 |
| NOT_GAP_FAILED | 10 |
| NOT_GAP_OUT_OF_SCOPE (bans, zoning rules, nonbinding resolutions; includes 28 NJ Pinelands-ban groups) | 104 |

### Data-center gaps confirmed by search (about 63 confirmed or likely)

**Adopted in August or September 2026 (~29).** These fall in the window the 2026-09-23 pass was meant to cover:
- **California (9 urgency ordinances):** Calaveras Co, Escondido, Eureka, Gilroy, Lake Elsinore, Mendocino Co, Morgan Hill (DC+BESS), San Joaquin Co, Tulare Co.
- **Florida:** Levy Co, Ormond Beach, Putnam Co.
- **Midwest and Northeast:** Agawam MA; Ridgely MD; Oak Grove, Pacific and Palmyra MO; Rio Communities NM.
- **New York:** Islip (18-month), Le Ray, Mohawk, Orangetown (DC+BESS).
- **South and West:** Jasper Co SC (third reading ~9/21); Lavon TX; Port Angeles and Lincoln Co WA (DC+BESS).
- **Wisconsin:** Polk Co, Sawyer Co.
- **Indiana:** Howard Co.

**Adopted before August 2026 (~34).** These are genuine older misses that the trackers carry:
- **Nebraska county wave (8):** Box Butte, Custer, Dundy, Furnas, Harlan, Hayes, Johnson and Kearney counties. Nebraska Public Media lists 11 NE counties with moratoria; we have only Butler, Otoe and Seward from that list. Also Broken Bow (7/14).
- Phillips Co CO (Res. 2026-02-27-01).
- Holmes Co FL (6/16).
- Heard Co GA.
- Buchanan Co IA.
- Henry Co IL (June).
- Clark Co IN.
- Topeka KS (7/14).
- Greenup Co KY.
- Marengo Twp MI (Ord. 2026-1).
- Pine Co MN.
- Washington Co MN.
- Canton NY (7/8).
- Ironton OH (Ord. 26-01).
- Moore Co TN.
- Paris TN.
- Milford UT (Ord. 4-2026).
- Beetown WI.
- Middleton WI (7/1).
- Likely:
  - Wichita city (distinct from Sedgwick County).
  - St. Joseph MN.
  - Hampden WI.
  - Collier Co FL (zoning-in-progress pause).
  - Hays Co TX (180-day resolution pause).
  - Olyphant PA (curative-amendment six-month pause).
  - Asbury Park NJ (resolution pausing applications).
  - Franklin Co MO (lifted March 2026).

**Pending proposals we lack (33).** Examples:
- San Francisco (45-day, introduced).
- Humboldt Co.
- Alachua FL; Martin, Orange, Hillsborough and Hendry Co FL.
- Northampton, Plymouth (Town Meeting 10/17) and Southbridge MA.
- Salisbury MD.
- Mount Pleasant SC.
- Brownsville TX.
- Tazewell Co IL. Its May resolution refusing data center petitions is itself a de facto pause, and a 9-month moratorium was recommended 9/9.
- Suffolk VA.
- Thurston Co WA.
- Town of Janesville WI.
- Grant Co NM (9/24 agenda).

### Tracker errors worth knowing about

1. **Misattributed states (5).** Each of these is a row we already have:
   - Lowndes Co "AL" is Lowndes Co GA.
   - Benton Co "AR" is Benton Co MO.
   - Madison Twp "MI" is Madison Twp, Lake Co OH.
   - Muhlenberg Twp "PA" is Muhlenberg Twp OH.
   - Bell Co "TX" is Bell Co KY. The Bell Co TX commissioners only tabled the idea.
2. **Split aggregates.** OCJ lists the Butler and Fayette County townships one by one; our county rows cover them.
3. **Proposals labeled adopted, or votes that failed:**
   - Clinton IA was rejected 5-2.
   - Raton NM was rejected 3-2 on 9/22.
   - Henderson NV was rejected.
   - Michigan City IN was tabled 9/15.
   - Lancaster Co NE was withdrawn.
   - Fayetteville NC's "120-day pause" was a pause on *considering* a moratorium.
   - Georgetown KY only backed Scott County's moratorium.
   - Brawley CA dropped its moratorium language on 6/2.
4. **NJ.** About 40 savrn/aigridwatch "Local moratorium" cards come from the Pinelands list of permanent bans. They are out of scope.

### BESS, solar and wind: the largest systematic gap

Carina and EticaAG together list about 170 BESS moratoria we do not have. About 110 are in New York (Southold, Oyster Bay, Hempstead, North Hempstead, Smithtown, Babylon, Huntington and many upstate towns), plus some in CA, WA, ME and MA. We have zero NY BESS rows.

A spot check of 10 of these listings (Southold, Oyster Bay, Ticonderoga, Byron, Hartwick, Iberville Parish, Sedgwick Co BESS, Grand Co CO solar/wind, Utica IL, Tippecanoe solar) found all 10 real and all 10 temporary.

The inventory's 90 battery_storage rows are therefore almost entirely data-center-linked, multi-sector instruments. Standalone BESS and renewable moratoria were not swept. That fact belongs in `docs/known-gaps.md`; the other option is to redefine the scope.

Sector gaps on jurisdictions we already have:
- Sedgwick Co KS: BESS moratorium through 2027-05 and a solar pause.
- Grand Co CO: solar and wind to June 2027.
- Phillips Co CO: wind, solar and BESS extensions.
- Custer Co NE: 12-month BESS moratorium.
- Henderson Co KY: wind.

## Extras: what we have that no tracker lists (272 rows)

- **Coverage by trackers.** 781 of 1,053 rows (74%) are listed by at least one tracker. The remaining 272 split as follows:
  - 41 are non-data-center rows that only the BESS or renewable trackers could have listed.
  - 231 are data-center rows. By status: 159 active, 35 pending, 20 extended, 13 replaced, 2 expired, 2 rescinded.
- **Where the unlisted data-center rows came from.** 161 of the 231 were added on 2026-09-23. 87 of those carry pre-August dates.
- **By state.** Michigan dominates the unlisted rows (59), then IA 32, GA 22, TN 14, WA 14, OH 11, CO 10 and NC 10.
- **Weak evidence.** 68 of the 231 have `[VERIFY]` tags. These are the rows to scrutinize first.

Contradictions (full list in `tracker-extras.json`):
- **High priority: 32 findings on 20 rows.** Examples:
  - fl-leon-county-undated: three trackers say it was adopted unanimously on 7/14; we say pending.
  - tn-hamblen-county-undated: trackers say adopted, running through 2027-07-07; we say pending.
  - nd-mercer-county-2026: lifted in June; we say active.
  - ga-kingsland-camden-county-2026: expired 8/9; we say active.
  - mi-caledonia-township and mi-saugatuck-township: trackers say expired; we say extended.
  - ca-calipatria-undated: a permanent ban. Candidate REMOVE.
  - Permanent bans that trackers characterize as such but we record as active pauses: nc-clay-county, nc-clyde, nc-eastern-band-of-cherokee, tn-hawkins-county, tn-white-county, the Fallon Paiute-Shoshone and Pyramid Lake Paiute tribal bans, oh-monroe-township-adams, oh-paris-township-union, oh-liberty-township-wood, and oh-urbana (a zoning removal on 6/16 may have superseded it).
- **Medium priority: 28.**
  - Trackers still describe these as proposals while we record adoption on or before the tracker's own date: az-pima-county, md-talbot-county, oh-plain-city, nc-hendersonville, fl-palm-beach-county, fl-hernando-county, al-helena, ut-iron-county, ny-clay.
  - Every tracker family that lists these rows gives a different adoption date from ours, usually a later month: GA Athens-Clarke, Rockdale, Coweta, Lagrange and Lamar; mn-minneapolis (trackers 5/21-22, ours 6/25); oh-vienna-township (Aug, ours 2/17); ny-north-tonawanda (2026-06, ours 2024-07); and others.
- **Low priority: 221.** These are mostly single-family date differences where the tracker is dating an extension or a later vote.

## Overall judgment

1. **Our inventory is the most complete public list of data-center moratoria, but it is not complete.**
   - Against savrn, the largest independent list, we match 650 of its rows. About 78 of its unmatched moratorium entries prove real on checking (44 adopted, 6 likely, 28 pending).
   - Unioned across all data-center trackers, verification finds about 63 adopted or likely-adopted data-center pauses and 33 formal proposals missing. That is roughly a 6-7% shortfall against our ~1,000 data-center rows, and about half of it is in August-September 2026.
   - California urgency ordinances (9) and the Nebraska county wave (8 counties plus Broken Bow) are the two clusters the 2026-09-23 pass clearly missed.
   - Outside data centers the shortfall is much larger. Standalone BESS, solar and wind moratoria are under-covered by an order of magnitude, about 150 or more missing, mostly in New York.
2. **The pre-August 2026 rows look mostly like genuine misses, not artifacts.**
   - Of the 282 rows added on 9/23 with pre-August dates, 176 (62%) appear in at least one tracker.
   - For 156 of those 176, the tracker also dates the adoption before August. Only 6 have a tracker date after July, and those are extension dates (Rochester Hills, Franklin Co GA, Rowan Co KY, Upper Sandusky OH, Clinton Twp PA, Lyon Co KY).
   - For comparison, 84% of pre-existing rows are tracker-listed.
   - The trackers independently carry about 34 more pre-August data-center pauses that we still lack. That supports the reading that earlier coverage was genuinely incomplete, not that the new rows were back-dated.
   - Caveat: most of that corroboration comes from the savrn/aigridwatch family and the OCJ map, and OCJ was itself a source for 61 candidates.
3. **The 106 pre-August new rows that no tracker lists need the closest QA scrutiny.** 41 are in Michigan, 12 in Iowa and 10 in Georgia. Most are small townships. Absence from trackers is not evidence they are wrong, since trackers also miss small townships, but these rows have no outside corroboration at all.
4. **Also act on:**
   - The two pending-but-adopted rows (Leon Co FL, Hamblen Co TN).
   - The permanent-ban rows listed above, which fall outside the codebook scope.
   - Mercer Co ND, which was lifted.
