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

The [current coordinator accounting](../work/audit/discovery-coordinator-accounting-2026-11-06.md) reconciles 185 candidates: 31 additions, one covered instrument, 118 reviewed withheld and 35 awaiting review. The helper pins 27 packets, checks 144 explicit candidate fingerprints and re-verifies 157 distinct original body/review-text versions. Six alternate-layout candidates retain scope limits. Mechanical accounting is not legal acceptance.

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
