# Conditional-cache pilot

Two bounded HTTP acquisitions exercised bc-web's native persistent cache against
the public dataset summary. Zero TTL forced origin contact on both calls. The
origin returned 200, then 304; the second result reused the original body and
preserved its observation time. Both raw bodies match their retained hashes, and
both budget reservations and terminal attempts remain in the ledger. No canonical
data changed.

The client supports `--conditional-cache` only with explicit `--mode http`, using
a private job-local cache capped at 100 MB. It records body reuse, origin
revalidation and origin attempt statuses separately from the materialized 200
body. Unsupported modes fail before budget reservation.

Archive tests verify that cached acquisition metadata preserves the original body
time and a later 304 does not rewrite an existing source-version manifest. Source
reacquisition is not substantive review: unchanged HTTP content does not prove
current law, complete coverage or correct interpretation. Full raw/cache artifacts
remain private. All 162 tests pass.
