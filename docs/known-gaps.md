# Known gaps and limitations

We're confident in what's in this dataset, but here's an honest accounting of what we know we're missing.

## What we know we don't have

### Small-township records that aren't online

Many small townships and rural counties don't post agendas, minutes, or signed ordinances on the web. When we know a moratorium exists from news coverage but can't pull the underlying instrument, we record it with a `[VERIFY]` note in `verify_notes` rather than guessing at the ordinance number or exact date. **140 of the 323 inventory rows** have at least one such evidence-ceiling note (`has_verify_tags = True`), down from 123 of 222 in v2026.04.4 after a targeted verification pass.

### Records behind authentication or CAPTCHA gates

Some primary sources (notably the NC eCourts portal at `portal-nc.tylertech.cloud`, several Legistar instances, and certain Granicus-archived meetings) are protected by Akamai-style human-verification challenges that defeat automated retrieval. For affected entries, we use the best secondary source (county press releases, local news) and document the evidence ceiling.

### Uneven coverage of the May-July 2026 window (v2026.07)

**This is the most important limitation in the current release.** The snapshot
date is **2026-07-31**, but the three months since the April snapshot were not
swept uniformly:

- **18 states were swept systematically**, month by month, for May, June, and
  July 2026: Alabama, Alaska, Arizona, Arkansas, California, Colorado,
  Connecticut, Delaware, Florida, Georgia, Hawaii, Idaho, Illinois, Indiana,
  Iowa, Kansas, Michigan, and Ohio. Coverage for those states in that window is
  comprehensive. Do not hand-maintain this list: it lives in
  `data/sweep_coverage.json`, is derived by `scripts/update_sweep_coverage.py`,
  and is mirrored into `summary_stats.json` under `sweep_coverage`.
- **The other 32 states were not.** Their new instruments from that window
  entered the dataset opportunistically, when a researcher resolving a flagged
  row happened to encounter one. The sweep for those states was still running
  when this release was cut.

**Swept-and-empty is not the same as unswept.** Of the 18 states swept
systematically, four — Alaska, Delaware, Hawaii, and Idaho — returned **zero**
local moratorium adoptions across all three months. Arizona returned none at the
local level either (its only qualifying action was a state tax-incentive freeze,
excluded as out of scope; see `docs/codebook.md`). Those absences are positive
findings: someone looked and there was nothing. A state absent from the inventory
because nobody has swept it is a different thing entirely, and the two cases are
indistinguishable from the row counts alone.

Treat May-July 2026 counts in the 32 unswept states as **lower bounds**. For
calibration on what the difference is worth: Florida had 1 row before its sweep
was converted and 14 after; Georgia went from 26 to 47. Cross-state comparisons
that include this window will understate the 32 unswept states, and time-series
analyses should either stop at 2026-04-28 or restrict to the 18 swept states.

### Extension and rescission events after the cutoff

Any moratorium extended, replaced, or rescinded after **2026-07-31** won't be
reflected until the next release. In v2026.07 we re-researched every row whose
recorded term had provably expired and every pending row older than 60 days, so
the backlog of stale statuses is cleared as of the snapshot date — but 244
instruments are currently in force and many carry sunsets in the next few
months.

### Disagreement with a sibling dataset (added v2026.07)

A sibling research project maintains its own state-level rollup of data-center
moratoria under different inclusion criteria. Reconciling it against this
inventory (`scripts/reconcile_sibling_tracker.py`) found the two disagree in
**31 of 34 shared states**, in both directions — and it names **44 jurisdictions
across 23 states** that this inventory has no row for, including seven states
where we currently record none at all (Florida, Nevada, New Mexico, Rhode Island,
South Carolina, Texas, Utah).

We did not merge those counts. Two datasets built to different definitions should
not be reconciled by overwriting one with the other, and the disagreement is
itself informative: it puts a floor under how incomplete single-source coverage
of this topic is. All 44 leads were verified individually; roughly three quarters proved real, and
five states (Florida, Nevada, New Mexico, South Carolina, Texas) entered the
dataset as a result. The false positives clustered into four failure modes:
advocacy mistaken for adoption, jurisdiction confusion, proposals counted as
votes, and one instrument that was adopted and then ruled legally invalid by the
jurisdiction's own counsel.

**What this means if you are using the data:** treat the state coverage list as a
lower bound on which states have moratorium activity, not an authoritative
enumeration. A state showing zero here may simply be a state nobody has swept.

### The clause taxonomy lags the inventory (v2026.07)

The 44-clause taxonomy analysis (`data/structured_extractions.jsonl`,
`data/clause_extraction_analysis.json`, and the `definitional-approaches`,
`findings-impact`, and `sector-specific-clauses` tables) rests on a cohort of
**348 documents across 211 jurisdictions, all collected before 2026-04-28**.

v2026.07 nearly doubled the inventory without re-running that extraction, so the
clause percentages now describe roughly half the rows. This was deliberate: the
50-state document sweep was still running, and extracting from a partial corpus
would have produced a cohort mixing two collection snapshots — worse than a clean
one taken later. Of the 200 instruments added this cycle, about 91 have a primary
source that could yield an extractable document; the remaining 109 are news-only
and would contribute nothing to a clause-level analysis regardless.

**What this means:** the inventory-derived tables (`top-states`,
`temporal-distribution`, `state-sector-counts`, `moratorium-inventory`) are
current. The three clause tables are not, and should be cited as describing a
pre-April-2026 sample rather than the present inventory.

Separately, `tables/clause-prevalence.tex` has **no generator** in this
repository and cannot be rebuilt from the shipped data. It is carried forward
from an earlier release.

### Non-English-language jurisdictions

We didn't find any moratoria adopted in languages other than English, but a comprehensive sweep of bilingual border-region jurisdictions or Spanish-language Puerto Rico municipal records was not part of the methodology.

### Federal moratoria and tribal-government moratoria

We document one tribal-government moratorium (Sault Tribe of Chippewa Indians, April 2026, on AI data centers on tribal/trust lands). There may be others we missed, particularly on Bureau of Indian Affairs–trust lands. Federal-level moratoria on federal land (BLM, USFS) are out of scope for this dataset, which focuses on local-government land-use authority.

## What we tried and couldn't get

| Item | Status |
|------|--------|
| Eco TIP West v. Chatham County docket number | Tyler eCourts portal hit Akamai challenge; case caption confirmed via news but file number not retrievable. |
| Watauga County NC April 21, 2026 hearing outcome | County BOC has posted no 2026 records online; no post-hearing news article identified. Listed as `Pending`. |
| Madison County NC replacement ordinance | Planning page lists 5 ordinances, none data-center-specific; moratorium most likely lapsed without replacement. |
| McDowell County NC original 2023 moratorium adoption date | County minutes archive only goes back to May 2023; original adoption was earlier. |
| Numerous small NC town ordinance numbers (Apex, Wendell, Brevard, Canton, Clyde, Swain, Boone) | These towns simply don't publish numbered ordinances online as of April 2026. |
| Buncombe County NC replacement ordinance status | Buncombe Legistar requires authenticated JS state; static fetch returns no items. |
| Wood County OH township cluster (Freedom, Henry, Liberty, Portage, Weston, plus second Plain and Washington Townships) | A single news roundup reports moratoria across these townships, all predating the 2026-04-28 cutoff, but no per-township government source was located for any of them. Deliberately **not** asserted into the inventory on one secondary source; queued for a dedicated pass against each township's own records. |
| South Lyon, MI and Grand Blanc Township, MI | South Lyon's city site shows no trace of its moratorium by direct fetch; Grand Blanc's third-party document portal returns HTTP 403 to every attempt. Both remain `[VERIFY]`-flagged. |

## Geocoding caveats (added v2026.04.2)

414 of 323 jurisdictions are geocoded to WGS84 lat/lon via OSM Nominatim. The 2 blanks are aggregate meta-rows (`Other Reported Local Moratoria, Michigan` and `Proposed or Rejected Local Pauses, Maryland`) that aren't real geographic points.

**Within-state name ambiguity.** Several Ohio townships share names across multiple counties (e.g., 7 different "Washington Township"s, 3 "Plain Township"s, 4 "Lake Township"s). The geocoder picks the highest-rank match, which isn't always the moratorium-adopting jurisdiction. We caught and manually corrected 4 such cases in v2026.04.2:

- Lake Township, OH (Wood County, not Logan County)
- Plain Township, OH (Stark County, not Franklin County)
- Spencer Township, OH (Lucas County, not Lorain County)
- Waterville Township, OH (Lucas County, not Stark County)

If you're using the lat/lon for a point map and a township seems oddly placed, check the row's `legal_basis` and `trigger` text for county hints. We've also flagged Washington Township, OH (40.11, -83.13) as residually ambiguous — the article context doesn't uniquely identify the county.

**The same failure recurred in v2026.07, and is now handled systematically.** Automated geocoding placed *Lyon Township, Michigan* in Roscommon County when the moratorium belongs to Lyon Charter Township in **Oakland County** — 130 miles off, and identifiable only because the row's affected project (the "Project Flex" hyperscale campus near New Hudson) pins the location. That row is now labelled `Lyon Charter Township (Oakland County)`.

Rather than silently patching coordinates, ambiguous and unresolvable cases are now recorded as **declared overrides** in [`scripts/apply_geo_overrides.py`](../scripts/apply_geo_overrides.py), each carrying a `why` field stating the evidence that settles which place is meant. The current overrides are:

| Row | Problem | Resolution |
|---|---|---|
| Lyon Charter Township, MI | Two Lyon Townships in Michigan | Oakland County, per the affected project's location |
| Forsyth Township, MI | Bare name resolved in neither geocoder | Marquette County, per the Gwinn / K.I. Sawyer reporting |
| Mercer County Fiscal Court, KY | "Fiscal Court" suffix defeats lookup | The fiscal court *is* the county government; use Mercer County |
| City of Effingham, IL | Stripping the prefix returns Effingham **County**, not the city | The city centroid; the county is a separate jurisdiction that declined to act |

Three "City of X" rows originally needed overrides. Investigating why turned up a
real bug rather than a data problem: `geocode_inventory.py` defined a
prefix-stripping regex and **never called it**, so every `City of ...` row fell
straight through to manual review. The geocoder now retries with the
governing-body prefix removed, and those overrides were retired — except
Effingham, where the stripped form resolves to the surrounding county instead of
the city.

The lessons that generalize: a jurisdiction name alone is not a geographic key in
states with repeated township names; governing-body prefixes and suffixes
("City of", "Fiscal Court", "Charter Township") defeat geocoders; and a
same-named county sitting around a city will outrank it. Expect to curate a few
of these by hand each refresh — but check first whether the failure is a class the
geocoder should handle.

**Audit confidence.** Geocoded coordinates were triple-checked across 89 verifications via three independent methods: spot-check against geographic knowledge, Wikipedia GeoSearch reverse-lookup (does the jurisdiction's name appear in nearby Wikipedia pages?), and nearby-page context analysis (when a township has no Wikipedia article, do nearby places confirm the right county?). Across all 89 verifications, **zero confirmed wrong geocodes** (after the 4 manual corrections above). Treat the lat/lon column as ≥99% accurate.

When new releases add new same-name townships, expect a small number of similar issues until the geocoder catches up.

## What gets fixed in each release

- New moratoria adopted between releases get added.
- `[VERIFY]` flags get resolved as towns post their post-meeting minutes online.
- Outcomes of pending moratoria (extended/replaced/expired/rescinded) get updated.
- Errors flagged by the community via the issue tracker get corrected.

If you have access to one of the records above and want to share it, please [open an issue](https://github.com/mjbommar/moratorium-data-2026/issues). We'll add it and credit you in the next release.

## Selection bias

This dataset is biased toward jurisdictions that:

1. Post agendas and minutes online
2. Have local newspapers or trade-press coverage
3. Have moratoria of large enough scope to attract attention

A small township in a rural county that adopts a 90-day data-center moratorium and never tells anyone is statistically very likely to be missing from this dataset. The bias is structural, not avoidable, and we don't try to correct for it. Treat the corpus as a high-confidence lower bound on the true count of moratoria, not as a probability sample.

## Confidence on individual entries

The `has_verify_tags`, `verify_count`, and `verify_notes` fields tell you which rows are most certain and which have remaining open questions. When we use a row in the structured-extraction analysis, a confidence score (0.0 to 1.0) is also attached.

For any specific row you want to use in a publication, **always read the `verify_notes` first** and cite a primary source rather than just our row.
