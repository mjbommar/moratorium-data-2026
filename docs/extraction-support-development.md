# Composed extraction evidence: development checkpoint

A later [compound-condition development increment](compound-condition-development.md)
adds transport 1.2.0 and an optional canonical profile, with no new accuracy result.

Follow-up: [classification definitions](ballot-semantic-definitions.md) now
specify the advisory development axis and reporting-completion meaning. Their
current-use audit flags evidence-lineage work separately; it does not renew
source acceptance. The text below records the preceding development checkpoint.

The failed three-source evaluation remains failed. This development increment
responds to its source-support findings; no new model extraction has been run,
no canonical fact promoted, and no improved accuracy measured.

Extraction transport schema [1.1.0](../work/schemas/extraction/1.1.0.json) adds
optional `supporting_passages` to field candidates. Each passage has exact text
and an explicit role, such as definition, override, limitation, actor, electorate
or territory. The candidate packet retains every matching document-text span,
flagging absent and repeated matches. The historical 1.0.0 schema is preserved.
These roles are unreviewed model assertions. The list may be empty, and its
completeness still requires source review. Document-wide location does not show
that the generating chunk contained the passage or resolve contest scope.

The revised guidance requires composed measurement bases and qualified statutory
references, keeps the requested actor separate from electorate/territory, and
withholds advisory mechanism classifications when their reference axis is unclear.
It conservatively withholds count completeness inferred solely from fully
reporting precincts. These are prompt changes, not demonstrated extraction fixes.
Canonical advisory/reporting enum definitions and review of existing uses remain
open; this change does not silently redefine or relabel historical records.

Candidate IDs hash the serialized fact, including its supporting passages. They
are specific to this representation; do not reuse old candidate-ID review labels
or call changed outputs an exact replay. The adapter, schema and prompt are
pinned in the cache context. A changed context must use a separately admitted
workspace. Rejection now preserves the old packet; a failed same-context rerun
still removes stale success output.

Historical evaluation audits now verify the retained executed-code bytes by
their original protocol hashes, rather than requiring live development files to
remain unchanged forever. They still require the frozen source/canonical inputs.
The old audit re-runs with the same 32 supported, four ambiguous, 11/12 matched
slots and zero ready documents. Added passage audit checks reject mismatched,
missing or fabricated location inventories; readiness with supplied supporting
passages requires unique locations. An absent optional passage list cannot prove
that no additional source evidence was needed.

Two independent read-only `gpt-6.1-terra` CLI jobs reviewed the initial change.
They identified the context-rejection deletion bug, frozen-audit live-code issue,
and insufficient passage auditing; these received code and regression changes.
They also identified open work: cross-chunk composition, durable promotion into
separately reviewed claims, dedicated actor/electorate/territory values, enum
definitions and source-grounded semantic evaluation. Those findings remain open.
The jobs did not review each other's output or validate the subsequent fixes;
the coordinator tests those changes. Their raw reports remain private and their
receipts identify the exact reports by hash. CLI agreement is not legal truth.

Next, settle the canonical semantic definitions and reviewed claim mapping, then
freeze a new evaluation cohort before paid extraction. Keep the earlier three
sources as development cases rather than presenting them as an unseen holdout.


## Literal-source gate development — November 8 UTC

The production rule-unit adapter now requires unique, exact Unicode occurrences of clause/nested source text and supporting quotations. It marks missing/repeated evidence, strict expression errors, unknown expressions and proposed-source/enacted-assertion conflicts unresolved. Returned clauses, qualifications, original outcomes, hashes and planned dispositions are retained independently of candidate status. Invalid or coerced values received at the adapter boundary remain unscorable; incomplete response accounting is explicit. This gate does not prove relevance, completeness or joint entailment. Every candidate remains unaccepted and review-required; condition expressions remain non-executable pending formal semantics.

The prompt explicitly preserves line breaks and line numbers and requires the source passage plus supporting passages jointly to support every assertion and governing qualification. Completeness takes priority over shortness. No lossy quote normalization, fragment joining or invented quotation is permitted.

The coordinator reran 27 focused adapter/native-transport/source-gate tests successfully using the existing BC interpreter, with no provider calls. A diagnostic replay of the exposed 27-response Virginia cohort retained all 27 clauses, yielding one mechanically eligible candidate and 26 unresolved. It does not alter the historical failed grade or create an unseen holdout. The source-contract diagnosis was independently reviewed before this conservative development integration.

Execution remains blocked on two concrete boundaries: native validation may reject or coerce provider content before the adapter can retain its original bytes, and the frozen review consumer rejects an unresolved disposition carrying a retained clause. Future evaluation must capture and bind raw inputs/outputs, account for all failed/unscorable/generated/planned units, and use a separately reviewed prospective consumer contract. Do not modify historical evaluation artifacts to make the new packets appear compatible. Source-grounded semantic review, condition/consequence semantics and a newly frozen calibration and unexposed holdout remain required. No P4 quality pass, automatic promotion or new paid trial is claimed.
