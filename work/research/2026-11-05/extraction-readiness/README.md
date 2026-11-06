# Full-document extraction integration readiness

Inspected November 5, 2026. `inspection.json` pins the bc-modules revision,
source-file hashes, read-only database counts and an isolated failure probe.
This packet records integration findings; it does not complete extraction.

## Resumable adapter implementation

`scripts/extract_document_resumable.py` now wraps the actual bc-evidence
`extract_document()` function. It accepts an explicit backend, resolved model
identity, cells, cutoff and persistent request cap. Workspaces retain private
context, per-request reservations, successful typed outputs, hashes and per-chunk
coverage. Source text, prompt, model configuration, adapter or extractor changes
reject cache reuse. A nonblocking workspace lock prevents simultaneous writers.
Completed text processing is explicitly separate from substantive domain review.

Nine offline tests exercise full processing/replay, truncation, cumulative call
limits, failed reservations, recovery after partial failure, context changes and
corrupt cache rejection, reduction failure and returned-model mismatch. They use bc-llm's scripted backend through the real
bc-evidence map/reduce path; they are not paid-model or legal-accuracy tests.
The initial version required caller-side dollar controls. The subsequent adapter
adds an optional pinned dollar-allocation policy, persists reservations before
calls, settles successful priced calls and stops persistently for unpriced or
over-reservation results. Three further tests cover restart accounting, unknown
pricing and overruns. A bounded backend and conservative per-call allowance are
still required; local pricing is not an invoice guarantee. The subsequent
[actual Peru pilot](../full-document-peru-pilot/README.md) exercises these controls
with one paid call and a cached replay. No production EvidenceDB extraction
timestamps or canonical domain facts have been changed by these tests.

## Verified starting point

The existing pilot database contains 13 documents and 90 imported claims, with
zero extraction timestamps. It contains **zero research cells and zero
document-to-cell links**. The importer deliberately imported scoped excerpts,
not full-document model extraction. Running the stock `extract()` against this
database would skip documents with no cells. Populate explicit electoral/legal
cells and URL associations, or use `extract_document()` with explicitly recorded
cells; do not count an empty stock run as successful extraction.

## Library behavior and required adapter controls

1. `extract_document()` chunks the selected text at 7,000 characters with 400
   overlap, reads every chunk by default, retries each up to four times and
   reduces summaries. A caller-supplied `max_chunks` truncates work with a stderr
   message. Record the complete expected chunk manifest, attempted/successful
   chunks, errors and any ceiling in durable receipts. Text coverage does not
   prove that parsing/OCR captured every page, table or image.
2. Only the first 16 supplied cells reach the model. The prompt requests at most
   12 claims per excerpt. Record both limitations. Multiple cell batches or
   targeted supplementary extraction must be explicit; never call chunk coverage
   exhaustive fact extraction.
3. The generic claim schema has legal-instrument names and procedural steps but
   no dedicated ballot result, certification, vote-category or duration objects.
   Preserve generic outputs as candidates; separately validate domain-typed
   candidates against the expanded schema and the existing scoped review gates.
   Neither a source's word "passed" nor a model's "enacted" is legal acceptance.
4. Quote verification locates text in the whole document. Date support also checks
   the whole text. Preserve those checks but additionally review whether each
   date/value belongs to the claimed question, instrument and procedural step.
5. **Failed-document resume needs an explicit guard.** The stock `extract()`
   catches ordinary extraction exceptions and calls `put_claims(error=...)`.
   `put_claims` sets `extracted_at` even on errors; `pending_documents()` requires
   that timestamp to be NULL. An isolated temporary-database probe confirms that
   a failed document drops out of the pending queue. No production database was
   altered. The adapter must durably record failure and explicitly requeue it,
   or avoid this wrapper and manage completion after `extract_document()` returns.
6. The CLI's dollar cap applies to each invocation, not cumulative restart spend.
   Persist run-level reservations and reconcile ledger costs before resuming.
   Pin model, effort, prompt/schema and source/text hashes in cache identities;
   do not reuse outputs under changed instructions or reset budgets on restart.

## Next implementation and acceptance gates

- Build a private, separately named extraction workspace. Preserve imported
  claims and immutable canonical publications; do not replay the pilot importer
  over completed extraction, because it deliberately clears extraction timestamps.
- Start with one fully inspected official document and registered complete-text
  derivation. Pin payload/text hashes, page coverage, cell definitions, cutoff,
  library revision and a bounded model/call/spend policy before paid execution.
- Cache successful chunk outputs under full request fingerprints. Record failed,
  interrupted, omitted and unattempted chunks separately. Retry should reuse only
  matching successful calls and preserve previous attempts and spend.
- Test failure after one successful chunk, restart, changed text/prompt/model,
  explicit chunk ceiling, empty text, no cells, more than 16 cells and exhausted
  budget. Failed or truncated work must never acquire a full-coverage marker.
- Run actual bc-evidence extraction, retain model outputs privately, verify exact
  spans and dates, and produce domain candidates for human review. A complete
  model pass may have zero accepted claims; acceptance is a separate stage.
- Publish a sanitized receipt distinguishing text/page coverage, model extraction,
  candidate validation and substantive review. Keep the broader extraction and
  census TODO items open until their full cohorts satisfy the requirements.
