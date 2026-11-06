# Retained search provenance cohort audit

This offline audit checks an explicit list of 396 retained ledgers. It makes no new API calls, canonical promotions, current-force judgments or complete jurisdiction/time-coverage claims. The [machine report](search-provenance-cohort-2026-11-06.json) pins every ledger hash and the normalizer/generator versions. [Exceptions](search-provenance-exceptions-2026-11-06.json) are separate from verified searches.

| Measure | Verified scope |
|---|---:|
| Ledgers passing current verification | 384 |
| Verified ledgers containing searches | 361 |
| Unique search attempts | 4,109 |
| Original sightings | 22,863 |
| Recorded failed attempts | 253 |
| Successful zero-hit attempts | 31 |
| Reservations without terminal events | 3 |
| Unpriced attempts | 2,050 |
| Known priced subtotal | $14.014 |

The verified attempts comprise 2,002 Exa, 2,007 SerpAPI, 50 Google News and 50 GDELT reservations. No attempt ID appears in two verified ledgers. A successful zero-hit response is distinct from an error; neither proves no relevant measure exists. The three nonterminal ledger reservations are not independent evidence of a running or interrupted process and are not instructions to restart jobs.

Nine legacy ledgers contain 106 search reservations without recorded client-hash provenance; they are excluded from verified search totals. Three other ledgers contain only selected fetch terminal records and are excluded from search totals without inventing reservation history. The twelve exception ledgers are not silently discarded or treated as complete provenance. Verified fetch-only ledgers likewise do not contribute search attempts.

The priced subtotal excludes unpriced calls and all exception ledgers; it is not total campaign spend. Provider response hashes and returned ordering are verified where retained; this does not establish rank fusion, source independence or factual acceptance. Canonical search publication currently remains the bounded Jay cohort, not all audited searches.

Reproduce with `scripts/audit_search_cohort.py --root PRIVATE_ROOT --ledger-list PRIVATE_PATH_LIST --output REPORT.json`. The input-list SHA256 is retained; each relative directory and ledger SHA256 is public in the machine report. Normalization failures publish scoped reason codes and exception types, never raw exception text. Duplicate inputs, duplicate search IDs across ledgers and ledger changes during audit fail closed. Native regression tests cover these aggregate boundaries separately from actual corpus verification.
