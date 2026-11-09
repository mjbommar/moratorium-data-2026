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
