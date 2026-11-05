# Coordinator review, 2026-11-05

This is scoped review evidence, not a declaration that the overall refresh is done.

## Wells Article 5 result certificate

The coordinator independently inspected the rendered first and second PDF pages:
`maine-pilot/wells-results-page.private-1.png` and
`maine-pilot/wells-results-page.private-2.png`.

Page 1 is headed “TOWN CLERK'S CERTIFICATE OF RESULTS OF SECRET BALLOT REFERENDUM,”
identifies a special town meeting on November 3, 2026, and states the clerk certifies
the counted ballots. Page 2 identifies Article 5 and the retroactive data-center
moratorium question, followed by YES 5818, NO 1282, Blank 459. It bears the clerk's
signature and handwritten date 11/4/2026. This supports a certified result observation
dated November 4, with 7,100 yes/no votes and 459 separately reported blanks. It does
not independently establish an overvote total or that 7,559 is overall election turnout.

The source PDF is the town's DocumentCenter item 8559, body SHA-256
`5f5e3d76054063a7fdcf7a2505bf4698aeac074c0ad18b5354abed45258d1d95`.
Image-based reading and OCR are distinct evidence methods; the handwritten date
must not be presented as a machine-located exact textual quote if OCR missed it.

This review does not accept ongoing legal force, a computed end date, a project
exposure link, or the identity of a predecessor ordinance. Warrant text and adoption
history require their own scoped decisions.

## Pilot execution incident

The Ohio job repeated six search calls after a script error; actual total 12 searches
and six unpriced SerpAPI calls. The first response files were overwritten. Its run
report records the incident. Do not count missing first responses as archived proof.
The replacement bounded client reserves each attempt persistently before network
access, uses unique artifact names, and refuses a rerun above the stored cap. Tests
exercise reservations surviving interruption and errors. Future jobs must use it.

## Normalization quality gate

A structurally valid ledger with all known values blank is not a complete adapter.
Normalize supported source-qualified values and results where available, retaining
per-field source claims and review states. Unknown applies to missing or unresolved
facts, not merely to facts whose downstream legal implications need separate review.
