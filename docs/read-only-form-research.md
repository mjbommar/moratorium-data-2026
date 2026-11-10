# Read-only government form research

Use this when an official search form exposes records that an indexed search or a static capture misses. An unsubmitted form is not a result set, and a zero-result query is not evidence that an instrument does not exist.

## Evidence and request contract

1. Inspect a retained official page first. Record its actual form action, method, field names, option values and submit control. Do not invent a document ID or assume a different portal's parameter names.
2. Reserve the operation before acquisition using the persistent research-client ledger. Admit the purpose, source URL, query, field and administration or jurisdiction filter. A browser form operation can require an initial GET for fresh session/viewstate and one search POST; report both intentional document requests as well as the client-operation count. Redirects and asset loads are separate from that count.
3. Submit only the observed read-only search form, to its observed action on the same origin. Preserve hidden state privately. Do not submit applications, authentication, comments, payments or other changes as a search operation.
4. Retain the actual POST response bytes and timestamp, query/filter values and initial-navigation lineage. Do not label the initial GET's HTML or readable text as the search response.
5. Extract text from the POST response. If reusing a `bc_web.FetchResult` object, replace its `html` and `raw` **and clear its cached `content`** before calling `bc_research.pipeline.document_text`. Otherwise the parser can return the earlier navigation's `PageContent`. Preserve the original extraction and register any corrected derivation against the exact response-body hash.
6. Inspect the result DOM when the main-text extractor omits a short result table. Record the returned population and the exact selected row; do not imply that the query covers all later history.
7. Follow a document link actually present in that row. Keep the result row, linked document, source clock, body/text hashes and source roles together. For scanned documents, inspect the relevant pages visually, retain OCR lineage and distinguish signing, filing and effectiveness.
8. Import the selected immutable versions into the evidence archive and verify native-store readbacks. Source corroboration does not substitute for the required independent review of a material assertion.

## Identifier variants are search hypotheses

The Kentucky journal stores the printed Executive Order `2026-494` as `2026-0494`. The literal order-number query returned zero. A separately admitted partial-number query, `494`, with the observed `EONumber` field and `ABeshear` administration value returned six records. The selected 2026 row linked its actual filed PDF.

Do not generalize the padding rule to another source without evidence. Record unsuccessful and successful queries. Never synthesize a PDF URL from a guessed padded number.

## Worked evidence

The [Kentucky review receipt](../work/research/2026-11-10/post-release-qa/kentucky-order494-publication-review.json) retains the original queries, result selection, extraction correction, five native-source readbacks and source-specific limits. The [candidate packet](../work/research/2026-11-10/post-release-qa/kentucky-order494-review-packet.md) separates a proposed observation from canonical admission.

The filed copy adds Secretary of State attestation/seal and a received-and-filed stamp absent from the governor's posted copy. The official journal row and stamp both report August 6, 2026. Those observations resolve a source gap; they do not establish unchanged current legal force or automatic project applicability.
