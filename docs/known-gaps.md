# Known gaps and limitations

We're confident in what's in this dataset, but here's an honest accounting of what we know we're missing.

## What we know we don't have

### Small-township records that aren't online

Many small townships and rural counties don't post agendas, minutes, or signed ordinances on the web. When we know a moratorium exists from news coverage but can't pull the underlying instrument, we record it with a `[VERIFY]` note in `verify_notes` rather than guessing at the ordinance number or exact date. Roughly **63 of the 223 inventory rows** have at least one such evidence-ceiling note.

### Records behind authentication or CAPTCHA gates

Some primary sources (notably the NC eCourts portal at `portal-nc.tylertech.cloud`, several Legistar instances, and certain Granicus-archived meetings) are protected by Akamai-style human-verification challenges that defeat automated retrieval. For affected entries, we use the best secondary source (county press releases, local news) and document the evidence ceiling.

### Extension and rescission events after the cutoff

Our snapshot is **April 2026**. Any moratorium extended, replaced, or rescinded after that date won't be reflected until the next release. About 130 of the 223 moratoria were enacted in 2025–2026 and are still in their original window — many will be extended or replaced in the next few months.

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

## Geocoding caveats (added v2026.04.2)

220 of 222 jurisdictions are geocoded to WGS84 lat/lon via OSM Nominatim. The 2 blanks are aggregate meta-rows (`Other Reported Local Moratoria, Michigan` and `Proposed or Rejected Local Pauses, Maryland`) that aren't real geographic points.

**Within-state name ambiguity.** Several Ohio townships share names across multiple counties (e.g., 7 different "Washington Township"s, 3 "Plain Township"s, 4 "Lake Township"s). The geocoder picks the highest-rank match, which isn't always the moratorium-adopting jurisdiction. We caught and manually corrected 4 such cases in v2026.04.2:

- Lake Township, OH (Wood County, not Logan County)
- Plain Township, OH (Stark County, not Franklin County)
- Spencer Township, OH (Lucas County, not Lorain County)
- Waterville Township, OH (Lucas County, not Stark County)

If you're using the lat/lon for a point map and a township seems oddly placed, check the row's `legal_basis` and `trigger` text for county hints. We've also flagged Washington Township, OH (40.11, -83.13) as residually ambiguous — the article context doesn't uniquely identify the county.

When new releases add new same-name townships, expect a small number of similar issues until the geocoder catches up. Treat the lat/lon column as 99%+ accurate, not 100%.

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
