# Pennsylvania and Virginia policy source review

All 40 current IDs are accounted for: 22 Pennsylvania and 18 Virginia. Two disjoint Codex CLI source reviews and one candidate review were invoked with `--model gpt-6.1-terra`. Each explicitly retains partial-review limits; none is a certification of every field or later legal history. [Reconciliation](coordinator-review.json) records accepted changes and unresolved questions.

## Applied changes

The [exact diff](exact-diff.json) contains 92 changed cells on 40 rows. Every other value and all 442 policy IDs are preserved. Changes include:

- 38 missing official source links; two Pennsylvania links were already present.
- Four explicit enacted effective dates, separating July 2026 site-assessment dates from January 2027 water-reporting dates without upgrading current-force classifications.
- Virginia SB 130’s chief patron, distinguished from the sponsor of the bill incorporating it.
- Applicant versus locality roles, retail-utility power basis, property-boundary radius, water-report availability and quarterly substitution, and proposed-versus-enacted or incorporated-versus-passed distinctions.
- Pennsylvania’s responsible model-ordinance agency, optional local pause authority, acceptance versus consideration, maximum term and earlier-application/repeat-use protections, incentive-conditioned NDA requirements and the later multi-part SB 1408 print.
- Later Pennsylvania re-referral and re-report dates, distinct from unverified amendment-vote claims.

The assessment exception’s ambiguous added-capacity phrase is preserved rather than converted to a definitive inequality. Tabled-bill failure classifications and other unlisted inherited fields remain qualified, not independently reverified. No legal-effect status, disposition category, instrument type, record count or local inventory value changes.

## Precursors and denominators

[Canonical memo-page links](precursor-links.json), retrieved without client-supplied bill parameters, connect memo 48467 to HB 2496, 48540 to SB 1345, and 48102 to SB 1359. All IDs remain stable; these precursor rows are not three additional independent bills or enacted restrictions. Their eventual finer form/identity migration remains open. README, codebook, known gaps and the generated landing page now explain why the legacy bill-type count is not a deduplicated independent-bill census. Resolution subtypes also remain in that legacy bucket.

## Evidence and validation

Nine targeted follow-up fetches used existing reservations: six memo variants/canonical pages and three published Virginia chapter PDFs. One native domain-filtered Exa search returned official leads; no legal fact was accepted from a search snippet. A memo was rendered through pydoll. [Search accounting](search-followup.json) reports the successful Exa estimate separately from unknown CLI/whole-run billing. No caps were reset and no new extraction-model calls occurred.

All 81 current retained source versions pass integrity checks, including the initial 72. The [50 selected source versions](selected-sources.json) have exact archived body/text matches. Raw bodies, model reports and screenshots remain private. Coordinator inspection covers 18 Pennsylvania HTML print pages and four Virginia PDF pages. The Pennsylvania markup was rendered offline with external requests blocked; it is not described as PDF inspection. Four additional prepared HTML renders were not accepted as visually inspected.

[Validation](validation.json): full data/site/check passes with zero errors, 491 unchanged warnings, all 53 documented numbers matching and no tracked private source text. Answer replay applies zero changes; archive replay adds no versions. Landing/gap captions were checked in generated output.

Apply only the explicitly selected `pa-answers.json` and `va-answers.json` with `--baseline work/research/2026-11-06/pa-va-policy-review/baseline.json`; the sidecar enforces exact whole-row prior values and guarded idempotence. Do not apply worker recommendations automatically. Broad all-record freshness, complete amendment/omnibus/legal histories, finer precursor/resolution forms, remaining pipeline gates and final release remain open.
