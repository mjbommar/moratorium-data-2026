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
