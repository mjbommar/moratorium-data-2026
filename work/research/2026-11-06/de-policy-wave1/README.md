# Delaware state-policy review — November 6, 2026

All three existing Delaware records in the distributed `gpt-6.1-terra` return `de-state-policy-001` received coordinator review. Retained evidence acquired November 5 was checked for body/text integrity and exact quoted text. November 6 recovery independently obtained two signed-bill pages, four current code chapters, and the SB 205 page through bc-web/pydoll (visible browser, 1,500 ms settle). This is a bounded statutory/disposition review, not a complete rulemaking, litigation or implementation audit.

| Existing stable record | Accepted result | Limits |
|---|---|---|
| de-hb-233 | House Substitute 1 signed/effective August 26, 2026; 85 Del. Laws chapter 440. Current 26 Del. C. § 203G contains ESA/TSA requirements. | Original HB 233 was substituted, not itself signed. One stable umbrella record explicitly tracks the successor; no duplicate enacted bill is added. Tariff/rulemaking completion is unverified. |
| de-sb-312 | Signed/effective August 26, 2026; chapter 447. Current 9 Del. C. § 401, 22 Del. C. § 2101 and 29 Del. C. § 612 contain county, municipal and state-agency NDA restrictions. | This is a transparency restriction, not a development moratorium. No complete enforcement/challenge history is asserted. |
| de-sb-205 | Final recorded status: Out of Committee, March 11, 2026, after the assembly ended; retain failed disposition. Browser page shows no floor roll-call records. | Remove unsupported precise sine die dates. SA 1 introduction on January 28 is displayed, but the amendment's substantive text remains unreviewed; its existing summary is not fully reverified. |

## Corrected HB 233 successor substance

The final engrossment defines large energy use facilities through alternative thresholds: monthly maximum demand of at least 75 MW at a load factor of at least 85%; monthly maximum instantaneous demand of at least 100 MW; or monthly maximum demand of at least 30 MW for facilities primarily engaged in NAICS 518210 services. Aggregation and specified exclusions also apply. The old 20 MW data-center threshold is incorrect for the enacted substitute.

Section 6 takes effect upon enactment, but the 180-day rate-application deadline runs from finalization of Commission regulations under section 203G. Section 317 likewise ties establishing the service classification to finalization of regulations. The bill page's original synopsis instead describes 180 days from the effective date; the final engrossment controls. Neither signing nor code publication proves that regulations are final or that utility tariffs/service agreements are implemented.

The in_force field is accepted here for statutory provisions based on signed/effective metadata and current official codification observed November 6. It does not assert implemented tariffs, completed rulemaking, an exhaustive later-amendment search, or the absence of all litigation. That narrower scope differs from the California chaptered laws whose ordinary effective dates remain in 2027.

## Evidence and acquisition limits

`answers.json` contains the reviewed changes; `baseline.json` pins all three existing rows. `review.json` records source-version hashes, exact quote checks, predecessor/substitute lineage and outstanding work. Raw bodies and provider exchanges remain in the durable private archive; public source manifests retain acquisition lineage and admitted official text.

The Exa query returned the official substitute, SB 312, the Governor's advisory and signing announcement, plus a news report. These leads do not establish absence of litigation or completion of rulemaking; no search-based negative finding is accepted. Eight bounded fetches were used, including one 404 caused by an incorrect zero-padded title09 path. The correct title9 county-code URL succeeded. The failed URL is retained as an acquisition failure, not evidence of a missing provision. One Exa search cost $0.007 in provider-reported charges.

This batch changes fifteen fields across three existing rows and adds no rows. The tracker remains 441 state-policy actions / 439 bills; enacted bills rise from 91 to 93. Local counts remain 1,293 instruments / 1,071 classified in force. Expanded ballot tables are unchanged. State-page inventory dates retain the November 5 cohort cutoff; this review does not renew other jurisdictions' freshness dates.

Validation: `make data site check` passed with zero errors and 282 existing data warnings; all 49 documented numbers match. Exact CSV comparison confirms fifteen field changes across the three intended rows. Replay proposes zero additional edits. A source-classification check after staging confirms no private source text is tracked. `validation.json` pins the completed build log.
