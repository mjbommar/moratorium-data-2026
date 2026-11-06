# Frozen domain extraction evaluation — November 6, 2026

**The bounded support gate did not pass. No model-generated facts were promoted.**

[Protocol](protocol.json) and [twelve required slots](required-slots.json) were committed as `6fd6e3f` before any calls. The current extractor and prompts were then held fixed while processing three retained sources: Wells's full warrant, Bloomington's special-town agenda and the North Dakota results view containing Harwood's charter contest plus neighboring contests. Seven Wells chunks and one chunk for each other source were processed; a Wells summary reduction accounts for the tenth accounted backend call. Each case replayed without additional calls.

These are previously source-reviewed cases, frozen against **further** extractor tuning. They are not historically unseen independent data or proof that the original pre-bulk ordering was met. Numeric thresholds and required slots were frozen before extraction; detailed reviewer label/severity operationalization and the reporting auditor followed extraction. Do not describe this as a fully preregistered or independent external benchmark.

## Measured result

The [artifact audit](audit.json) verifies contexts, original body/text hashes, cached outputs, accounted backend call/reservation limits, backend-ledger agreement, review coverage and matched slot fields/values. It performs no model calls and does not determine entailment itself. The separate SDK diagnostic leaves the strict provider HTTP-attempt cap unverified.

| Metric | Observed | Frozen criterion |
|---|---:|---|
| Supplied text chunks processed | 9 / 9 | Complete |
| Field-schema-valid candidates | 36 / 36 | 100% |
| Candidates with exact original quote locations | 36 / 36 | 100% |
| Candidates with multiple possible quote locations | 4 | Reported separately; exact location alone is not entailment |
| Coordinator fully supported/relevant candidates | 32 / 36 (88.9%) | At least 95%; **not met** |
| Ambiguous candidates | 4 | Withheld; not four confirmed factual errors |
| Required slots fully matched | 11 / 12 (91.7%) | At least 80%; met for this checklist only |
| Confirmed high-impact factual errors | 0 | Zero; does not resolve two high-impact ambiguities |
| Review-ready source documents | 0 / 3 | Each must meet support/coverage/slot checks and resolve critical ambiguity |

All 36 raw candidate IDs are counted once; different supporting quotations can still produce separate nominations for the same field value. Support labels concern the listed values, not an exhaustive enumeration of every source fact unless required by a frozen slot. The small, deliberately selected test is not a population accuracy or confidence estimate. Discovery recall, false exclusions and primary-source recovery rates were **not measured**: sources were already selected and recovered. Text-chunk completion is not proof of complete PDF/OCR coverage or complete legal review.

## Source-based findings

- Wells's proposed 180-day term and June16 applicability anchor were extracted correctly, distinct from election day and actual effectiveness. Its area threshold has the correct number, operator and unit, but the candidate basis says only the defined Data Center Area term; it does not explicitly carry the impervious-surface composition required by the frozen slot. That slot is partial, not a full match.
- A Wells legal-reference candidate flattens a notwithstanding/default provision and a nullification limitation into a legal-basis list. The statutes occur in the document, but their roles need qualification. Its narrow quote also does not cover every component of that value.
- Bloomington's advisory status, proposed wording and scheduled election date are supported. The City asked to act remains distinct from the township electorate; a proposed restriction's actual territory is not established by the actor's name alone. The advisory_support enum also needs a clearly defined reference axis before accepting a classification.
- Harwood's 105/325 charter counts and unofficial status remain separate from another Harwood contest, Horace and statewide totals. One-of-one fully reporting precincts does not expressly settle every meaning of count completeness. The complete reporting-status candidate remains ambiguous; generic repeated quotes also need contest-specific scope selection.

## Independent review and adjudication

Two separate `gpt-6.1-terra` CLI jobs reviewed all 36 candidates and twelve slots against the retained original text, without reading each other's labels or the coordinator's initial assessment. Both jobs are terminal. They agreed on 35 of 36 disposition labels (97.2%; nominal Cohen's kappa about 0.82). Their disagreement concerns whether the flattened Wells legal-basis candidate is unsupported or ambiguous. Both independently identify the incomplete area-basis slot.

The coordinator's initial labels were recorded before reading the CLI outputs. Final source-based reconciliation retains four ambiguities, including advisory terminology even though both CLI reviewers supported its literal meaning. This is not majority-vote legal acceptance. AI review agreement is not an accuracy measure or independent human ground truth. [Label comparison](candidate-review-labels.csv) and [provenance](provenance.json) retain the distinction between initial, final and each CLI judgment; detailed quoted reviews stay private.

## Cost, preservation and next action

Ten successful `openai:gpt-6-sol` backend calls used low effort, native output and a 6,000-token output ceiling. Backend retry/agent repair was disabled, and no native chunk retry was needed. **This did not disable the OpenAI SDK retry layer.** The [installed-client audit](sdk-retry-audit.json), performed without a network call, observes SDK `max_retries=2`. No provider HTTP-attempt ledger was captured, so ten backend calls do not prove ten HTTP/model attempts or compliance with the intended thirteen-request cap. There is no evidence here that the provider cap was actually exceeded; it is unverified. Successful-call estimated cost was **$0.2375234**, and accounted backend reservations stayed within thirteen calls/$6.50. Unobserved failed/retried provider attempts may have unrecorded cost. This uses the installed bc-llm price table, not provider invoices. CLI review cost is separately unknown; this is not a campaign-wide spending total. Cost per review-ready document is undefined because none passed readiness.

Canonical CSVs, identity registry and expanded publication are unchanged. All candidates remain unaccepted. Full inputs, requests, cached outputs, budgets, reviews and executed-code snapshots remain private under `/data0/moratorium-refresh-2026/frozen-domain-evaluation/`.

Next: explicitly control SDK retries and retain actual HTTP-attempt accounting; clarify advisory mechanism and reporting-completeness semantics; preserve statutory-reference roles and actor/electorate/territory distinctions; require explicit composed measurement bases and richer supporting spans. Make changes using development/regression cases, then freeze a new evaluation cohort. Do not retune and rerun these same documents while presenting them as a fresh independent holdout. Broader P3/P4 calibration, discovery/search metrics and all remaining freshness/release gates remain open.
