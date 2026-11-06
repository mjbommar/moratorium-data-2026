# New Jersey chapter portal network review

A bounded headed pydoll acquisition with a 5,000 ms settle and bc-web network
recording identified the portal's actual `GET /api/chapterLaws` request. A separate
HTTP acquisition retained the complete 7 MB JSON response. It contains four
arrays; the first has 8,133 chapter records. Its 2026 subset has 72 entries and a
highest chapter number of 70, with a latest observed approval of August 6, 2026.
Chapter 75/S3379 is not in that returned subset. The separately retained official
bill history reports approval on August 27.

This is an observed catalogue coverage gap, not a conclusion that chapter 75 does
not exist, was not enacted or lacks legal effect. The portal's “Loading” text and
a request's HTTP 200 status alone were not treated as law evidence. No canonical
field or status changed.

The original JSON and rendered page/network payload remain private. A separately
registered 2026 JSON projection pins extraction lineage without replacing the
original empty client text. `review.json` records source hashes, request provenance,
counts and interpretation limits. The research client now supports
`--record-network` in explicit browser mode; unsupported controls fail before
reserving budget.
