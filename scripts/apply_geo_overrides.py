#!/usr/bin/env python3
"""Apply declared geocoding overrides for ambiguous jurisdiction names.

Automated geocoding resolves a bare jurisdiction name to whichever match the
provider ranks first, which is wrong whenever a state has several places with
the same name. Michigan has a Lyon Township in Oakland County and another in
Roscommon County; the geocoder picked the wrong one, putting a Detroit-area
hyperscale moratorium 130 miles north.

Every override here is declared with the evidence that settles which place is
meant, so the correction is reviewable rather than a bare coordinate edit.
Overrides may also disambiguate the `jurisdiction` label itself, which the
codebook permits ("May include disambiguating context").

Entries here should be genuine ambiguities, not cases the geocoder can handle.
When geocode_inventory.py learns to resolve a class of name, retire the overrides
it supersedes so this table keeps meaning "a human had to decide this."

Idempotent. Run from repo root:
    python3 scripts/apply_geo_overrides.py --dry-run
    python3 scripts/apply_geo_overrides.py
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"

# moratorium_id -> override
OVERRIDES: dict[str, dict] = {
    "ak-fairbanks-north-star-borough-undated": {'latitude': '64.670454', 'longitude': '-146.496061', 'why': 'Reviewed Census2026 Fairbanks North Star Borough GEOID 02090 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ak-petersburg-borough-undated": {'latitude': '57.245959', 'longitude': '-132.788762', 'why': 'Reviewed Census2026 Petersburg Borough GEOID 02195 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ca-hayward-2026": {'latitude': '37.626826', 'longitude': '-122.104015', 'why': 'Reviewed Census2026 Hayward city GEOID 0633000 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "co-brighton-undated": {'latitude': '39.965676', 'longitude': '-104.794056', 'why': 'Reviewed Census2026 Brighton city GEOID 0808675 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "co-fort-collins-undated": {'latitude': '40.548405', 'longitude': '-105.064988', 'why': 'Reviewed Census2026 Fort Collins city GEOID 0827425 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "co-phillips-county-2025": {'latitude': '40.594712', 'longitude': '-102.345105', 'why': 'Reviewed Census2026 Phillips County GEOID 08095 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "co-phillips-county-2024": {'latitude': '40.594712', 'longitude': '-102.345105', 'why': 'Reviewed Census2026 Phillips County GEOID 08095 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "de-kent-county-2022": {'latitude': '39.097088', 'longitude': '-75.502982', 'why': 'Reviewed Census2026 Kent County GEOID 10001 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "de-kent-county-undated": {'latitude': '39.097088', 'longitude': '-75.502982', 'why': 'Reviewed Census2026 Kent County GEOID 10001 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ga-union-county-2026": {'latitude': '34.833333', 'longitude': '-83.989257', 'why': 'Reviewed Census2026 Union County GEOID 13291 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "id-blaine-county-undated": {'latitude': '43.394179', 'longitude': '-113.955387', 'why': 'Reviewed Census2026 Blaine County GEOID 16013 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "il-chicago-undated": {'latitude': '41.837045', 'longitude': '-87.684939', 'why': 'Reviewed Census2026 Chicago city GEOID 1714000 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "il-stephenson-county-2026": {'latitude': '42.349726', 'longitude': '-89.665994', 'why': 'Reviewed Census2026 Stephenson County GEOID 17177 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "in-vermillion-county-undated": {'latitude': '39.854045', 'longitude': '-87.462071', 'why': 'Reviewed Census2026 Vermillion County GEOID 18165 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "in-zionsville-undated": {'latitude': '39.991538', 'longitude': '-86.321762', 'why': 'Reviewed Census2026 Zionsville town GEOID 1886372 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ia-sac-county-2025": {'latitude': '42.387526', 'longitude': '-95.105224', 'why': 'Reviewed Census2026 Sac County GEOID 19161 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ia-sioux-county-2023": {'latitude': '43.082618', 'longitude': '-96.17798', 'why': 'Reviewed Census2026 Sioux County GEOID 19167 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ky-camargo-2026": {'latitude': '37.999694', 'longitude': '-83.888489', 'why': 'Reviewed Census2026 Camargo city GEOID 2112052 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "la-bossier-parish-2022": {'latitude': '32.693317', 'longitude': '-93.631366', 'why': 'Reviewed Census2026 Bossier Parish GEOID 22015 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "me-ashland-2024": {'latitude': '46.650441', 'longitude': '-68.388373', 'why': 'Reviewed Census2026 Ashland town GEOID 2300301710 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "me-bridgton-2022": {'latitude': '44.047513', 'longitude': '-70.743319', 'why': 'Reviewed Census2026 Bridgton town GEOID 2300507170 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "md-talbot-county-2022": {'latitude': '38.747066', 'longitude': '-76.177374', 'why': 'Reviewed Census2026 Talbot County GEOID 24041 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ma-braintree-undated": {'latitude': '42.206188', 'longitude': '-71.00232', 'why': 'Reviewed Census2026 Braintree Town city GEOID 2507740 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ma-methuen-undated": {'latitude': '42.742648', 'longitude': '-71.178643', 'why': 'Reviewed Census2026 Methuen city GEOID 2540675 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "mi-locke-township-2023": {'latitude': '42.733945', 'longitude': '-84.206362', 'why': 'Reviewed Census2026 Locke township GEOID 2606549040 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "mi-locke-township-2023-2": {'latitude': '42.733945', 'longitude': '-84.206362', 'why': 'Reviewed Census2026 Locke township GEOID 2606549040 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "mi-meridian-township-2026-2": {'latitude': '42.725291', 'longitude': '-84.419722', 'why': 'Reviewed Census2026 Meridian charter township GEOID 2606553140 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "mn-pequot-lakes-undated": {'latitude': '46.588091', 'longitude': '-94.287969', 'why': 'Reviewed Census2026 Pequot Lakes city GEOID 2750416 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ne-sarpy-county-2020": {'latitude': '41.115064', 'longitude': '-96.109125', 'why': 'Reviewed Census2026 Sarpy County GEOID 31153 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "nj-east-windsor-undated": {'latitude': '40.259139', 'longitude': '-74.533576', 'why': 'Reviewed Census2026 East Windsor township GEOID 3402119780 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "nm-silver-city-2021": {'latitude': '32.778581', 'longitude': '-108.269409', 'why': 'Reviewed Census2026 Silver City town GEOID 3573260 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ny-massena-undated": {'latitude': '44.96202', 'longitude': '-74.83465', 'why': 'Reviewed Census2026 Massena town GEOID 3608946030 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "ny-niagara-2024": {'latitude': '43.115446', 'longitude': '-78.98098', 'why': 'Reviewed Census2026 Niagara town GEOID 3606351033 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "nc-town-of-mooresville-undated": {'latitude': '35.583591', 'longitude': '-80.828328', 'why': 'Reviewed Census2026 Mooresville town GEOID 3744220 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "sc-awendaw-undated": {'latitude': '32.967885', 'longitude': '-79.654755', 'why': 'Reviewed Census2026 Awendaw town GEOID 4503385 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "tn-orlinda-2026": {'latitude': '36.593839', 'longitude': '-86.701561', 'why': 'Reviewed Census2026 Orlinda city GEOID 4756020 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "wa-spokane-valley-2026": {'latitude': '47.663353', 'longitude': '-117.23278', 'why': 'Reviewed Census2026 Spokane Valley city GEOID 5367167 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "wa-whitman-county-2025": {'latitude': '46.905944', 'longitude': '-117.53539', 'why': 'Reviewed Census2026 Whitman County GEOID 53075 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "wi-sun-prairie-2026": {'latitude': '43.183796', 'longitude': '-89.234319', 'why': 'Reviewed Census2026 Sun Prairie city GEOID 5578600 internal representative point; retained record identity checked. Not a boundary, project point, legal applicability or current-force finding. Receipt: work/research/2026-11-09/post-release-qa/missing-geography-application.json.'},
    "oh-ada-2026": {"latitude": "40.768139", "longitude": "-83.825211", "why": "Verified municipal identity against official Census2025Ohio place internal point and retained primary municipal source; previous point failed >25km screen. Internal representative point only, not boundary/applicability. Review: work/research/2026-11-06/ohio-municipal-geography-review/."},
    "oh-clinton-2026": {"latitude": "40.928138", "longitude": "-81.631137", "why": "Verified municipal identity against official Census2025Ohio place internal point and retained primary municipal source; previous point failed >25km screen. Internal representative point only, not boundary/applicability. Review: work/research/2026-11-06/ohio-municipal-geography-review/."},
    "oh-jefferson-2026": {"latitude": "41.738411", "longitude": "-80.768782", "why": "Verified municipal identity against official Census2025Ohio place internal point and retained primary municipal source; previous point failed >25km screen. Internal representative point only, not boundary/applicability. Review: work/research/2026-11-06/ohio-municipal-geography-review/."},
    "oh-warren-2026": {"latitude": "41.239564", "longitude": "-80.816015", "why": "Verified municipal identity against official Census2025Ohio place internal point and retained primary municipal source; previous point failed >25km screen. Internal representative point only, not boundary/applicability. Review: work/research/2026-11-06/ohio-municipal-geography-review/."},
    "oh-perry-undated": {
        "latitude": "41.763674",
        "longitude": "-81.143013",
        "why": (
            "The reviewed Ordinance 2026-13 belongs to Perry village in Lake County, "
            "as independently confirmed by https://perryvillageohio.com/. The 2025 "
            "Census Ohio Gazetteer identifies Perry village GEOID 3961882 and this "
            "internal point (not a geometric centroid or legal boundary): "
            "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_gaz_place_39.txt. "
            "Corrects the prior 39.637029,-82.204437 wrong-location result; distinct "
            "from North Perry village, Perry Heights CDP and Perry Township. "
            "Primary review: work/research/2026-11-06/perry-geography-review/."
        ),
    },
    "mi-caledonia-township-undated": {
        "latitude": "42.812169",
        "longitude": "-85.487564",
        "why": (
            "Michigan has a Caledonia Township in Alcona County and Caledonia Charter Township "
            "in Kent County. The moratorium is the Kent County township's (its minutes and the "
            "Grand Rapids-area coverage); automated geocoding had returned the Alcona County "
            "township. Found in QA round 3 (2026-09-23)."
        ),
    },
    "mi-lincoln-township-2026": {
        "latitude": "42.0178900",
        "longitude": "-86.5049670",
        "why": (
            "Same-name township: the row's evidence places it in Berrien County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Lincoln Township (Berrien County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-porter-township-2026": {
        "latitude": "41.8311645",
        "longitude": "-85.8183348",
        "why": (
            "Same-name township: the row's evidence places it in Cass County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Porter Township (Cass County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-washington-township-2026": {
        "latitude": "42.7570924",
        "longitude": "-83.0373036",
        "why": (
            "Same-name township: the row's evidence places it in Macomb County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Washington Township (Macomb County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "oh-richfield-township-2026": {
        "latitude": "41.6905055",
        "longitude": "-83.8301363",
        "why": (
            "Same-name township: the row's evidence places it in Lucas County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Richfield Township (Lucas County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "oh-scioto-township-2026": {
        "latitude": "39.7567168",
        "longitude": "-83.0802156",
        "why": (
            "Same-name township: the row's evidence places it in Pickaway County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Scioto Township (Pickaway County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-buffalo-township-2026": {
        "latitude": "40.7149082",
        "longitude": "-79.7385009",
        "why": (
            "Same-name township: the row's evidence places it in Butler County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Buffalo Township (Butler County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-butler-township-2026": {
        "latitude": "41.0395791",
        "longitude": "-75.9880458",
        "why": (
            "Same-name township: the row's evidence places it in Luzerne County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Butler Township (Luzerne County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-center-township-2026": {
        "latitude": "40.9329281",
        "longitude": "-79.9265663",
        "why": (
            "Same-name township: the row's evidence places it in Butler County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Center Township (Butler County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-smithfield-township-2026": {
        "latitude": "41.0073171",
        "longitude": "-75.1324962",
        "why": (
            "Same-name township: the row's evidence places it in Monroe County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Smithfield Township (Monroe County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "pa-warrington-township-2026": {
        "latitude": "40.0656653",
        "longitude": "-76.9368682",
        "why": (
            "Same-name township: the row's evidence places it in York County, but automated "
            "geocoding of the bare name had returned a township of the same name in another "
            "county. Row renamed 'Warrington Township (York County)' in QA round 1 (2026-09-23); coordinates resolved "
            "by hand with Nominatim."
        ),
    },
    "mi-howard-charter-township-cass-county-undated": {
        "latitude": "41.855143",
        "longitude": "-86.165948",
        "why": (
            "'Howard Charter Township' is not how the gazetteer names the Cass County "
            "township (it is plain 'Howard Township'), so the county-qualified query still "
            "fell through to a Grand Traverse County match. Resolved by hand with Nominatim "
            "on 2026-09-23 (QA round 1)."
        ),
    },
    "ak-houston-undated": {
        "latitude": "61.630278",
        "longitude": "-149.818055",
        "why": (
            "Neither geocoder resolved bare 'Houston, Alaska' (Texas wins the name). The instrument is the City of Houston in the Matanuska-Susitna Borough (Ordinance 26-20). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ca-patterson-2026": {
        "latitude": "37.471623",
        "longitude": "-121.129695",
        "why": (
            "Bare 'Patterson, California' failed both geocoders. The row is the City of Patterson, Stanislaus County (its council adopted the 2026-07-16 urgency ordinance). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ga-chatham-county-2026": {
        "latitude": "31.966889",
        "longitude": "-81.062601",
        "why": (
            "'Chatham County, Georgia' failed the Census geocoder (it resolves places, not counties) and Nominatim ranked North Carolina's Chatham County first in bulk mode. The instrument is the Savannah-area county. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ga-toccoa-2026": {
        "latitude": "34.577437",
        "longitude": "-83.332881",
        "why": (
            "Bare 'Toccoa' failed both geocoders; the row is the City of Toccoa, Stephens County. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "ky-boyd-county-fiscal-court-2026": {
        "latitude": "38.360893",
        "longitude": "-82.694593",
        "why": (
            "'Fiscal Court' is the Kentucky county legislative body, not a place, and defeated both geocoders. The referent is Boyd County (Ashland area). Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "oh-swancreek-township-fulton-county-2026": {
        "latitude": "41.537719",
        "longitude": "-83.940839",
        "why": (
            "The township spells itself 'Swancreek' but the gazetteer entry is 'Swan Creek Township, Fulton County'; neither geocoder bridged the spelling. Resolved by hand with Nominatim on 2026-09-23."
        ),
    },
    "mi-park-township-2026": {
        "jurisdiction": "Park Township (St. Joseph County)",
        "latitude": "42.016737",
        "longitude": "-85.586519",
        "why": (
            "Michigan has a Park Township in Ottawa County (Holland area) and another in "
            "St. Joseph County. The moratorium's own record is park-township.org, whose "
            "May 13 and September 9, 2026 board minutes carry St. Joseph County reports, so "
            "the St. Joseph County township is the referent. Automated geocoding had "
            "returned the Ottawa County township at 42.812025 / -86.174118 (2026-09-23 refresh)."
        ),
    },
    "mi-lyon-township-2026": {
        "jurisdiction": "Lyon Charter Township (Oakland County)",
        "latitude": "42.476464",
        "longitude": "-83.613258",
        "why": (
            "Michigan has a Lyon Township in Oakland County and another in Roscommon "
            "County. The record's affected project, the 'Project Flex' hyperscale campus "
            "near New Hudson, is in Oakland County, so the Oakland County township is the "
            "correct referent. Automated geocoding had returned the Roscommon County "
            "township at 44.482887 / -84.792879."
        ),
    },
    "pa-brookville-borough-2026": {
        "latitude": "41.160435",
        "longitude": "-79.079470",
        "why": (
            "The 'Borough' suffix defeated both geocoders. Pennsylvania boroughs are "
            "incorporated municipalities, so the referent is simply the place: Brookville, "
            "Jefferson County."
        ),
    },
    "tn-unincorporated-hamilton-county-2026": {
        "latitude": "35.175564",
        "longitude": "-85.194079",
        "why": (
            "'Unincorporated Hamilton County' has no gazetteer entry -- it is the part of the "
            "county outside its municipalities, which is the moratorium's actual scope. The "
            "county centroid is the honest representative point; it is not a municipal boundary."
        ),
    },
    "il-city-of-effingham-2026": {
        "latitude": "39.120143",
        "longitude": "-88.543480",
        "why": (
            "geocode_inventory.py now retries with the governing-body prefix stripped, "
            "which resolves most 'City of X' rows automatically -- but not this one: a bare "
            "'Effingham, Illinois' lookup returns Effingham COUNTY first. This row is the "
            "city's Ordinance 052-2026, and the county is a distinct jurisdiction that "
            "separately declined to act for want of zoning authority."
        ),
    },
    "mi-forsyth-township-2026": {
        "latitude": "46.246523",
        "longitude": "-87.428150",
        "why": (
            "Bare 'Forsyth Township, Michigan' resolved in neither geocoder. The reporting "
            "places this action in the Gwinn / K.I. Sawyer area, i.e. Forsyth Township in "
            "Marquette County, which resolves once the county is supplied."
        ),
    },
    "ky-mercer-county-fiscal-court-undated": {
        "latitude": "37.808758",
        "longitude": "-84.876084",
        "why": (
            "Both geocoders failed on 'Mercer County Fiscal Court, Kentucky'. In Kentucky "
            "the fiscal court IS the county's governing body, so the geographic referent is "
            "simply Mercer County; resolved by querying the county name alone."
        ),
    },
}


def read_rows() -> tuple[list[dict], list[str]]:
    with open(INV, encoding="utf-8", newline="") as f:
        src = f.read()
    reader = csv.DictReader(io.StringIO(src))
    return list(reader), list(reader.fieldnames or [])


def write_rows(rows: list[dict], fieldnames: list[str]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    with open(INV, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows, fieldnames = read_rows()
    by_id = {r["moratorium_id"]: r for r in rows}

    changes: list[str] = []
    missing: list[str] = []

    for mid, override in OVERRIDES.items():
        row = by_id.get(mid)
        if row is None:
            missing.append(mid)
            continue
        for column, value in override.items():
            if column == "why":
                continue
            if column not in fieldnames:
                print(f"ERROR: unknown column {column!r} in override for {mid}")
                return 2
            if row[column] == value:
                continue
            changes.append(f"  {mid}.{column}: {row[column]!r} -> {value!r}")
            row[column] = value

    if missing:
        print(f"WARNING: {len(missing)} override target(s) not present in the inventory:")
        for mid in missing:
            print(f"  {mid}")

    if not changes:
        print("All overrides already applied.")
        return 0

    print(f"{len(changes)} cell(s):")
    for line in changes:
        print(line)

    if args.dry_run:
        print("\nDry run - nothing written.")
        return 0

    write_rows(rows, fieldnames)
    print(f"\nWrote {INV.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
