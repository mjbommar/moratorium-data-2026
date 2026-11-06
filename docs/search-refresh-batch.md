# Sparse multi-provider refresh search

`scripts/search_refresh_batch.py` combines explicit bc-spec cells with native bc-web `Searcher.search_many`. It performs read-only research transport and produces private review artifacts. It does not promote domain facts, allocate canonical object IDs or establish legal force.

## Plan and preview

Each versioned plan contains a bounded registry, explicit cells, named provider variants, a sampling policy with seed, per-provider/total call caps and an explicit unpriced-call policy. Registry entries preserve government labels/aliases and source-backed official hosts. Unknown hosts and jurisdiction coordinates fail validation. This is a reviewed input contract, not a completed all-jurisdiction registry or automatic host-discovery process.

Cells specify lane (`inventory_refresh`, `election_census`, `gap_discovery`), jurisdiction, sector, period, intent and known-object context. All five existing sectors remain available. Native bc-spec `Space`, `Point`, `check`, `sample` and `estimate` provide stable coordinate identities, seeded selection and transparent estimates. Only explicit sparse cells are sampled; the full Cartesian product is never expanded. Preview reports selected cells, exclusions, provider counts and unknown prices. A period label is not a legal-event-date filter. Explicit SearchQuery dates constrain publication only; undated official-page recovery remains possible.

Known-object contexts still require explicit identity review against current inventories/registries. The Jay pilot used a human search-context label; its validation packet records the actual canonical measure UUID without allocating a new ID or alias. Full closed-object validation and automated worklist generation remain open.

Use the bc-modules interpreter:

```sh
BCPY=/home/mjbommar/projects/bc/bc-modules/.venv/bin/python
"$BCPY" scripts/search_refresh_batch.py work/research/2026-11-06/search-batch-jay/plan.json
"$BCPY" scripts/search_refresh_batch.py reviewed-plan.json --execute /data0/moratorium-refresh-2026/EXPLICIT-NEW-RUN
```

Preview makes no API calls or filesystem changes. Executing requires an explicit private directory and unpriced-call authorization. Unknown prices remain unknown, never zero-priced totals. Call caps do not constitute a complete dollar budget. Whole-run/per-stage dollar accounting, current account-specific SerpAPI pricing and broader campaign controls remain open.

## Transport, provenance and recovery

Named Exa semantic and Google exact/domain queries run through native `search_many`, native URL normalization and reciprocal-rank fusion. Original per-variant responses and every original sighting are retained alongside fused URLs/scores/ranks and marginal contributions. Retrieval agreement is not independent source corroboration or legal acceptance.

A small context-tagging override wraps the pinned native `_metered` method solely to associate response callbacks with concurrent variants, including two variants on the same backend. Native search, parsing and fusion remain library code. Relevant implementation file hashes and the bc-modules commit are pinned. Revalidate this private integration point when upgrading the library.

Before transport, the adapter creates an exclusive run marker and persistent reservations through the existing research client. Provider retries and throttle retries are disabled. Response callbacks retain body hashes and redact actual configured credentials before storage. Raw exception messages are discarded in favor of error types. Provider failures preserve their reservations and response exchanges. The final adapter emits per-variant response files and the existing normalizer's query/window/exchange-ledger format; the real Jay cohort passes `normalize_search_provenance.py` offline.

Completed runs have a sealed result and hash inventory. Exact cached replay verifies plan, runtime, response/body and ledger hashes and spends nothing. An unfinished retained run stops for inspection; it never restarts because an observer timed out. A runtime change requires explicit retained-result review. This implements bounded local replay, not the remaining independent full-store restore or end-to-end maintenance gate.

Coverage distinguishes returned hits, completed zero-hit queries, declined index windows and backend errors. Domain diagnostics retain out-of-scope URLs rather than silently dropping them; `query_scope_status` exposes scope mismatches separately from transport completion. Neither successful transport nor an empty response establishes complete coverage or absence.

## Actual bounded runs

- [Seattle](../work/research/2026-11-06/search-batch-seattle/): Exa returned five official-host URLs; Google returned five unrelated/outside-host URLs. The explicit one-call single-host repair returned zero hits. The deficient query and repair remain separate; no later-history/absence conclusion is accepted. These initial prototype runs predate the final per-variant normalizer-compatible response files; their exact runtime hashes remain pinned rather than retroactively rewritten.
- [Jay](../work/research/2026-11-06/search-batch-jay/): two providers returned six sightings, all on the declared town host. Native fused ranks, original responses and body hashes are retained; offline normalization and exact cached replay pass. The follow-up HTTP warrant landing returned 404. Actual pydoll/bc-web rendered the notices page, which contained an unrelated hiring notice, not the requested primary return. Only the stated endpoints were checked. Primary return/certification, passage rule and operative-law gaps remain open.

Together these are five search calls: two Exa and three SerpAPI, with a known Exa subtotal of $0.014 and three unpriced SerpAPI calls; this is not a campaign total. Two further source fetches include one actual pydoll browser call. Source bodies, snippets and network payloads remain private. Canonical local/state CSVs and expanded publication are unchanged.

Nine behavioral tests cover native shared-URL fusion, original sightings, normalizer compatibility, concurrent same-provider exchange attribution, credential redaction, failed-versus-zero-hit outcomes, index-window decline, domain mismatch retention, persistent caps, incomplete-run stops, cached replay, tamper rejection and seeded three-lane exclusions. This does not substitute for the broader P4 calibration gate.
