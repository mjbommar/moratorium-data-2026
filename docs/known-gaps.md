# Known gaps and limitations

We're confident in what's in this dataset, but here's an honest accounting of what we know we're missing.

## What we know we don't have

### Small-township records that aren't online

Many small townships and rural counties don't post agendas, minutes, or signed ordinances on the web. When we know a moratorium exists from news coverage but can't pull the underlying instrument, we record it with a `[VERIFY]` note in `verify_notes` rather than guessing at the ordinance number or exact date. **300 of the 1291 inventory rows** have at least one such evidence-ceiling note (`has_verify_tags = True`), down from 123 of 222 in v2026.04.4 after a targeted verification pass.

### Records behind authentication or CAPTCHA gates

Some primary sources (notably the NC eCourts portal at `portal-nc.tylertech.cloud`, several Legistar instances, and certain Granicus-archived meetings) are protected by Akamai-style human-verification challenges that defeat automated retrieval. For affected entries, we use the best secondary source (county press releases, local news) and document the evidence ceiling.

### Coverage of the May–July 2026 window (v2026.07)

**All 50 states were swept** month by month for May, June, and July 2026. We
once said this made the counts for those months complete. The September 2026
update proved that wrong. It found 161 more moratoria adopted in those three
months, mostly in small Ohio and Michigan townships. The monthly search reached
counties and cities, but it often missed the smallest towns. Read the May–July
counts as the fewest there could be, like every other month.

**8 states recorded no local adoption during the window**: Alaska, Arizona,
Delaware, Hawaii, New Hampshire, Vermont, West Virginia, and Wyoming. The
first version of this list named ten states. It was wrong about three of them.
Idaho, Louisiana, and Rhode Island each adopted a moratorium in those months
that the sweep missed. New Hampshire joins the list because its only moratorium
passed in September. Wyoming is the clearest case. Cheyenne's council voted
down a twelve-month moratorium 9 to 1, so Wyoming has none because its council
said no, not because nobody looked.

**What the sweep was worth.** Conversion changed several states' counts
dramatically, and none of it was because anything changed on the ground:

| State | Before its sweep | After |
|---|---|---|
| Florida | 1 | 14 |
| Georgia | 26 | 47 |
| South Carolina | 1 | 6 |
| Utah | 0 | 6 |

Take that as the measure of what single-source coverage of this topic misses.

**Earlier windows were not swept this way.** Anything dated before 2026-05-01
entered the dataset through document search and opportunistic discovery, so those
counts remain lower bounds. A time series across the 2026-05 boundary will show a
step that is partly method, not only events.

The machine-readable record is `data/sweep_coverage.json`, derived by
`scripts/update_sweep_coverage.py` and mirrored into `summary_stats.json` under
`sweep_coverage`.

### Coverage of the September 2026 update

On September 23, 2026 we searched every state for moratoria we did not have.
Then we ran four rounds of checks, including a comparison with nine other
public lists. The list is now far more complete for August and September than
before.

It is still not a full count. This time we searched each state as a whole,
not month by month. A small town whose only record is a post on social media,
or a story behind a paywall, can still slip through. So treat the counts for
August and September as the fewest there could be. `data/sweep_coverage.json`
records this search under `discovery_passes`, apart from the monthly sweep.

**Most of the added moratoria are older, and they are real.** 276 of the 520
rows this update added were adopted before August. We checked each one against
its saved source. We also checked a random sample with people who saw only the
place name. Almost all held up. They come from townships and villages that
earlier searches did not reach. Other public lists name most of them too.

**Battery storage, solar, and wind are not covered evenly.** Until this update,
the list included those pauses only when they came bundled with a data center
pause. The checks added 127 New York town and village pauses, most of them on
battery storage, and about 20 elsewhere. We have not searched other states for
these pauses the same way. So their counts are low, and 20 more entries from
other lists are still waiting to be looked up.

**Three states still have none:** Hawaii, West Virginia, and Wyoming. In West
Virginia, a state law (HB 2014) stops towns and counties from limiting large
data centers. In Wyoming, Cheyenne voted its proposal down.

### Changes after September 23, 2026

A moratorium can be extended, replaced, or ended at any meeting. Anything that
happened after September 23, 2026 is not in this update. Before that date we
rechecked four kinds of rows. We looked at rows past their end date and
extensions with no new end date. We also looked at proposals more than 60 days
old and rows with a `[VERIFY]` note.

1063 moratoria are in force, and many end in the next few months. The data
check still flags eleven rows that look out of date. Eight of them, in
Cedartown, Georgia and seven New York towns, have passed their end date. We
could not find out what happened next, so each carries a `[VERIFY]` note. The
other three are fine. Waterford Township, Michigan and East Whiteland Township,
Pennsylvania have votes set for the days after September 23. Westfield, New
York was confirmed from its own minutes.

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

**What this means if you are using the data:** for the 2026-05 to 2026-07 window
the state list is now an enumeration rather than a lower bound, because every
state was swept. Outside that window it remains a lower bound.

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

1289 of 1291 instruments are geocoded to WGS84 lat/lon via Nominatim, the place-name search service of OpenStreetMap (OSM). The 2 blanks are aggregate meta-rows (`Other Reported Local Moratoria, Michigan` and `Proposed or Rejected Local Pauses, Maryland`) that aren't real geographic points.

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


**In September 2026 we found this problem in 37 rows and fixed the cause.**
To put a row on the map, a script looks up its place name. Our script dropped
the county from names like "Washington Township (Stark County)" before looking
them up. So for any township name found in more than one county, it could pick
the wrong one. We checked every row against the county it names and found 37 in
the wrong place. A few had been wrong for months, such as Calhoun, Georgia and
Warrington Township, Pennsylvania. The script now keeps the county in the name.
We added the county to township names that lacked one. We also placed the rest by
hand, with the reason written in `scripts/apply_geo_overrides.py`. The 243 rows
added in the checks were tested the same way, and none were misplaced.

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
