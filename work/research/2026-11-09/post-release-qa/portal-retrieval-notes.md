# Retained portal retrieval findings, November 9

These methods were used for bounded authority follow-ups, not a new nationwide search. Every live request retained the existing source-only client's pre-call reservation and immutable body/text artifacts; the 500-fetch ceiling remains unchanged. No new paid search or experimental model API call was made.

## WordPress authority indexes

Morgan County's public WordPress REST search returns raw JSON with discoverable post URLs. A generic readability extractor returns zero characters for these JSON responses; that is not an empty response. Parse the retained body as JSON and retain its original hash. The `2026` query returned only its first 30 entries; do not call that a complete site inventory. The `referendum` query returned three older posts, and the media `ballot` query returned an empty list. Neither establishes that no ballot or referendum exists elsewhere.

An official August 12 meeting page found through the index concerns a failed Cook County separation referral and public discussion of data centers. It does not establish the separate data-center advisory question's wording, qualification or result. Do not join measures merely because they share a meeting or jurisdiction.

## CivicEngage search fragments

Franklin County's `/Search` page is a JavaScript shell. A plain HTTP request to `/Search/Results` redirects to `/Search/Index` and also returns the shell. Both have transport success but supply no substantive result list.

The page's own JavaScript defines the results route. Supplying the normal AJAX request header produces the actual fragment through the existing bc-web HTTP transport:

```python
await retriever.fetch(
    results_url,
    mode="http",
    extra_headers={"X-Requested-With": "XMLHttpRequest"},
)
```

Here `results_url` is the observed `/Search/Results` endpoint with `searchPhrase`, `pageNumber` and `perPage` query parameters. Encode phrases as query values; preserve the final URL, redirects, exact body and request variant. The normal AJAX header changes the response representation; it supplies no source authenticity or legal authority.

For these three admitted requests, the existing bounded client was copied privately with only `controls["extra_headers"]` added before the existing Retriever call. The canonical repository client was unchanged; caps, reservations and receipt paths were preserved. This is a documented transport recipe, not a claim that the canonical client CLI now exposes custom headers.

The `2026 ballot` request returned the first 20 of 347 matches. Quoted `data center` returned three indexed hits and quoted `question 2` returned seven. The returned snippets show that quoting does not guarantee literal phrase semantics in this index. The subject matches concerned county resolutions, planning minutes and a commission index; the question-number matches were unrelated material. These bounded results do not establish the identity of Ottawa's reported question or prove absence of another ballot document. Search snippets are leads; follow the exact official question or ballot before admission.

## PrimeGov archived minutes

Renton’s official calendar links its PrimeGov public portal. The portal’s archive script exposes `/api/v2/PublicPortal/ListArchivedMeetings?year=2026`. Its retained JSON lists meeting dates, titles, committee IDs and published document descriptors; parse the body as JSON when readability extraction returns no text. Select the actual council record by date/title/committee rather than another same-day committee.

The selected descriptors supplied compiled document IDs 3780 (August 17) and 4038 (October 5). Both actual PDFs were retrieved with `/Public/CompiledDocument?compiledMeetingDocumentFileId=ID&compileOutputType=1`. Earlier requests using the numbers as `meetingTemplateId` returned HTTP 200 Document Not Found shells. Status 200 and an index entry alone do not prove a recovered document; validate file type, title/date, pages, content and hashes. Distinguish the descriptor’s template definition from its compiled output.

Two of the eleven retained portal/index/script/representation captures are the actual minutes. The index’s publication fields remain attributed metadata, and November 9 observation is separate from the August/October events. An ordinance title declaring immediate effectiveness does not supply the complete signed operative clause or its anchor. The October minutes’ opening CDBG wording anomaly is preserved while the data-center heading, discussion and closure identify the relevant entry.

## Session-specific profile rendering

Four South Dakota profile URLs were taken directly from retained official bill sponsor links. HTTP transport returned status 200 application/noscript shells without the party fields. These are retained acquisition versions, not party evidence. A bounded headless Pydoll render with a three-second settle produced the named 2025 or 2026 profile heading, party and district. The four expected name/year/party combinations and body/text hashes were independently checked. The rendered pages still include a generic unsupported-browser fallback in their DOM; the presence of that text alone must not invalidate actual profile content or make an empty HTTP shell evidentiary.

The canonical bounded-client CLI was unchanged. A private copy used `headless=True` in its existing browser controls because this environment had no display; reservations, fetch cap and immutable artifacts remained in the same namespace. Browser callback log prefixes were retained privately and separated from the wrapper JSON receipts; the authoritative journal and source artifacts were unchanged. Read-only rendering retrieved the public profile fields. The published findings are names, session years, party and source references; full source bodies remain private.


## Legistar status headers and unavailable action details

North Port's retained legislation HTML provides `ctl00_ContentPlaceHolder1_lblStatus2` (Passed) and `ctl00_ContentPlaceHolder1_lblPassed2` (September 22, 2026). Its normalized text extraction starts at the action-history table and omits these header fields. Inspect retained HTML/DOM before concluding that the record lacks a status or final-action date; missing extracted text is not missing source content.

The linked September 22 meeting page separately reports draft/unfinalized minutes and unavailable detailed actions/results. Preserve both observations: the legislation portal records passage, while the detailed roll call and executed text remain unverified. An unavailable action-detail link does not establish denial, and a portal status does not supply the missing executed provisions or current-force proof.

The attachment labeled August 31 meeting minutes supports the amended continuation motion, eighteen-month term, application processing condition and named dissent. The PDF lacks a printed date, start time, roll-call header and signatures. Attribute it to the official link label, preserve these limitations, and do not infer a numeric vote or hearing duration. See [source continuity](northport-source-continuity.json) and [coordinator adjudication](northport-adjudication.json).


## CivicWeb search metadata and signed copies

Loveland's public Virtual Library script discloses a GET to `/Services/ItemsService.svc/portal/search` with the `criteria` parameter and document/tracker/meeting flags. It returns document IDs. Its read-only `/Services/ItemsService.svc/portal/search/details` POST takes the returned ID array as JSON and returns titles, document paths and links. The endpoint and request shape were read from the actual retained site script; the request was reserved against the existing fetch cap and its request-body hash, response and source clock retained. This does not invoke a paid general search or write an external record.

The exact R-48-2026 lookup identified the signed resolution as October 27 attachment document 521898 and September 15 unofficial voting results as document 519022. Fetch those actual files before accepting facts; metadata titles are navigation evidence. The earlier unsigned document 518569 was byte-identical to its prior capture and added no substantive evidence. Distinguish unsigned six/nine-month drafts, the signed twelve-month resolution, and later attachment/capture dates from adoption/effectiveness. The voting-results sheet is labeled unofficial and does not identify the amendment mover.

## Image-only minutes and signature appendices

Lochbuie's signed ordinance and July 21 minutes have empty original normalized extracts. Preserve those original bytes/extracts, render the actual pages, retain a separately hashed local OCR reading aid, and verify material handwriting and vote text visually. Store the OCR as a distinct derivation of the exact body rather than overwriting the original extraction or renewing factual acceptance automatically. The adoption/publication certification and actual newspaper publication are different evidence questions.

Paonia's already retained four-page resolution includes a scanned final signature-audit appendix omitted from normalized text. Inspect the complete PDF, including signature and appendix pages, before treating a missing text passage or conditional boilerplate as proof of an unexecuted draft. The printed audit report supports documentary execution; it is not cryptographic verification. No network refetch was needed for that source. The checked town meeting index was empty or linked an archive ending in April 2025, and the public document browser was blocked; none proves absence of 2026 minutes or later action.


## Historical session rows in Maine's Presto database

The legislature library links a maintained biographical database with distinct legislator and session searches. Use the Sessions records for historical party: match legislature number, years, chamber, residence and name, rather than projecting a current affiliation backward. The library identifies its sources and describes the database as informational rather than an official record of service. Match its row to the official bill sponsor summary; Dill's 125th-session row combines House and Senate service, so the bill's own chamber and date still matter.

The public QuickSearch widget script supplies the query-builder endpoint and the observed Last Name field; its query builder returns an encoded expression. The common script supplies the ClearSearchRedirect navigation. Preserve query construction as navigation metadata, not party proof. A first anonymous deep link can redirect to the home page, and an unrendered search response can report a hit count without any party rows. Initialize and reuse the anonymous session and render the actual results grid. The retained Sherman, Stanley and Dill grids contain the party cells used here. Record rendered DOM/text separately from raw HTTP payloads and do not invent an HTTP status when the direct browser capture did not measure one.

## California analysis downloads and historical party

LegInfo analysis links use observed JSF form controls including bill ID, version, analysis ID and office. Download the actual selected analysis with the anonymous form session; a prior retained page has redacted cookies and cannot supply a live session for a later form POST. Keep live cookies in memory, redact them in retained metadata and publish no viewstate values. The read-only form requests remain reserved against the existing fetch cap. The normal curl-based HTTP transport retrieved the PDFs after the plain anonymous transport failed; failed reservations remain recorded.

The dated official Senate floor-analysis headers identify Papan and Cortese as Democrats. An older analysis can establish historical party while the relevant amended/enrolled bill version supplies the actual material provisions; do not substitute an older version for later amendments. Current official member pages supply full-name identity correlation, not retroactive party proof. An inherited state-wide activity label is analytic context under the codebook, separate from bill-specific legal claims. Consistency across local and policy rows does not independently validate that underlying statewide judgment.

Custom captures retain exact body/text bytes and hashes. Their actual extraction methods are specified in the source-continuity receipt, because the legacy archive's default method label is generic. Redirected pages, scripts, query metadata and operational failures are retained as retrieval evidence and never counted as independent party facts.

## Arizona final-disposition API, November 9

The rendered final-disposition search page links its `FinalDispBundle` and `/Home/JavascriptConstants`. The actual script calls `/api/Disposition/` with `sessionId` and an explicit empty `body` parameter; omitting `body` returned HTTP 404, while the observed form returned HTTP 200 XML. Select a returned DispositionId and call `/api/BillStatus/` with `sessionId`, `dispositionId` and `body=`. Match the returned session, BillId and bill number before opening the observed BillOverview route. The form itself and a successful script retrieval do not establish any bill outcome. Preserve XML bodies and hashes; parse namespace-aware element names rather than expecting JSON. [Actual captures and applied review](arizona-final-review.md) document fourteen successful versions and one private failed-parameter attempt.
