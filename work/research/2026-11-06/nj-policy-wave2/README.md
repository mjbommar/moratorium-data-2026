# New Jersey remaining-worker review and Chapter 75 follow-up

This applies fifteen field corrections across three existing state-policy IDs.
All 442 IDs, all other state-policy values, the local CSV and expanded snapshots
are preserved. [Preservation check](preservation-check.json) records each change.
These are source-qualified procedural/proposal corrections, not a completed
New Jersey current-force or later-action census.

[Validation](validation.json): all 272 tests and 44 subtests pass; full
data/site/check has zero errors, 489 existing warnings and 53 matching audited
numbers. Replay proposes zero additional edits.

| Record | Correction | Remaining limits |
|---|---|---|
| S4293 | Replace unsupported final-death claim with the documented conditional-veto action; category `vetoed`, legal effect `unknown`. Add reporting/agency classification and primary URL. | No verified final session disposition, concurrence or override. The bill is not asserted to have revived. |
| S3611 | Preserve proposal status; record SPC review/default timing and defined subsidy limits, with permitting mechanism/mixed scope and primary URL. | SPC deemed approval is not all municipal approvals. Proposed effectiveness is not actual enactment. |
| S680/A1170 | Preserve separate chamber histories and synopsis/text-version distinctions; qualify both A1170 supply and plan submission by its published-finding trigger. Add utility-grid scope and primary URL. | Official companion designation does not prove identical final text. No BPU finding or implementation is established. |

## Direct source review and corrections

Seven hash-verified retained source versions support the review: four fully
rendered bill histories, two introduced proposals and the conditional-veto
document. Earlier generic shared status-shell bodies are not treated as the
filled histories. Acquisitions were November 5–6 UTC; coordinator review was
November 6 New York time. Their last displayed actions are not a proof of no
later unrecorded action.

The three substantive HTML bodies explicitly declare Windows-1252. Their original
client extractions contain replacement characters. Strict declared-encoding
decoding and HTML text extraction are separately registered in
[derivation receipts](derivations.json), retaining the original bodies and text
versions. This is not consolidated amendment-markup parsing or a declaration
that introduced text is enacted law. `pages:[1]` denotes the logical HTML
extraction unit, not a physical PDF page count.

Two read-only `gpt-6.1-terra` CLI jobs reviewed procedural status and proposal
terms in distinct source scopes. Both identified a qualification missing from
the initial A1170 draft: its finding/publication condition applies to plan
submission as well as supply. Coordinator source review incorporated that fix,
the separate connection-clause language and the S3611 limits. The jobs did not
independently re-review the refinements; agreement is not legal ground truth.
Hashes and findings appear in [reconciliation](review-reconciliation.json).

S3611's 45 days run from planning-board submission to SPC, consulting BPU;
silence deems SPC approval. Its subsidy definition concerns State-public-body
funds over $25,000 and excludes unsubsidized procurement. A1170's proposed plan
decision/resubmission intervals are 90/30 days. Its supply rule specifies new
verifiable Class I renewable energy and/or nuclear power, without net decrease
of the specified sources supplied to the system. Its section 3(d) connection
clause refers to a plan under 3(b); the trigger interaction is not adjudicated
here. The S4293 veto document's header/return identify S4293 while internal
references say 4923; the source discrepancy is retained rather than normalized
into a new bill identity or enacted recommendation.

## Chapter 75 remains unresolved

One fresh bc-web HTTP invocation used the final reserved fetch allowance in the
existing chapter-portal workspace, without resetting caps. The response observed
November 7 at 00:07 UTC (November 6 New York time) has the same body hash as the
earlier catalogue. The returned 2026 part0 projection still has 72 entries, maximum
numeric chapter 70, and no chapter 75 row. These include different document types;
they are not 72 distinct chapter laws or the complete law universe. See the
[exact follow-up](chapter75-index-followup.json). The signed chapter,
effectiveness and implementation remain unresolved. No more guessed URLs or
repeated broad search calls were made, and no absence finding follows.

## Archive and application

[Source preflight](source-preflight.json) verifies all seven original versions
and separately registered text versions. Four archive versions were added:
three corrected text decodings and one refreshed catalogue observation whose
body is unchanged. Native bc-store replay/readback verifies all 62 eligible
New Jersey manifest records; thirteen pre-existing body gaps remain unimported.
This is not four new primary laws or complete source recovery. Raw bodies,
provider exchanges and detailed CLI reports remain private.

The explicit baseline and guarded legislation applier limit changes to fifteen
fields in three rows. Replay proposes zero edits. Counts remain 1,330 local
records, 442 state-policy records, 440 legacy bill rows, 94 enacted bill rows,
50 measures and 50 current ballot-result observations. State `failed_died` falls
by one and `vetoed` rises by one; this is an uncertainty correction, not an
asserted revival. Final release, broader freshness, implementation and sibling
delivery gates remain open.
