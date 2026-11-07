# Event validity publication integration

[Profile 1.0.2](../../../../docs/event-validity-publication.md) now connects the event-maintenance contract to structural validation, evidence review, atomic publication, predecessor traversal and CSV export. The real dataset remains on profile 1.0.1: no event validity migration, real withdrawal/correction, headline change or fresh legal-force acceptance occurred.

Three terminal distributed `gpt-6.1-terra` reviews drove corrections to export receipt authentication, replay proofs, chronology, historical-profile compatibility, portable dependencies and receipt binding. New-profile plans seal the public proof set and pin the predecessor receipt. New generation names bind tables and exact public receipt bytes. [Review reconciliation](review-reconciliation.json) retains report hashes/session IDs and coordinator fixes. Internal hashes still require an externally pinned Git revision or verified release manifest including the tip pointer; they do not authenticate a reviewer.

The 17 synthetic integration/packaging cases exercise actual source-byte/quote checks, profile1-to-profile2 withdrawal migration, correction to new IDs, reinstatement/second withdrawal, immutable historical fields, stale/backdated plans, proof/receipt replacement, downgrade prevention and receipt-only successor CAS. Restored actual checker/export scripts run in a separate root without Git or source bodies. Missing/tampered schemas and missing runtime fail. These are mechanical fixture assertions, not factual legal judgments.

Full suite: **316 tests and 44 subtests passed**. Data/site/check build: zero errors, 489 warnings, all 53 documented numbers matched. [Validation](validation.json) pins final implementation and logs. The committed portable bundle check is the next pinned-revision step; this packet initially records it as pending.

[Preservation](preservation.json) verifies unchanged legacy CSVs, identities, original schemas and JSONL pointer. The regenerated current CSV projection has all sixteen view bodies byte-identical to its predecessor; only the manifest's exporter fingerprint changes. The actual source generation, profile and event/ballot counts are unchanged. The new eighteen-view export set is available only when a reviewed source generation actually selects profile 1.0.2.

Real five-event validity review/promotion, consumer reconciliation and final release/download/hosted verification remain open. No search/fetch/extraction API calls occurred in this increment; CLI review spend is unknown, not zero-priced.
