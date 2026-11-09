# South Dakota terminal-bill confirmation

Both assigned dispositions are **confirmed unchanged** for the named historical bills. No cell changes are proposed. The whole-row hashes below guard the supplied snapshots; they are not evidence that all 19 fields were independently verified, nor a live canonical-row check.

## Named bills

**SB 177 (2025).** The [official bill history](https://sdlegislature.gov/Session/Bill/25901) records adoption of 177D and failure of the amended bill 17–18 on February 13, followed by no motion to reconsider on February 18. Its rendered Sponsors section links Senator Wheeler and Representative Weisgram as prime sponsors. The [February 7 engrossed text](https://sdlegislature.gov/Session/Bill/25901/281290), section 2(2), limited substantial refurbishment to a 20-year period. The [adopted 177D HTML](https://mylrc.sdlegislature.gov/api/Documents/281678.html), section 2(2), strikes that phrase; extracted plain text alone obscures the deletion. The current provision accurately distinguishes the versions. The proposal was a refund incentive.

**SB 239 (2026).** The [official bill history](https://sdlegislature.gov/Session/Bill/27299) records committee do-pass amended 6–3 on February 18, floor failure 17–16 on February 23, and failed reconsideration 16–17 on February 24. Its rendered Sponsors section links Senator Crabtree as prime and Senator Schoenfish. The [February 19 engrossed proposal](https://sdlegislature.gov/Session/Bill/27299/304007), sections 1–2, includes data centers in projects, excludes cryptocurrency-attributable data processing, storage, retrieval or communication costs, and provides a direct payment permit pathway and qualifying future equipment upgrades for up to 30 years. These are proposed incentive provisions.

The bill-page body contains sponsor links that the extracted action text leaves blank. The four rendered profile headings identify the session year and their Party fields say Republican. All rendered body and extracted full-text hashes were independently checked against the normalized receipts. The HTTP-only counterparts are application/noscript shells and do not establish party. Capture on November 9, 2026 is distinct from the 2025 or 2026 session represented by each profile and from the legislative event dates.

| Profile | Session | Observed UTC | Body SHA-256 | Text SHA-256 |
|---|---:|---|---|---|
| [Senator David Wheeler](https://sdlegislature.gov/Legislators/Profile/4679/Detail) | 2025 | 2026-11-09T15:51:44.071713Z | `0f2cc25222a55fe7a919bc36fabd5d51cc06579f838b35c8a6e4c6ffc6757bc5` | `c1a895955f6ae5da14ed0cb257b778e0ee7763814f4d8f5428e67d7185d389e2` |
| [Representative Mike Weisgram](https://sdlegislature.gov/Legislators/Profile/4678/Detail) | 2025 | 2026-11-09T15:52:55.317924Z | `5a7f58d7eaa5d2b7f219e63abf7ad74a9be54c2014e24f7ccddae0f4617ffefb` | `a3b82afb8f7c90913b17a8ff2722277b0c5439ec87fecafa8d979f371fef33c9` |
| [Senator Casey Crabtree](https://sdlegislature.gov/Legislators/Profile/4741/Detail) | 2026 | 2026-11-09T15:53:05.694481Z | `8b173dc954095967c7d88797ba30eb1a04074f18392c8a88f5a12085f1f7c482` | `3650797ff56db77d0c63d7a17c732a2a2e5456c9c2d69723fa1894f5c407234b` |
| [Senator Kyle Schoenfish](https://sdlegislature.gov/Legislators/Profile/4817/Detail) | 2026 | 2026-11-09T15:53:07.970563Z | `074b420edfc6d63d7c9731f76a689130cd2e63b2538e34df24a62ff0c10f7bfb` | `0df2590163798c4dd3d801955cb771eb039b91ed9b8b123cbc621811fd083ffc` |

## Source checks and boundaries

All five assigned bill-source bodies and their extracted texts matched the supplied SHA-256 values. Acquisition times are UTC; legislative event dates are identified separately above. Locators refer to the retained versions, not a claim about a later site state.

| Source | Body SHA-256 | Text SHA-256 | Acquired UTC | Locator |
|---|---|---|---|---|
| [Official source](https://sdlegislature.gov/Session/Bill/25901) | `4ce6faffd7e8887feaae25445f80394f71f7162cd5cbbe7ea948ca9ab0073f07` | `9f2392567479476477350758c2f66d1c3b399d3d9288d5ed373a1293baf802de` | 2026-11-06T00:19:17.086211Z | legislative action table: February 7-18, 2025 |
| [Official source](https://sdlegislature.gov/Session/Bill/25901/281290) | `4b33d1001bc25da536ef8b3f188a35b47a028ba52633c0355df246fe3e89c67e` | `976805d5f7dbc4c33ed798a77c14f34a2a4b647dd617a744f9c83d50909d1b85` | 2026-11-06T00:20:10.505472Z | Senate Taxation engrossed sections 1-2 |
| [Official source](https://mylrc.sdlegislature.gov/api/Documents/281678.html) | `fea289baf439d3ad38d95e2797b42b5032e17bbf58f8f1b9ee7b63e7157fa93d` | `8baa7dc95e8703cfab9ccc56bdd265d9d0d4e3ead453731de82a62156048a225` | 2026-11-06T00:22:40.418144Z | amendment 177D, section 2(2), inspect HTML strike element around twenty-year phrase |
| [Official source](https://sdlegislature.gov/Session/Bill/27299) | `4ffd65fa4d6f21403b1d95251fd04b08639eb693558d362a9b32612f038e9c77` | `08da7509085f459b3893f14522f7f54595db6bd67f154e89118253d0d4537b7d` | 2026-11-06T00:20:35.238895Z | bill history action table |
| [Official source](https://sdlegislature.gov/Session/Bill/27299/304007) | `0b104dabd3239cb18aa4062d54702e846321f0301d3681962347494cd41681e0` | `1935b7747398953c600b46f98cabaadece9f882e1f0d4ec3b99035eb8e55da92` | 2026-11-06T00:21:33.314671Z | Senate State Affairs engrossed sections 1-3; project and project-cost definitions |

Snapshot guards: SB 177 `d0446ae73fbf6b36f63575c4eabec9d155c729fad571fb622acabd70cba8c2e7`; SB 239 `a2f6a858ffa7b54f2f8ccbc2df79a815ae8ada8f14e761b3ad3369fb7daa1de2`. Sorted-key compact JSON hashes were recomputed from the assigned snapshots. The performed review covers named sponsors and party, terminal actions, and material proposal claims, reusing the actual prior primary and independent reviews; it does not independently verify every guarded cell.

The formerly generic named-record uncertainty can be removed because the rendered bill pages identify the named sponsors, the matching session profiles supply party, and the dated histories and actual proposal texts support the outcome and material provisions. There is no remaining question about those reviewed named-record claims. This does not resolve other instruments, successor laws, or current law. State activity **Medium** is a qualified statewide aggregate and was not independently reassessed here; the rows’ **Low** values are separate from that aggregate and were not changed.
