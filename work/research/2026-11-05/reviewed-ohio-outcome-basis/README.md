# Ohio reported-outcome candidate review

This overlay preserves the original `ballot-oh-001` worker ledgers and adds an
explicit reported basis for four result observations that had no independently
supported numerical passage rule. It covers Ashville's two differing vote-count
observations, Defiance, and Granville. Conneaut's calculated observation is unchanged.

The coordinator inspected retained source text, added four outcome claims scoped
to the corresponding result observations, and independently located every excerpt.
The original counts, unknown passage rules, unofficial certification status and
unresolved legal links remain unchanged. A reported electoral direction does not
establish cancellation, legal force, or a new moratorium.

Input and output hashes and complete before/after result records are in
`work/audit/ohio-outcome-basis-review-2026-11-05.json`. Recheck this directory using
`scripts/expanded_data.py` with both canonical CSV reference arguments. Source-backed
audit also requires the ignored retained client artifacts from `ballot-oh-001`.

These are candidate records, not authoritative published data. No current accepted
review decisions or canonical IDs are created by this overlay. The original job
audit correctly continues to report errors in the unmodified worker return; use
this reviewed overlay for the later census integration and promotion review.
