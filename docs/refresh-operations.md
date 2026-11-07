# Refresh operations

Work from a pinned commit and retain the cohort cutoff separately from the date
of an individual source review. Research jobs are not a substantive acceptance gate.

## Due work

Run the ballot worklist without network or model calls:

```sh
python3 scripts/build_ballot_due_work.py --today 2026-11-06 \
  --output work/audit/ballot-due-work-2026-11-06.json
python3 scripts/build_worklist.py --today 2026-11-06 --pretty
```

Ballot rules use exact election days only. The default qualification lead is 30
calendar days; post-election collection starts the following day. These are
operator priorities, not statutory deadlines. Current result observations exclude
explicitly superseded observations. Uncertified current observations require a
certification/correction check. Non-advisory measures require separate implementation
review; no outcome or operative law is inferred. Re-running this report does not
mark a task completed or renew source dates. Resolve tasks through evidence review
and canonical correction/publication, then regenerate from the new snapshot.

The seven unresolved frozen candidates remain in the separate ballot disposition
ledger. The legacy worklist handles expiry, unknown extension anchors, stale pending
records and verification markers. Its date alerts are research prompts: verify the
actual effective-date anchor, calendar term and later actions before changing status.

## Acquisition and interruption

Use a bounded `scripts/research_client.py` directory with persistent caps. Preserve
its ledgers, original bodies/text, failed attempts and separately registered reviewed
derivations. Inspect terminal status and the same process handle after an observation
timeout; do not restart a job merely because output observation expired. Original
November jobs are all terminal and should not be rerun as a collection recovery step.
Raw source copies remain private; public hashes and review excerpts follow the
source-tracking policy. Do not promote a CAPTCHA response or search snippet as a
successful primary acquisition.

## Conditional HTTP recrawl

Use `fetch --mode http --conditional-cache` for static source URLs in a bounded
job. The client uses bc-web's native private cache with zero TTL, origin
revalidation on every call and a 100 MB size cap. A repeated request still consumes
its fetch reservation. HTTP 304 can materialize an earlier 200 body; the ledger
separately records `from_cache`, `revalidated`, origin attempt statuses and the
original `body_observed_at`. Do not turn cache reuse into a fresh factual acceptance.

Archive versions remain immutable when body/text hashes are unchanged; new
acquisition observations remain in the attempt ledger. New archived cached versions
retain body-observation/cache metadata. Dynamic browser portals require their own
render/API review and cannot use this HTTP-only option. The [live pilot](../work/research/2026-11-06/conditional-cache-pilot/README.md)
verified a 200/304 round trip without changing canonical facts. Due-work rules and
source-specific decisions determine when to recrawl; no schedule is installed.

## Adaptive revisit proposals

Run `scripts/build_adaptive_revisit_plan.py` with the bc-modules Python environment,
repeatable `--directory` job paths, a timezone-aware `--as-of` timestamp and an
`--output` JSON path. It verifies retained bodies and uses native bc-web
`recrawl.estimate_rate` and `interval_for`, keeping HTTP/browser variants separate.
Failed acquisitions and future observations cannot count as unchanged visits.

Optional `--event-due FILE` maps URLs to timezone-aware ISO review times. These
operator priorities can shorten, never postpone, native due times; they are not
inferred statutory deadlines. Reports pin input and native-policy hashes and
sanitize signed retrieval URLs. The retained
[pilot](../work/audit/adaptive-revisit-pilot-2026-11-06.json) uses the actual two-fetch
conditional-cache ledger. This is an advisory offline planner, with no network
calls, installed schedules, task resolution or canonical factual updates. The
pilot does not establish inventory-wide policy calibration or legal freshness.

## JavaScript portals and JSON endpoints

For a bounded job, `fetch --mode browser --settle-ms 5000 --record-network`
retains subrequest metadata in the private payload. Follow the actual GET/POST
method and URL rather than guessing document paths. Network metadata identifies
leads; it does not retain or authenticate the response body. Acquire a useful
endpoint separately through the bounded client and pin that response's own hash.
Keep credentials, cookies and provider payloads private.

A rendered “Loading” view is incomplete evidence even if HTTP status is 200.
Likewise, an empty client text extraction from JSON does not mean the response
body is empty. Parse the retained body, validate the shape, and register any
reviewed text/projection separately against its exact body hash. State the filter
and retained subset; missing entries in an observed catalogue are not proof of
absence from law or the underlying universe. The [New Jersey portal review](../work/research/2026-11-06/nj-chapter-portal-review/README.md)
exercises this path and preserves the unresolved chapter discrepancy.

## Restore and release preparation

### Legacy source archive bridge

`scripts/bridge_legacy_sources.py --output PRIVATE_REPORT.json` inventories all
legacy manifests, preserving manifest/line fingerprints, original URLs and hashes,
retrieval times, publication flags and extraction lineage. It verifies retained
files before proposing imports. Missing original bodies remain explicit gaps;
an expected hash does not make a payload available. Historical missing filenames
do not by themselves establish that a source never existed or that a later source
version is missing.

After the storage preflight, add `--store PRIVATE_STORE --apply` to replay eligible
versions into native bc-store. Keep active SQLite on admitted local NVMe, route
`blobs` through the existing external-storage layout, and retain all material
privately. Original source rights flags are metadata, not permission to publish
the store. Exact manifest lines are retained as separate metadata derivations;
text variants have hash-specific producers. Shared native source/kind/time
identities may share one observation only when the body hash agrees. Conflicting
bodies, invalid timestamps and asserted-text drift require review.

The [November bridge receipt](../work/audit/legacy-source-migration-2026-11-06/validation.json)
records 6,455 manifest entries, 2,756 verified-body imports and 3,699 explicit body
gaps. Two extraction versions share a native observation, giving 2,755 observations.
Replay is identical and original manifests are unchanged. The retained SQLite
backup covers metadata; it is not an independent full-blob restore. Importing
bytes does not renew facts, establish current legal force, complete extraction or
change any publication flag.

The [post-discovery delta](../work/audit/legacy-source-migration-post-discovery-2026-11-06.json)
adds 24 private MA/WI source versions without changing earlier mapping entries.
That checkpoint's manifest inventory is 6,479 entries: 2,780 verified-body versions map
to 2,779 native observations, with the same 3,699 original-body gaps. The full
post-discovery replay is identical; its metadata backup is separately pinned.

The [Kent and body-recovery checkpoint](../work/audit/legacy-source-migration-kent-and-body-recovery-2026-11-06.json)
covers 6,485 entries and 3,042 verified-body versions. It adds six private source
versions and restores 256 missing compatibility paths using already-retained,
exact-hash CAS bytes. The [reviewed link plan and receipts](../work/audit/source-body-link-recovery-2026-11-06/README.md)
preserve original manifests, publication flags and existing links. Restored paths
are Git-ignored; they do not export source content or renew retrieval dates.

The [Brighton/Chicago delta](../work/audit/legacy-source-migration-brighton-chicago-2026-11-06.json) adds two previously collected official-announcement versions, bringing the current mapping to 6,487 entries and 3,044 verified-body versions. It preserves original acquisition dates and verifies native payload readback.

The 3,443 remaining gaps mean no matching body through the manifest-listed paths,
not proven global payload loss. They include 119 failed acquisitions without a
recorded body hash. Other private stores have not been exhaustively searched.
Recovery of a body is separate from authentication, extraction completeness,
substantive source acceptance and legal force.

For a mixed-state acquisition directory, `archive_research_attempts.py --attempt-id`
can explicitly route selected successful original attempts to the correct state.
Repeat the flag for multiple IDs. Unknown/failed IDs reject the selection before
archive writes; original acquisition ledgers remain unchanged. Omit the option
only when the complete successful-fetch set belongs in that archival scope.

### Distributed discovery review

The November 6 discovery review uses explicit frozen queues under
`work/jobs/2026-11-06-discovery-review/`. Original collection jobs are not rerun.
`scripts/audit_discovery_reviews.py` verifies candidate fingerprints against
original answers, exact retained source versions and quote offsets, schema shape,
and complete disjoint return coverage. It counts a verified failed acquisition as
failure accounting, never positive source evidence. Reused pilot artifacts require
an explicit pinned artifact manifest and coordinator-supplied aliases.

Use `--baseline-inventory` to inspect the retained frozen CSV after canonical
changes; otherwise the audit checks the current CSV and reports baseline drift.
The [review receipt](../work/research/2026-11-06/discovery-distributed-review/validation.json)
pins the original baseline commit. Missing assignments in initial partial returns
remain visible even after separate smaller jobs cover them. Model recommendations,
located text and body-only visual assertions remain separate from coordinator
acceptance and canonical promotion.

### Release candidate preparation

`scripts/build_release_candidate.py` builds public assets from a committed revision.
Its archive includes retained expanded generations and the relative `data/expanded`
pointer. Restore into a new empty directory with a symlink-aware extractor, retain
all generations, and verify every member against the manifest. The candidate is a
data bundle, not a complete source-code/runtime distribution; use the pinned source
checkout and its dependencies to rerun validators against the restored inputs.

A deterministic archive, successful build or local tag does not prove publication.
Verify remote branch/tag targets, GitHub Release metadata, downloaded asset hashes
and hosted-page bytes separately. Historical paper/consumer editions keep their
own cutoffs. No schedules are created by this workflow.

The [Iowa review checkpoint](../work/audit/legacy-source-migration-iowa-review-2026-11-06.json) verifies six selected original PDF fetches, three already archived and three newly imported versions. The full native readback covers 6,490 entries, 3,047 verified-body versions and the same 3,443 listed-path gaps. Twelve rendered pages were independently reviewed; source authenticity, later legal actions and factual acceptance remain separately scoped.

The [Illinois action checkpoint](../work/audit/legacy-source-migration-illinois-action-2026-11-06.json) adds five source versions (three retained prior sources and two freshly acquired official records). Full native payload/manifest readback covers 6,495 entries and 3,052 verified bodies; the 3,443 listed-path gaps are unchanged. Fulton full-board approval and Tilton minutes narrow source-stage findings without establishing operative anchors or complete later histories.

The [NM/MT/OR source checkpoint](../work/audit/legacy-source-migration-nm-mt-or-2026-11-06.json) adds six previously collected versions. Full native readback covers 6,501 entries and 3,058 verified-body versions, with 3,443 listed-path gaps unchanged. Silver City’s original event-based solar endpoint remains unresolved despite its explicit 2026 repeal; archived evidence is not a continuous-force finding.

The [Washington notice/utility checkpoint](../work/audit/legacy-source-migration-wa-review-2026-11-06.json) adds three retained versions and verifies the full native mapping: 6,504 entries, 3,061 verified-body versions, 3,443 listed-path gaps. The unsigned Chelan PUD confirming text is not proof of execution or the City of Chelan land-use instrument.

The [Tennessee review checkpoint](../work/audit/legacy-source-migration-tn-review-2026-11-06.json) adds four retained versions and verifies full native body/manifest readback: 6,508 entries, 3,065 verified-body versions, 3,443 path gaps. The Orlinda PDF extraction omits page 1; complete two-page visual review independently supports the newly added record without claiming complete text extraction.

The [Texas review checkpoint](../work/audit/legacy-source-migration-tx-review-2026-11-06.json) verifies five original source pairs and adds four archive versions (one matching body already retained). Full native readback: 6,512 entries, 3,069 verified-body versions, 3,443 path gaps. Visual review covers ten listed pages, not every attachment.

The [Rhode Island checkpoint](../work/audit/legacy-source-migration-ri-review-2026-11-06.json) adds six retained source versions and verifies full native readback: 6,518 manifest entries, 3,075 verified-body versions and 3,443 listed-path gaps. Six candidate recommendations share five HTML reports and one two-page draft; candidate count is not independent-source count.

The [Idaho checkpoint](../work/audit/legacy-source-migration-id-review-2026-11-06.json) adds five retained versions and verifies full native readback: 6,523 manifest entries, 3,080 verified-body versions and 3,443 listed-path gaps. Visual scope is Gooding pages 1–2 of five and all three Blaine pages. A planning deadline is not automatically a moratorium duration.

The [Kansas checkpoint](../work/audit/legacy-source-migration-ks-review-2026-11-06.json) adds six retained original versions and verifies full native body/manifest readback: 6,529 entries, 3,086 verified-body versions and 3,443 listed-path gaps. The separately registered Jefferson OCR is hash-verified by the review; its new native-store import is not claimed.

The [NE/UT/WY checkpoint](../work/audit/legacy-source-migration-ne-ut-wy-2026-11-06.json) adds five retained versions and verifies native readback: 6,534 entries, 3,091 verified-body versions, 3,443 listed-path gaps. Sarpy’s signatures require visual proof because extraction missed them; generated-summary dates and page-interface dates are not event anchors.

The [North Dakota checkpoint](../work/audit/legacy-source-migration-nd-review-2026-11-06.json) adds four retained source versions and verifies full native readback: 6,538 entries, 3,095 verified-body versions and 3,443 listed-path gaps. Five recommendations rely on four distinct sources; Bowman’s shared article does not prove separate instruments or independent support.

The [current coordinator accounting](../work/audit/discovery-coordinator-accounting-2026-11-06.md) reconciles 185 candidates: 38 additions, one covered instrument, 146 reviewed withheld and zero awaiting review. The helper pins 30 packets, checks 179 explicit candidate fingerprints and re-verifies 185 original/followup versions; four pilot versions are independently verified in the Maine packet. Six alternate-layout candidates retain scope limits. Mechanical accounting is not legal acceptance.

The [Minnesota checkpoint](../work/audit/legacy-source-migration-mn-review-2026-11-06.json) adds six retained versions and verifies full native readback: 6,544 entries, 3,101 verified-body versions and 3,443 listed-path gaps. Ten PDF pages were visually inspected; city staff reporting remains distinct from operative text.

The [Maryland/New Jersey checkpoint](../work/audit/legacy-source-migration-md-nj-review-2026-11-06.json) adds six original retained versions: 6,550 entries, 3,107 verified-body versions and 3,443 listed-path gaps. All seven PDF pages were visually reviewed; Talbot’s registered OCR remains separate from its empty original extraction. Two source-scoped additions preserve every prior row. Full freshness, archive/extraction, consumer and final-release gates remain open.

The [Colorado checkpoint](../work/audit/legacy-source-migration-co-review-2026-11-06.json) adds seven distinct original retained versions: 6,557 entries, 3,114 verified-body versions and 3,443 listed-path gaps. All eleven PDF pages were visually reviewed; two Phillips County histories share an extension date but remain separate instruments. Alamosa/Rio Grande share one article, counted once. Printed Fort Collins passage/effectiveness remains unverified final action.

The [Indiana checkpoint](../work/audit/legacy-source-migration-in-review-2026-11-06.json) adds seven distinct original retained versions: 6,564 entries, 3,121 verified-body versions and 3,443 listed-path gaps. All eight PDF pages were visually inspected; the two additions are source-stage proposals, not enactment findings. Blackford R9/R10 remain distinct leads with one shared automated source.

The [Alabama/Georgia checkpoint](../work/audit/legacy-source-migration-al-ga-review-2026-11-06.json) adds nine distinct original retained versions: 6,573 entries, 3,130 verified-body versions and 3,443 listed-path gaps. Seven PDF pages visually reviewed. Union’s empty original extraction is preserved alongside separately registered OCR; full native body/manifest-line readback is not full original-text extraction coverage.

The [Kentucky/Louisiana checkpoint](../work/audit/legacy-source-migration-ky-la-review-2026-11-06.json) adds thirteen distinct original retained versions: 6,586 entries, 3,143 verified-body versions and 3,443 listed-path gaps. Eight PDF pages visually reviewed, including only Washington page 14/34. Camargo’s source-stage adopted classification does not establish publication/effectiveness; Bossier’s historical original term does not exclude later action.

The [Massachusetts/Pennsylvania checkpoint](../work/audit/legacy-source-migration-ma-pa-review-2026-11-06.json) verifies eleven selected retained originals, with six new archive entries and five existing correspondences: 6,592 entries, 3,149 verified-body versions and 3,443 listed-path gaps. Twelve coordinator cases withheld without CSV or expanded-snapshot changes. Town-meeting reporting and curative-amendment legal/model scope remain distinct followup requirements.

The [Carolina/Virginia checkpoint](../work/audit/legacy-source-migration-nc-sc-va-review-2026-11-06.json) adds twelve original retained versions: 6,604 entries, 3,161 verified-body versions and 3,443 listed-path gaps. Seven PDF pages visually reviewed; Greene scope is 3/46 only. Town-reported Mooresville approval remains separate from unsigned ordinance terms; Awendaw remains a source-stage proposal.

The [remaining-states preparation checkpoint](../work/audit/legacy-source-migration-remaining-states-preparation-2026-11-06.json) verifies seventeen successful original versions: twelve new entries and five already represented, for 6,616 entries, 3,173 verified-body versions and 3,443 listed-path gaps. One unsuccessful empty-text county homepage is excluded from the successful-fetch archive importer. The [review preparation](../work/research/2026-11-06/remaining-states-discovery-review/review-preparation.json) pins fifteen candidates, eighteen original body/text versions and 35 visually reviewed pages out of 166 retained pages. Three additions are prepared, twelve cases have proposed withholding reasons; canonical promotion and final ledger accounting remain pending. The official queue therefore remains fifty.

The remaining-states batch is now [dispositioned](../work/research/2026-11-06/remaining-states-discovery-review/review.json): three signed-record additions and twelve withheld cases. All 1,321 prior inventory rows are preserved. Current inventory: 1,324 records, 1,079 classified active/extended, 78 pending and 167 recorded past; 697 VERIFY rows and 34 missing reference points. Review preparation is historical; final ledger accounting reports 35 awaiting review. No new acquisitions or final release/deployment.

The [New York checkpoint](../work/audit/legacy-source-migration-ny-review-2026-11-06.json) verifies eight successful originals, seven new and one already represented: 6,623 entries, 3,180 verified-body versions and 3,443 listed-path gaps. All nine PDF pages inspected. Ten candidate dispositions add historical Niagara and proposed Massena; eight remain withheld for specific evidence requirements. All 1,324 prior rows preserved. Current discovery queue: 25 awaiting coordinator review; 126 reviewed withheld. No fresh collection or final release/deployment.

The [Michigan checkpoint](../work/audit/legacy-source-migration-mi-review-2026-11-06.json) adds nine verified original source versions: 6,632 entries, 3,189 verified-body versions and 3,443 listed-path gaps. All 29 PDF pages inspected. Nine dispositions add two historical Locke acts and Meridian township-reported BESS adoption, separate from its existing data-center act; six withheld with specific next requirements. All 1,326 prior rows preserved. Current queue: sixteen Maine candidates awaiting coordinator review, 132 reviewed withheld. No fresh collection or final release/deployment.

The [Maine checkpoint](../work/audit/legacy-source-migration-me-review-2026-11-06.json) verifies eleven successful original discovery versions, ten new and one existing: 6,642 entries, 3,199 verified-body versions and 3,443 listed-path gaps. Four pilot body/review-text versions are independently hash-verified in the packet, including separate Wells OCR and original Wiscasset HTML. Twelve complete discovery PDF pages plus three selected pilot pages inspected. Sixteen dispositions add Bridgton/Ashland historical terms, preserving all 1,329 preceding rows. All 185 frozen candidates are dispositioned; 146 remain withheld for explicit evidence requirements. Jay solar ballot is a separate primary-recovery lead, not a canonical publication. Full freshness/pipeline/copy/consumer/release gates remain open.

The [Jay recovery/promotion](../work/research/2026-11-06/jay-ballot-promotion/README.md) adds one separately reviewed solar measure outside the frozen 56 groups: current 50 measures / 50 current results / 56 retained results, still five certified current observations. Signed warrant/question, proposed petition clauses and placement minutes are distinct from secondary unofficial 1,464 / 723 counts and unknown operative law. Two Exa searches, one unpriced SerpAPI search and six fetches included a pydoll 404 and successful official-media reference chasing. Three recovered primary PDFs imported: 6,645 entries / 3,202 verified bodies / 3,443 listed-path gaps. No legacy CSV change, accepted current restriction, project join or final release/deployment.

The [site-link renderer review](../work/audit/site-link-render-review-2026-11-06.json) repairs 32 fictitious HTML destinations across four generated documents. Links now resolve against their source document and use only known generated outputs; unrendered research packets keep Markdown URLs. All 59 rendered pages and 953 local link references resolve to retained repository targets. Six regression cases and the full 187-test native suite pass. This is local-file verification, not hosted HTTP responses, anchors, refreshed source facts or final deployment.

Expanded CSV projections now derive all fifteen schema tables and a separate current-result view from one pinned reviewed generation. `data/expanded` remains authoritative; `data/expanded-csv` is an atomic relative pointer to a separately fingerprinted projection directory. The manifest pins source JSONL/publication/schema/exporter and every CSV hash. `make data` regenerates; `make check` detects file, pointer and download-link drift. Historical observations, separate reporting scopes and unknown values survive without inferred zeroes or new legal acceptance. Release selection includes projection generations and both portable pointers when present in the selected revision.

Search provenance review: `scripts/normalize_search_provenance.py PRIVATE_DIRECTORY` reads existing research-client ledgers without making API calls. It verifies successful response identities/counts and recorded provider-body hashes, retains original returned order/provider positions and separates zero-hit success, error, interruption and declined-window partial results. The Jay bounded recovery replay verified three responses and three provider exchanges, with the $0.014 priced subtotal and one unpriced call retained separately. All 200 native tests passed. This is review transport, not canonical search publication or complete coverage: legacy failed reservations lack query/window intent, and separate error-path exchange-ledger ingestion remains open. See `work/audit/search-provenance-adapter-validation-2026-11-06.json`.

Search error-path follow-up: the adapter now reads and hashes `exchanges.private.jsonl`, verifies retained error/interruption bodies and reconciles matching terminal copies without double counting. Conflicting copies, orphan events, duplicate artifacts and hash drift fail closed. New research-client reservations persist query/window intent before transport; historical missing intent remains unknown. Jay successful-response replay and failure/interruption regression fixtures pass with the full 204-test suite. This supersedes the preceding error-path adapter limitation; it does not close canonical publication, rank-fusion or coverage requirements. Receipt: `work/audit/search-error-provenance-validation-2026-11-06.json`.

The [Jay search provenance publication](../work/research/2026-11-06/jay-search-promotion/README.md) adds the first canonical search run: three retained attempts, eighteen original sightings and one explicitly partial coverage observation. Full existing claim/source/visual preflight, opaque identity allocation, immutable publication and exact replay passed. All eleven non-search/coverage JSONL tables remain byte-identical; both legacy CSVs remain unchanged. No new search calls, fused ranking, complete price, substantive source acceptance or exhaustive coverage is asserted.

The [retained search-cohort audit](../work/audit/search-provenance-cohort-2026-11-06.md) inventories 396 explicit ledgers: 384 pass current verification, containing 4,109 unique search attempts and 22,863 original sightings across Exa/SerpAPI/Google News/GDELT. It separates 253 recorded failures, 31 successful zero-hit searches, three nonterminal reservations and 2,050 unpriced attempts. The $14.014 known subtotal is not campaign spend. Nine legacy ledgers with 106 search reservations lack client-hash provenance; three fetch-only selected subsets lack reservation events. Exceptions remain separately accounted. No acquisition restarted, canonical cohort expanded or comprehensive factual coverage inferred by this audit.

A new [duration-encoding review queue](../work/jobs/2026-11-06-duration/queue.json) freezes 474 fixed-day rows whose original duration text mentions calendar months/years, across 39 states. Six disjoint 79-row `gpt-6.1-terra` CLI reviews use existing retained evidence only, with concurrency three and no new search/acquisition calls authorized for these jobs. This is new normalization review work, not a restart of the 333 completed acquisition jobs. Genuine original day counts, including originals followed by calendar extensions, must remain fixed-day; ambiguous original terms are withheld. Each recommendation pins the input row and whole inventory hash. The [dispatch receipt](../work/audit/duration-review-dispatch-2026-11-06.json) verifies the first three live Codex processes; recommendations require independent coordinator review and explicit conflict-safe application before any data change. No current-force renewal is implied.

All six duration-review jobs are terminal and 474 returns pass mechanical checks. Coordinator adjudication of the first 79 records applies 35 original calendar-term encoding corrections (70 fields), retains eight explicit-day originals and withholds 36; 395 coordinator reviews remain open. Exact replay changes zero rows. Every other local CSV value, both canonical ID sets, state-policy bytes and expanded canonical generation remain unchanged. Full 213 native tests and `make data site check` pass: zero errors, 321 warnings, all 53 documented numbers matched. The 29 added calendar-end warnings explicitly retain unknown current endpoints. Current field accounting covers 520 edited local records/1,799 matching last field values, with no drift. See the [review/validation](../work/research/2026-11-06/duration-encoding-review/README.md).

The second duration cohort independently adjudicates 79 more records: 36 encoding corrections applied, two explicit-day originals retained and 41 withheld. Cumulative coordinator accounting is 158 reviewed / 71 corrected / 10 retained / 77 withheld / 316 pending. Generated summaries, an incomplete Bullitt transcript, Waterloo’s explicit 90-day ambiguity and Collinsville’s stage identity are withheld. Exact 72-field changes preserve every other value; replay changes zero rows. All 36 newly converted active records retain blank current endpoints, exposing uncertainty instead of guessed day arithmetic. Source review is separate from status/date/current-force acceptance.

The third duration cohort applies 36 original-term encoding corrections, retains three explicitly stated original day counts and withholds 40 cases. Cumulative coordinator review is 237 reviewed / 107 corrected / 13 retained / 117 withheld / 237 pending. Later Pontiac, Saugatuck and Waterford documents support original six-month intervals separately from extensions; Gorham, Pittsfield and Saline city remain fixed-day. Ambiguous stages, pre-final drafts, stakeholder/generated summaries and Eagan’s insufficient original clause remain withheld. Exact 72-field changes preserve every other local value and all state/expanded data; replay changes zero rows. Twenty-eight additional calendar-end warnings retain blank current endpoints rather than guessed expiry arithmetic.

Third-cohort validation passes all 213 native tests and the full data/site check: zero errors, 384 warnings and all 53 documented numbers matched. Twenty-eight calendar-end warnings were added; one Waterford status-drift warning disappeared because its guessed 180-day original term no longer produces a September 19 expiry. No status or date changed. Current field accounting tracks 1,943 matching last-applied local field values with zero drift.

The fourth duration cohort applies 30 encoding corrections (60 fields), retains Pendleton’s explicit 180 days and withholds 48 cases. Cumulative coordinator disposition is 316 reviewed / 137 corrected / 14 retained / 165 withheld / 158 pending. Salina page 3 was visually reviewed to resolve extraction order; Cairo’s persistent 2025 ID is retained while its current legal basis matches the 2026 law. Colfax’s recording/effectiveness versus adoption anchor remains a separate named gap. Exact field comparison and replay preserve every other value and all state/expanded data. Twenty-six calendar-end warnings are newly exposed; Hartwick’s guessed-expiry drift warning disappears without a status/date change.

Fourth-cohort checks pass all 213 native tests and the full data/site check: zero errors, 409 warnings and all 53 documented numbers matched. The net 25-warning rise consists of 26 newly explicit unknown calendar endpoints minus Hartwick’s previously guessed-expiry drift warning. Current local field accounting covers 615 edited records and 2,003 matching last-applied field values, with no drift.

The fifth duration cohort applies 50 original reported calendar-unit corrections (100 typed fields), retains three explicitly stated original day counts and withholds 26 cases. Cumulative coordinator disposition is 395 reviewed / 187 corrected / 17 retained / 191 withheld / 79 pending. Durham city’s and Hillsborough’s 60-day originals and Waterville’s amended 182-day original remain fixed-day. Morgan Township’s generated summary is withheld. Camden’s explicit five-month reporting, Durham County’s official nine-month label, historical Hubbard interval and Sprigg voluntary interval are not promoted to new date/current-force/ballot conclusions. Every other row value and all state/expanded data remain unchanged; replay changes zero rows. Forty-one additional calendar-end warnings retain unknown current endpoints.

Fifth-cohort validation passes all 213 native tests and full data/site checks: zero errors, 450 warnings and all 53 documented numbers matched. All 41 additional warnings concern unknown current calendar endpoints; none supply a new expiry or change status. Current local field accounting covers 662 edited records and 2,103 matching last-applied field values, with no drift.

The frozen duration queue is fully coordinator-dispositioned: 474 reviewed / 230 encoding corrections applied / 21 explicit-day originals retained / 223 withheld / zero awaiting review. The final cohort applies 43 corrections, retains four specified day counts and withholds 32. Exact cumulative comparison against frozen revision db58d8c changes only 460 duration fields on 230 rows; all other values and IDs, including retained/withheld rows, are unchanged. The 223 source-fact requirements remain open. Cheney page 3 was visually reviewed. Two Seattle records cite the same ordinance, creating a separate identity/alias/consumer review requirement before unique-instrument freeze; normalization does not consolidate them.

Final duration-cohort validation passes all 213 native tests and the full data/site check: zero errors, 489 warnings and all 53 documented numbers matched. Exact replay recognizes 86 already-applied fields with zero edits. Across all cohorts the warning count reconciles as 292 prior + 200 newly explicit unknown calendar endpoints - three removed guessed-expiry drift warnings = 489. Local field accounting covers 703 edited records and 2,189 matching last-applied field values, with zero drift. Closure is specific to the frozen duration review; original-term source gaps, identity/freshness gates and final release remain open.

The [Seattle primary identity review](../work/research/2026-11-06/seattle-identity-review/README.md) confirms the two legacy rows identify one Ordinance127447/CB121214. One Exa call (known search subtotal$0.007), pydoll clerk landing-page acquisition (HTTP200/zero usable text), official legislative-summary PDF and Legistar history retain explicit provenance. Three PDF pages visually verify identity and stages; council vote9–0 differs from the emergency3/4threshold and committee5–0. Two usable documents imported and fully read back:6,647manifest entries/3,204verified bodies/3,443listed-path gaps. The exact-input identity preview proposes an existing-ID alias and projects1,330records only if applied; raw1,331rows, canonical data, counts and expanded publication are unchanged. Compatible alias lookup, field reconciliation and full consumer/count propagation remain open.

## Seattle identity application — November 6

The [reviewed retirement receipt](../work/research/2026-11-06/seattle-identity-review/retirement-validation.json) now supersedes the earlier preview-only checkpoint: 1,330 current local records, 1,079 classified active/extended, 1,289 geocoded and Washington 43. Both original rows and IDs remain in the append-only registry; all survivor fields are unchanged. Lookup, expanded references, retired-ID write rejection, core validation and release asset selection support the alias. Exact replay and interrupted-transaction recovery are tested. This is an identity-only correction, not reacceptance of survivor project prose or renewed current legal force. Final downstream snapshots remain open.

## Bounded native search-many adapter and closeout review

[Search adapter documentation](search-refresh-batch.md) records explicit sparse bc-spec cells, seeded preview, native provider variants/fusion, original sightings, body/response hashes, exchange attribution, persistent call caps and sealed no-spend replay. Two new terminal `gpt-6.1-terra` closeout reviews audited 43 checklist items; coordinator reconciliation adds the omitted Jay item and verifies 67 evidence hashes. Workers made no API calls or repository edits. Root ran five searches (two Exa/three SerpAPI; known subtotal $0.014 with three unpriced calls) and two Jay fetches including actual pydoll. The initial Google Seattle branch returned unrelated/outside-host hits, its explicit single-host repair returned zero, and Jay primary return remains unrecovered after the two stated endpoint checks. Raw bodies remain private; no canonical data or legal conclusions changed. These runs are outside the prior 396-ledger search cohort. Whole-run dollar budgeting, calibration and final publication remain open.

## Retrospective pilot contracts and El Dorado field evidence

The [seventeen-case pilot review](../work/research/2026-11-06/pilot-contract-review/README.md) pins nine canonical case groups, three source-review cases and five labeled artificial examples. It checks 23 explicit expectations, twelve selected measures and March/November cohort separation. This is retrospective: the original before-tuning/before-implementation order was not met, and no independent holdout/accuracy or full quality gate is claimed. A retained-source recheck verifies all 511 baseline claim bindings with no version errors.

El Dorado’s existing three-sector value is supported by the proposed definition, but the old field decision cited the shorter notice. The [applied correction](../work/research/2026-11-06/el-dorado-sector-lineage/README.md) adds one directly visual-supported claim and two decisions, superseding only that field decision. All prior records/field values and both legacy CSVs remain unchanged. Expanded totals are fifty measures, 56 retained/50 current result observations, five current certified observations, 141 source documents, 512 claims and 2,334 review decisions. Full evidence preflight/application and exact replay pass; no new source/API/model calls or legal-force conclusions occur. The fixture baseline retains its original finding, linked to the later resolution rather than rewritten.

The qualification regression now rejects accepted enactment links from disqualified/withdrawn/canceled measures while retaining historical proposal links. Independent holdout, discovery/extraction metrics, disagreement/spend reporting, real predecessor history and remaining source/legal facts still require completion.

## First frozen multi-document domain extraction evaluation

The [three-document extraction evaluation](../work/research/2026-11-06/frozen-domain-evaluation/README.md) committed its source/settings/thresholds and twelve-slot checklist before calls. Actual bc-evidence/domain extraction processed nine supplied-text chunks, made ten accounted successful gpt-6-sol backend calls and produced 36 schema-valid, exactly located candidates. Source-based coordinator adjudication fully supports32and retains4ambiguities;11/12requiredslots match. The 95%support gate is not met and none of three source documents is review-ready. Two independent gpt-6.1-terra CLI reviews cover all candidates/slots and agree on35/36labels; this is AI agreement, not truth. Successful-call estimated usage cost$0.2375234 and backend reservations are recorded separately from the intended provider-request ceiling; CLI spend remains unknown. Cached replay makes no calls. Canonical inputs are unchanged and no candidates are promoted. Historical source familiarity, post-extraction rubric operationalization and unmeasured discovery/false-exclusion rates remain explicit.

The evaluation also exposed a transport-accounting gap: bc-llm max_attempts1does not disable the installed OpenAI SDK default of two retries. Ten accounted backend calls and their successful-call estimated usage costs are verified; actual provider HTTP-attempt count is not captured. The intended thirteen-provider-request limit is therefore unverified, not known exceeded. Backend reservations stay within their recorded limits, while failed/retried provider charges and CLI spend are not a complete invoice. Strict transport retry/attempt controls must be fixed before claiming a provider-level cap. See [SDK audit](../work/research/2026-11-06/frozen-domain-evaluation/sdk-retry-audit.json).

## Advisory mechanism and count-scope correction

The [applied semantic-lineage packet](../work/research/2026-11-06/ballot-semantic-lineage/README.md)
closes five explicit field-evidence tasks after coordinator review of nine PDF
pages and two distributed `gpt-6.1-terra` source-image reviews. Four advisory
mechanisms retain their values with direct claim support. Wrightstown retains
the proposed infrastructure/service and within-or-affecting qualifications;
Bloomington restriction territory becomes unresolved. An immutable Monterey Park
successor records final city-total count scope while preserving all counts and
the separate county/city certification phases. Earlier observations and decisions
remain unchanged. Three pre-application preparation/receipt issues were caught
and resolved before canonical publication.

Current totals: 50 measures, 57 retained/50 current result observations, five
current certified observations, 141 sources, 523 claims and 2,369 decisions. Both
legacy CSVs are unchanged. Full evidence preflight/application verifies 523 claim
bindings; exact replay is a no-op. All 263 tests and 42 subtests pass; the complete
data/site/check build passes with zero errors, 489 existing warnings and 53
matching audited numbers. The post-correction targeted audit has no current-use
flags; its historical predecessor gaps remain visible. This does not complete
the extraction evaluation, broader freshness/implementation gates, final release
or hosted/sibling delivery.

## First source-supported instrument-event migration

The [five-event cohort](../work/research/2026-11-06/instrument-event-migration/README.md)
publishes three signed adoptions and two explicit immediate-effect events for
existing Stephenson, Whitman and Spokane Valley instruments. Stephenson actual
effectiveness and all three later histories/current force remain unresolved.
No expiry is inferred from an original endpoint. All prior records and both
legacy CSVs remain unchanged; there are still 1,330 local records, 442 state-policy
records, 50 measures, 57 retained/50 current results and five certified current
observations. Expanded sources/claims/decisions now number 144/528/2,394, with
five instrument events.

Two distributed terra CLI reviews checked source images and initial contracts.
Coordinator fixes preserve historical validation profile1.0.0 while new event
plans pin profile1.0.1 and require exact accepted event claims cited by the
instrument/action/occurrence field decisions. Complete source preflight/application
verifies 528 claim bindings; replay is a no-op. All 272 tests and 44 subtests pass,
as do the frozen seventeen-case audit and full data/site/check build. Existing
489 warnings and legal qualifications remain. Broader migration, freshness,
extraction-quality and final publication/deployment gates are still open.

## New Jersey remaining-worker review

The [three-record follow-up](../work/research/2026-11-06/nj-policy-wave2/README.md)
applies fifteen fields after review of seven retained source versions and two
distributed terra source reviews. It replaces S4293's unsupported final-death
claim with its documented conditional-veto action and unknown legal effect;
qualifies S3611's SPC timing/default and subsidy limits; and separates A1170's
conditional plan/supply requirements from its connection clause and companion
synopsis. All stable IDs and other values are preserved. No revival, enactment,
BPU finding or current-force conclusion is inferred.

One fresh bc-web chapter-catalogue invocation, using the final retained allowance,
reproduces the earlier body hash; signed Chapter75 remains unrecovered. Three
separately decoded Windows-1252 text versions and that refreshed observation add
four archive versions. Native bc-store readback verifies the 62 eligible NJ
manifest rows while thirteen older missing-body gaps remain. This does not make
the catalogue a complete law census. All headline totals are unchanged; one
`failed_died` category moves to `vetoed`, with legal effect unknown. Full build,
272 tests/44 subtests and zero-edit replay pass. Broader state review,
implementation, final release and delivery remain open.

## Seattle survivor field reconciliation — November 6

[Seven narrative corrections](../work/research/2026-11-06/seattle-survivor-reconciliation/README.md) distinguish original passage/effectiveness, the qualifying operating-facility expansion exception, original term and separate Attachment A deadlines. A terminal `gpt-6.1-terra` CLI review verified both retained body/text pairs and requested restoration of the definition's primary-use condition and source-specific support attribution; both were corrected before application. Coordinator visually reviewed four original PDF pages. No new network calls, IDs, classifications or operative endpoints; project aggregates/applicability and current-force questions remain qualified. Both prior rows remain preserved in the identity registry. Final consumer reconciliation remains open.

## Full object worklists — November 6 planning cutoff

The [native sparse generator](sparse-refresh-worklists.md) accounts for 1,330 local IDs, 442 state-policy IDs and 50 measures plus two separate 250-item state-sector exploration frames. All 2,713 explicit cells are selected by default; the optional three-cell sample reports 2,710 exclusions. Sector-neutral state-policy recovery, original sector translations and missing host reviews remain visible. Two terminal terra CLI reviews drove state-query, host-authority and query-scope corrections. Version-2 execution verifies filtered-host review files before reservations; historical version-1 plans cannot start new runs. All 277 tests/44 subtests and make check pass. No providers called, canonical data changed or freshness renewed; planned 5,427 variants are not an authorized or executed paid campaign. Full host review, pricing/calibration and remaining final data/release gates remain open.

## Event maintenance contract development — November 6

The [isolated event-validity contract](event-maintenance-development.md) now has 22 synthetic regression cases covering withdrawal/reinstatement, historical support, combined review timelines, typed correction relationships and canonical predecessor retention. Two terminal terra CLI design/code reviews found substantive issues; coordinator fixes preserve the source-proof boundary and an explicit predecessor-bound migration choice. All 299 tests and 44 subtests pass. No canonical record, active schema or CSV projection changed. Production profile/plan, promotion/source-proof/offline-history, consumer/export and portable-restore integration remain open; this does not close P7 or enable real withdrawal publication.

## Event validity profile integration — November 6

[Profile 1.0.2](event-validity-publication.md) now connects explicit event validity and correction relationships to structural/source-proof review, sealed atomic publication, predecessor-bound historical fields, offline history and retained/current/status CSV views. Three terminal terra CLI integration reviews identified receipt/export/replay and metadata-replacement weaknesses; new-profile public-proof pins, predecessor receipt hashes and generation seals bind those values. Receipt-only successors retain exact predecessor-receipt CAS and monotonic review times without renewing unchanged event observations. All 316 tests and 44 subtests pass, including 17 source-byte integration/packaging cases; make data/site/check reports zero errors, 489 warnings and 53 matching documented numbers. No real event migration occurred. The live source remains profile1.0.1; its new CSV projection `502d8eef6a4a5b6eab147ce69ba9a7ff67c4cc23dd6d518d6f7fedade7680bef` changes only the exporter fingerprint in its manifest, with all 16 view bodies identical. The [integration packet](../work/research/2026-11-06/event-validity-integration/README.md) retains exact scope. The subsequent pinned-commit check built `57916eb` twice identically, verified all 727 bundle members and restored publication/CSV/pilot checks without Git or private bodies; [receipt](../work/research/2026-11-06/event-validity-integration/portable-bundle-restore.json). No release asset was published. Real-event validity review, consumer reconciliation and final release/hosted verification remain open.

## Real event validity migration — November 6 review cohort

The [source-reviewed five-event migration](../work/research/2026-11-06/event-validity-migration/README.md) now selects profile1.0.2 at sealed generation `9f2c9b4d29e31a5434bb38f071724c38b59b926e114ad4b75acba854aa080287`. All previous records are unchanged; five explicit validity decisions accept three historical adoptions and two source-declared immediate-effect events. Coordinator visual review covers eight of eleven physical pages; separate terra adoption/effectiveness reviews plus a read-only candidate review retain their exact scopes. All528 retained claims reverified across144 source records/51 owned acquisition directories; three invalid selection-ledger copies were excluded with complete valid-source coverage. No new source acquisition or extraction-model call. Whitman's July7 original schedule remains in duration but is cleared from typed current end and qualified in status prose; no classification or headline count changes. Exact replay succeeds without source roots/visual artifacts. The new `d73054880d4aa5c472483295da33ccd24f451bac1c96c1162d94839e4887834e` projection supplies18views with five current accepted historical events, not current-force findings. The ballot-summary consumer now dispatches the authenticated publication profile, including a withdrawn-history regression. All316 tests/44subtests and full build/check pass (zero errors,489warnings,53matching numbers). The pinned `ed33d74` bundle built twice identically, verified all782members and restored actual profile1.0.2 publication/18-view CSV/pilot/cohort replay without Git or private bodies; all public hashes still match after replay. [Restore receipt](../work/research/2026-11-06/event-validity-migration/portable-bundle-restore.json). Temporary archives were removed and no release asset was published. Broader freshness, consumer/delivery and final release gates remain open.

## Missouri legislative-history follow-up

The [wave2 packet](../work/research/2026-11-06/mo-policy-wave2/README.md) narrows seven status statements, adds four missing official source links and replaces SB 4’s unsupported specific tariff threshold with the retained PSC overview’s supported scope. Exact comparison preserves all 442 IDs and every other value: 12 fields on seven rows change. Four new acquisitions, including pydoll, use the original job’s remaining reservations; the original 14-search/21-fetch cap is now consumed. Eight selected source versions are archived; replay adds none. Two terminal CLI reviews were requested with gpt-6.1-terra. Typed failed classifications and parties remain inherited rather than independently revalidated; exact session disposition, statutory force, tariff terms and sponsor-party evidence remain open. Final consolidated decisions replay without edits. Full data/site/check passes with zero errors, 489 warnings and 53 matching documented numbers. No headline counts or expanded generation changed.

## Supplemental original-term review

The [retained-source follow-up](../work/research/2026-11-06/duration-source-followup/README.md) visually checks four PDF pages across Carroll County, South Fork and Ormond Beach. Published calendar-term clauses support two encoding corrections; Carroll’s prose also records the earlier-repeal condition and distinguishes the published ordinance from later/current-force evidence. Six fields on two rows change; every other value and all 1,330 IDs remain unchanged. South Fork’s jurisdiction/termination wording remains unresolved, and Ormond’s unsigned second-reading text is not promoted as final adopted text. The frozen original 223-withheld list remains historical; supplemental outstanding source requirements number 222, including South Fork and Ormond. Two terminal CLI reviews were invoked with gpt-6.1-terra. No new source acquisition or extraction-model call. Exact answer/archive replay is a no-op; full data/site/check passes with zero errors, 491 warnings and 53 matching documented numbers. The two additional calendar-end warnings expose unresolved current endpoints rather than inferred fixed-day expiries; all other warning-category counts are unchanged. No headline or active-classification changes, full freshness renewal or final release.

## Ohio and Illinois policy follow-up

The [23-record source review](../work/research/2026-11-06/oh-il-policy-review/README.md) applies 60 field corrections with three terminal gpt-6.1-terra CLI reviews and eight coordinator-inspected Ohio PDF pages. Version-specific summaries preserve important procurement, cost-recovery, siting and contract exceptions; new sponsor dates remain separate from substantive procedural progress. HB 96’s unidentified veto-item action is not assigned to the data-center exemption or a bill-wide effective date. All 442 IDs and every unlisted value are preserved; disposition categories, legal-effect fields, typed effective dates and headline counts are unchanged. Thirty-two selected source versions are archived and replay without additions; all 55 retained versions pass integrity checks. Three Illinois status observations were newly acquired within existing caps, including pydoll, while other source dates remain historical. Exact baseline-guarded answer replay makes no changes. Full data/site/check passes with zero errors, 491 unchanged warnings, 53 matching documented numbers and no tracked private source text. All-field freshness, party/companion/omnibus questions, subsequent legal histories and final release remain open.
