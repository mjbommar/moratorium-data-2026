# Brownfield and Freedom native-JPEG evidence exercise

Four source-qualified claims passed `audit_expanded_evidence` against the retained
acquisition ledgers: Brownfield's 671 yes / 191 no / 862 ballots-counted statement;
Freedom's 331 yes / 115 no; and Freedom's separate VOIDS 24 and circled total 470.
No result is certified or canonically published by this exercise.

Receipts pin original bytes, **stored** dimensions and EXIF orientation. Brownfield
is 2200 × 1700 with orientation 8; its display orientation differs from its stored
raster dimensions. Freedom is a progressive 600 × 800 JPEG with orientation 1.
The verifier checks complete JPEG framing and strict Pillow decoding, dimensions,
orientation, source/claim fingerprints and original-byte identity. It does not
transpose, crop, resize, resave or create a synthetic PDF. A receipt's
`render_sha256` equals the original source-body hash. Image verification does not
repeat or authenticate the substantive visual judgment.

`claims.json`, `visual-reviews.json` and `verification.json` retain the review-stage
claims and evidence proofs. `source-projections.json` preserves source metadata;
the public Freedom projection omits the expiring CDN acquisition URL. The original
private ledger retains that URL, and the actual audit used it. The durable post
citation is not substituted for the image's acquisition URL. These public
projections are documentation, not directly executable canonical source records.

Freedom's account affiliation and certification remain unresolved. Its VOIDS
category remains unmapped, and its circled total is not assigned to ballots cast.
Brownfield's unusual draft power wording and both places' operative legal histories
remain open. Review-stage IDs are not canonical registry allocations. The original
worker and canonical snapshots remain unchanged.

Validation: 21 visual-review tests passed in both project and bc-modules Python
environments; all 108 unit tests passed in the bc-modules environment. Tests
reject claim/body drift, transformation hashes, orientation/dimension mismatch,
missing orientation/crop parameters, truncated/non-JPEG data and lenient decoder
configuration. PNG and PDF behavior retains its existing checks. Pillow is now
included in `make install` dependencies.
