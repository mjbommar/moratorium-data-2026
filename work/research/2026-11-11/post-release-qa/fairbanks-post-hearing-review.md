# Fairbanks November 10 hearing: bounded follow-up

The current published edition remains qualified v2026.11.11.post1 / V35. This follow-up changes one research-queue entry and no canonical data, public page, status, headline or ballot record. The 1,347 unresolved whole-record reviews remain open.

The earlier November 10 recovery preceded the scheduled evening hearing. A new, bounded November 11 phase therefore looked for completed proceedings, rather than repeating the failed original attachment. One Exa query returned six results, including pre-hearing notices, unrelated material and our own dashboard. None supplied independently verified completed-action evidence. One SerpAPI query restricted to November 10 onward returned zero results. Neither observation proves that no hearing or vote occurred. The own-dashboard result was excluded as corroboration.

A browser capture of the actual [meeting page](https://fnsb.portal.civicclerk.com/event/5763/overview) produced only a thin visible shell. Its recorded network activity exposed an actual GET to [Events/5763](https://fnsb.api.civicclerk.com/v1/Events/5763), which was then acquired directly. That JSON identifies the Planning Commission event and lists two published files: agenda 13383 and agenda packet 13403, both carrying October 29 publication timestamps. The captured response has no usable minutes or media file. Its live/streaming/default-timestamp fields are retained but do not establish an ongoing meeting, a completed meeting, a vote, or nonpublication elsewhere.

The source-provided full-packet URL for **file 13403** was attempted once over HTTP and failed without a body. It is distinct from the previously exhausted file 13344 routes, which were not repeated. No usable full packet, ordinance text or completed action was recovered. Further routes were not guessed. The fixed cap is exhausted: one Exa operation, one SerpAPI operation and three top-level fetch operations. The browser also loaded dependent resources recorded in the private trace; the fetch-operation count is not a count of all HTTP requests. No model requests or agents were used.

Two successful body/text pairs—the rendered portal and event JSON—were archived and read back exactly from the private native store. The generic text extractor returned empty text for the JSON body; a lossless indented serialization supplies a separately pinned derivation, with decoded JSON equality checked and the original extraction retained. The failed empty packet was not imported as a substantive source. Exa reported $0.007; SerpAPI pricing is unknown, so no complete total or zero-cost claim is made.

Next evidence must be a distinct published minutes, action, media or ordinance source, or a documented changed version/transport condition. Do not repeat these same queries, meeting page/API, file 13403 HTTP request or old file 13344 routes merely to rediscover this state. Planning Commission recommendation, Assembly adoption, operative terms, effective anchor, later action and actual project applicability remain separate questions.

- [Attempt accounting, source pins and residual questions](fairbanks-post-hearing-review.json).
- [Exact source continuity](fairbanks-post-hearing-source-continuity.json).
- [Queue and unchanged-data verification](fairbanks-post-hearing-verification.json).
