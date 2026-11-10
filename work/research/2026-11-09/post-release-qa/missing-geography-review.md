# Missing-coordinate discovery, November 9, 2026

The current local inventory has 41 rows without coordinates across 25 states. Four bounded HTTP captures retained the official Census 2026 directory and the national county, place, and county-subdivision ZIP files. Three lossless member derivations are retained in the US source manifest. No paid searches or model calls were used.

The attached reproducible audit found exactly one state/name/type candidate for each of the 39 named-jurisdiction rows. Two aggregate rows (Maryland proposed/rejected pauses and Michigan other reported moratoria) have no jurisdiction to map and must remain blank. The 39 observations include repeated jurisdictions; they are not 39 distinct governments.

These are candidates, not applied corrections or closed legal QA questions. Identity review must compare retained record evidence, especially the Maine and New York towns, Michigan townships, East Windsor township, Braintree Town city, and Sun Prairie city rather than its separate town. Census internal points are representative map anchors, not geometric centroids, legal boundaries, project sites, or evidence that a policy applies throughout the jurisdiction.

The audit pins inventory bytes, each normalized input row, the source ZIPs, and exact member bytes. Inputs use pipe delimiters, unlike some earlier Gazetteer editions. Candidate coordinates preserve the source strings. Canonical CSV, maps, dispositions, published release and consumer snapshot remain unchanged by this discovery step.

Next: authenticate the 39 jurisdiction identities against retained source context, integrate justified points with guarded writes and regenerated map outputs, and leave any ambiguous identities blank. Whole-record legal-force questions remain open unless separately resolved.

## Applied identity review

All39 candidate identities were checked against retained source bodies and text; their hashes were recomputed. Michigan Ingham County and New Jersey Mercer County identities match the Census subdivision county codes. New York towns remain distinct from villages/cities, Sun Prairie uses the city rather than town, and Braintree Town city retains the inventory label. Pequot Lakes letterhead was visually inspected because text extraction omits the city logo. Sun Prairie uses the already reviewed full-DOM derivation rather than the incomplete original extraction.

The [guarded application](missing-geography-application.json) changes78 coordinate cells and no other canonical fields. The persistent overrides and interactive GeoJSON are updated. Legal questions and whole-record dispositions remain open. Seven exact native source-body/text pairs were read back and verified. The paper map generators aggregate by state and do not read coordinates; they require no image regeneration for this coordinate-only update. The downloadable map layer is regenerated.
