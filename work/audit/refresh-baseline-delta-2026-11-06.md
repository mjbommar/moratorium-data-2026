# Working refresh: baseline comparison

Baseline: `dbaab04d84f8d679ba5a3d57bf45f32186109222`, whose README describes September 23, 2026.
The current comparison was generated from base revision `3773212` and the working-tree
CSV bytes pinned in the JSON. This compares working data, not the last public
release. The cohort cutoff remains November 5; later scoped reviews do not renew
all-record legal-force freshness.

| Metric | Baseline | Current | Delta |
|---|---:|---:|---:|
| Local instruments | 1291 | 1329 | +38 |
| Active | 897 | 888 | -9 |
| Extended | 166 | 192 | +26 |
| Active plus extended | 1063 | 1080 | +17 |
| Pending | 77 | 79 | +2 |
| Replaced | 93 | 94 | +1 |
| Rescinded | 8 | 12 | +4 |
| Expired | 50 | 64 | +14 |
| State-policy records | 440 | 442 | +2 |
| State-policy records classified enacted | 85 | 95 | +10 |

The enacted policy total includes 94 records using the legacy bill type and one
executive order. The tracker covers multiple policy mechanisms. Resolution
subtypes remain inside the legacy bill category; it is not a verified denominator
of bills or enacted state moratoria.

Thirty-eight local records were added: `ak-fairbanks-north-star-borough-undated`, `ak-petersburg-borough-undated`, `ca-hayward-2026`, `co-brighton-undated`, `co-fort-collins-undated`, `co-phillips-county-2024`, `co-phillips-county-2025`, `de-kent-county-2022`, `de-kent-county-undated`, `ga-union-county-2026`, `ia-dubuque-county-2026-2`, `ia-sac-county-2025`, `ia-sioux-county-2023`, `id-blaine-county-undated`, `il-chicago-undated`, `il-stephenson-county-2026`, `in-vermillion-county-undated`, `in-zionsville-undated`, `ky-camargo-2026`, `la-bossier-parish-2022`, `ma-braintree-undated`, `ma-methuen-undated`, `md-talbot-county-2022`, `mi-locke-township-2023`, `mi-locke-township-2023-2`, `mi-meridian-township-2026-2`, `mn-pequot-lakes-undated`, `nc-town-of-mooresville-undated`, `ne-sarpy-county-2020`, `nj-east-windsor-undated`, `nm-silver-city-2021`, `ny-massena-undated`, `ny-niagara-2024`, `sc-awendaw-undated`, `tn-orlinda-2026`, `wa-spokane-valley-2026`, `wa-whitman-county-2025`, `wi-sun-prairie-2026`. Two policy records were added:
`ca-ab2469-2025-2026`, `nj-a4696-2026-2027`. No baseline IDs were removed. Among surviving baseline records,
446 local and 30 policy records have changed fields.
These are edit counts, not completed record reviews or counts of new enactments.
The two Kent additions describe historical terms ending in 2022 and 2023; the wind
adoption-year conflict remains explicit.

The separate expanded publication contains 49 reviewed ballot measures, 55 retained
result observations, one proposed restriction with unknown legal status and one
accepted ballot `proposes` link. Of 56 frozen candidate groups, 49 have scoped
publication and seven remain unresolved. This is a reviewed subset, not a complete
election census. No Edgewater adoption event or in-force ban is inferred.

The November 5 collection accounting remains historical. Its 440-policy denominator
must not be reused as the current policy total. Current field-lineage accounting
is separate from substantive source/legal review.

Reproduce the machine-readable comparison:

```sh
python3 scripts/build_refresh_headline_delta.py
```

The [JSON report](refresh-baseline-delta-2026-11-06.json) pins CSV hashes, all
added/removed IDs and changed fields, plus the ballot projection and snapshot.
Regeneration against later data requires updating this prose. Five reviewed Ohio
point corrections and the Warren identifier correction remain descriptive changes,
with no headline-count effect. No result here proves complete legal-force
verification, consumer synchronization or release publication.
