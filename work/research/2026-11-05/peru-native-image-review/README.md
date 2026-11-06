# Peru native-PNG evidence-gate exercise

The town-hosted full-size results PNG was directly reviewed for Article 2's
578 yes / 182 no row. `source.json`, `claim.json` and `visual-review.json` retain
a scoped review-stage transcription and explicit source/claim hashes.
`verification.json` records a successful call through `audit_expanded_evidence`
against the bounded client's verified acquisition ledger.

The receipt uses `renderer: native-png`, original width 795 / height 350 and a
null `pdf_page`. Its `render_sha256` is the original source-body SHA, not a
converted, cropped or rescaled image. The verifier checks PNG container/chunk
integrity and dimensions; it does not repeat or automate visual interpretation.
The existing source, subject, claim/value fingerprint and reviewer gates still
apply. PDF receipts retain their page/DPI rendering checks.

These review-stage IDs are not canonical allocations. No identity registry or
canonical measure changes in this exercise. Peru's 774 total voters remains a
separate observation; blank votes, question-specific ballots cast and certification
are not inferred. Canonical field/identity/publication review and operative legal
history remain open.

Validation: 12 visual-review tests, 93 full unit tests, and the real retained
Peru PNG evidence audit passed. Tests reject claim/body drift, changed image
hashes, crop/page parameters, dimension mismatch, non-PNG bytes and corrupt
container checksums. Byte/container verification does not authenticate the town,
certify the result, decode all pixel semantics or establish legal effect.
