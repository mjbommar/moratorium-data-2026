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

Preview makes no API calls or filesystem changes. Executing requires an explicit private directory and either an independently pinned priced contract or the existing explicit unpriced authorization. Unknown prices remain unknown. The priced phase described below adds a prospective search allocation; the historical unpriced runs retain their original accounting.

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

## Full worklist generator and version-2 execution

The [sparse worklist generator](sparse-refresh-worklists.md) now accounts for all existing local/state/ballot IDs plus independent state-sector discovery/election frames, while preserving missing host reviews and sector uncertainties. Its default preview selects the full explicit frame; optional tiny samples report every exclusion. New executions require plan version 2 and pinned authority-review files for domain filters. Version-1 artifacts retain historical preview/replay semantics under their pinned runtime and cannot start new runs. These changes supersede earlier implementation-only registry/worklist limitations for object accounting; comprehensive official-host review, query calibration and campaign budgets remain open.

## Optional priced discovery phase

A new phase requires explicit user approval through the coordinator; a contract and its hash are technical controls, not approval. The optional `--budget-contract PATH --budget-sha256 SHA256` must supply an independently recorded SHA-256 of the exact contract bytes. The contract pins the canonical plan hash and original caps, runtime commit and implementation hashes, non-secret settings fingerprint, pricing context and all phase limits. The review example is private and is not permission to execute. Runtime, configuration, plan, price or contract drift stops before creating a run directory or contacting a provider. New runs also require an empty directory; retained incomplete runs never restart.

The configured allocation is $0.007 per Exa Auto search with at most ten results and no requested contents, and $0.01 per Google SerpAPI search as a subscription allocation. The Exa adapter normally defaults to highlights; this priced path explicitly disables them. Text, highlights, summaries, Exa categories, other Exa modes and non-Google SerpAPI engines are rejected. A positive account pacing rate and the $0.01 configured SerpAPI rate are required in `BcWebSettings`; select and review pacing for the actual account. Pricing is a pinned input, not a live price check. Confirm applicable prices, availability, credits and account constraints before authorizing a phase.

The existing locked attempt ledger holds $0.02 before every search dispatch and never releases or refills it, including for successful, failed, interrupted and unknown-cost attempts. `bc_core.BudgetMeter` is reconstructed under the lock for each admission, with a $25 ceiling and 1,200 search attempts; original per-backend and total plan caps also apply. There are no LLM API calls in this path. One native `Searcher`, native response-cost meter and its backend limiter instances are reused across the cells; retries are disabled. The ledger is authoritative for holds; the native meter counts returned costs and can log an unpriced warning when Exa omits a price. It does not turn unknown costs into zero. Response costs, SerpAPI subscription allocation and holds are separate observations; invoice amount remains unknown. A returned cost above its hold stops further admissions for review; no local mechanism can retroactively limit an unexpectedly higher charge.

The same ledger optionally admits up to 500 source-fetch reservations, including at most 20 explicit pydoll browser reservations. Source collection requires a sealed search run, explicit HTTP mode first and a finished HTTP attempt for the same URL before browser mode. `auto` is rejected for this phase and fetch retries are disabled. Original source bytes and retrieval/body timestamps stay in private artifacts. HTTP and browser resource costs are separate from the search allocation and no zero invoice is asserted. The coordinator must enforce at most two simultaneous browser contexts across processes; this is not a persistent semaphore. Per-process searcher pacing is shared across cells, not a cross-process account quota; coordinate other clients separately. Calls through unrelated clients are outside this ledger.

Appending source attempts preserves the sealed search-ledger prefix for cached replay; source attempts remain in the same ledger and are not part of the original search seal. A crashed or incomplete run requires human inspection, including its ledger, and has no automatic retry. The phase provides no provider API extraction or model/review authorization; CLI model/review work remains `gpt-6.1-terra`. All amounts and call limits are prospective and do not relabel older unpriced runs.

The coordinator fixed the independent interrupted-seal finding: replay and priced source admission now share the same completed-seal, result-hash and retained-artifact/prefix verification. Empty or partial seals and changed search evidence reject before a fetch reservation. Appended source attempts remain outside the immutable search prefix. The prepared nationwide proposal passed 27 distinct offline tests (18 batch/budget, six legacy client and three sparse-worklist), without provider searches or authorization; see the [exact proposal](national-discovery-batch-2026-11-08.md).
