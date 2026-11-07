# Source-reviewed compound clauses: Mandan and Harwood

Applied to sealed generation
`f8829533a5e363a1c50e5b82aadf6b48d5aee5d1ac0b45bf1ae602f6dfd57530`,
selecting validation profile **1.0.3**. The table fingerprint is
`cf4cd459aaf76cacdcfbcfef133b12ea17f789c65601a747209af7c9bfefd945`;
[application](apply.json) pins the publication receipt. This is publication of
descriptive proposed-source clauses, not acceptance of operative law or a passing
extraction evaluation.

| Existing provision | Selected clauses | Preserved limits |
|---|---:|---|
| Mandan future initiated ordinance | 7 | Primary-use/accessory definition; capacity-based Large-Scale definition; prohibition retains that defined predicate and capacity-or-demand language; both-below conjunction; no entitlement; objective aggregation and anti-evasion. Territory, existing operation and vested rights remain qualified. The definition/measurement interaction is unresolved. |
| Harwood proposed Article X | 5 | Any one of five major alternatives or at least two of six moderate criteria, with Industrial Development/discretionary municipal approval gates. The water comparison remains unsimplified text; common-plan/cumulative modification and effective-applicability limitations remain proposed. No capacity or operative date is invented. |

Exactly two provision records gain `condition_clauses` and append their new claim
IDs. **Twelve claims and fourteen scoped review decisions** are added. Every prior
record and every other field is unchanged, including both legacy CSVs, existing
flat threshold arrays, measures, results, source observations and historical
events. No election, result, source or legal instrument was added. All fifty
measures and their existing counts/statuses remain unchanged.

## Source and review evidence

Two independent CLI jobs requested `gpt-6.1-terra` and drafted 23 clauses from the
complete retained Mandan legal-page extraction and Harwood proposal. Both outputs
passed [mechanical checks](review-artifact-verification.json): source hashes,
exact quoted character spans, supporting-span bounds and both Python/canonical
condition schemas. These checks do not establish textual entailment.

The coordinator read relevant source context, visually reviewed all five Mandan
legal pages and Harwood physical pages3–4, and selected twelve clauses. Personal
petition pages1–3 were excluded. Separate Harwood absolute/percentage water
components were withheld as standalone clauses to avoid converting an unresolved
comparison into independent triggers. Alternative duplicate transcriptions were
not published as additional facts. [Selection](selection.json) preserves source
spans and interpretation limits; [claim bindings](claim-bindings.json) maps those
clauses to public claim/decision IDs. Each new claim also retains its clause's
interpretive limits. The structured tree describes selected conditions and does
not replace the complete proposed provisions or supply executable legal rules.

A third [Terra review](final-review.md) found no blocker within that descriptive
scope, checked all old-field preservation and accepted the proposed clause groups.
It did not claim legal truth, extraction accuracy or independent holdout results.
[Provenance](review-provenance.json) records exact report/event hashes and requested
models, without independently attesting provider model identity. Reviewer B
emitted a complete report and `turn.completed`, while its process wrapper returned
143; the completed artifact was independently checked and retained. No job was
restarted or represented as a clean wrapper exit.

[Source preflight](source-preflight.json) reverified all **540 claims** across
**144 source records** using 51 retained acquisition directories. This includes
all original 528 claims and twelve new claims. It is retained-version verification,
not source reacquisition, independent institutional corroboration or current-law
confirmation. Raw sources, model drafts and rendered pages remain private. The
November5 working cohort and original source observation timestamps remain intact.
No new search, fetch or extraction-provider request was made; the three CLI jobs
have separately unpriced model work.

## Publication, replay and remaining gates

[Preparation](prepare.py) only builds a candidate and scratch registry. The
[identity plan](identity-plan.json), [publication plan](publication-plan.json),
[source/field preservation](preservation-preflight.json), [preflight](preflight.json)
and application bind the reviewed transaction. Only 26 claim/decision identities
are allocated. The runner's workstation context is private; public exact replay
can use the core writer and retained snapshot directly:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python scripts/expanded_promotion.py \
  --candidate data/expanded-snapshots/f8829533a5e363a1c50e5b82aadf6b48d5aee5d1ac0b45bf1ae602f6dfd57530 \
  --plan work/research/2026-11-06/compound-clause-source-review/publication-plan.json \
  --apply
```

This replay is valid while that exact reviewed generation is selected; later
publications require historical receipt checking instead of moving the pointer
backward. Original application requires the retained private sources and visual
receipts. The published condition field still leaves absent legacy grouping
unspecified. Profile1.0.3 retains event-validity history and forbids downgrade.

Mandan/Harwood are known development sources. Source-adjudicated canonical changes
are distinct from a frozen model-extraction experiment. The historical quality
gate remains failed (32/36 supported, zero review-ready documents); a new frozen
evaluation/driver/cap manifest, broader freshness, consumer/copy reconciliation,
final release and hosted verification remain open. See [validation](validation.json)
for the resulting build/check and preservation evidence.
