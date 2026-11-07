# Alaska full-record source review

November 7 review of the three Alaska records, retaining the November 5 source cohort separately from later retrievals. All 26 fields per record received a source-specific assessment and independent Terra CLI review. The public field ledger contains value fingerprints, source-version hashes, qualifications and specific next actions; private source bodies and full review outputs remain outside Git.

All three records remain **researched, unresolved**. Fairbanks has a referral rather than established enactment; Petersburg has first-reading materials rather than established final passage; Houston's adoption is documented but its separate signature date, exact operative endpoint and later history remain unresolved. This is not acceptance of all 78 values as current facts or completion of inventory-wide freshness.

One guarded correction replaces Houston's unsupported citywide negative about projects with the report's Rauscher-to-AIDEA attribution and explicit uncertainty about permits, boundaries and legal applicability. The coordinator inspected the retained report passage. Both the full original row fingerprint and exact prior cell matched before the standard apply pipeline ran; its dry run and actual apply each changed exactly one field. No rows, IDs, dates, status classifications or headline counts changed.

The field ledger preserves the reviewed values' fingerprints and explicitly marks Houston's corrected cell as superseded. The [answer](answers-local.json) and [apply receipt](../../../audit/apply-20261107T082926.json) preserve the exact before/after values. The independent review rejected the initial compressed attribution; only its qualified replacement was applied.

Validation after the correction: `make data site check PYTHON=.venv/bin/python` completed successfully. The exact canonical CSV comparison against parent `ed82965` found one changed cell and 1,330 unchanged row identities. Generated Alaska Markdown/HTML reflect the correction; all 65 checked documented numbers still match. This verification does not resolve the source gaps above.
