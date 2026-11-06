# Retrospective pilot contract review — November 6, 2026

This freezes 17 section-11 case fixtures: nine source-backed canonical case groups, three additional source-review cases and five explicitly synthetic schema examples. The [manifest](manifest.json) pins the immutable baseline snapshot, baseline legacy CSV hashes, schema, exact record fingerprints and 16 source-review files. The [validation](validation.json) checks 23 explicit field expectations and twelve selected canonical measures: eleven November measures and Canterbury's March measure. Wilmington's four questions remain four measures sharing one election and jurisdiction.

This review occurred **after** previous prompt tuning and publication. It is not an unseen holdout or proof that the original pre-implementation/pre-bulk ordering was followed. No model extraction or discovery experiment was run here. Structural validation success is not an accuracy percentage, source-independent adjudication or current-force finding. The P4 holdout, metrics, disagreement, cost and quality-threshold gates remain open.

## Source-backed cases

| Case | Representation checked | Continuing source/factual limits |
|---|---|---|
| Peru | Proposed 180-day effective-date term; separate official tally | Binding adoption, wording/polarity, formal passage and operative effectiveness remain unresolved; the plan's initial description is not accepted fact |
| Wells | Certified observation; proposed June16 applicability anchor and defined aggregate area | Election date is not the term anchor; certification does not prove enactment or operative interval |
| Bloomington | Township identity; advisory proposal | City actor, township electorate and election administration remain distinct; original placement/boundary requirements remain open |
| Piqua | Named charter contest and unofficial counts | Full primary charter wording, polarity, predecessor relationship and force remain unaccepted |
| Grove City | Proposed binding voter gate, alternative thresholds and exemptions | Proposed terms/version differences are not operative law; future-project voting threshold is not amendment passage rule |
| Harwood | Proposed extra review; unofficial count observation | No inferred permit, project approval or accepted formal outcome from unfavorable counts alone |
| Wilmington | Four separately numbered parcel questions, one city/election | Secondary development context does not establish project identity, applicability, approval or cancellation |
| El Dorado | Data-center, BESS and explicit cryptocurrency-mining coverage in proposal; unknown term | Ten-year notice/proposal discrepancy remains; no generic BESS-capacity shortcut, chosen expiry or legal force |
| Earlier election | Canterbury March10 question | Not added to November totals; proposed permanent prohibition is distinct from adopted law |
| December pending | Clarksville's two financing-referendum source reviews | Conditional/conflicting December date is not a qualified final election date or November result |
| Council-only | Seattle original council act and reviewed duplicate retirement | Council adoption, mayoral approval and current force are distinct; no ballot is inferred |
| Portal failure | Miami unselected ballot form and Lucas challenge | Failed acquisition is not record absence or complete portal coverage |

All source-review cases retain their existing source limits. Review-only cases are not silently promoted into canonical elections or instruments.

## Synthetic examples and behavioral checks

The five folders under `synthetic/` are **artificial examples, not observed governments, votes or laws**:

- Failed qualification preserves the disqualified proposal without inventing a result.
- Amended certification preserves both observations while counting one current certified result.
- Mixed polarity remains `mixed`, separate from a multi-sector restrictive proposal.
- Distinct predecessor/replacement identities and events remain separate from ballot counts. This illustrates schema capacity; it does not resolve Piqua's real predecessor history.
- A scheduled December example has no result and is explicitly not acceptance of Clarksville's date.

The qualification case also exposed a consistency gap. An accepted `enacts` link could pass structural validation for a disqualified, withdrawn or canceled measure. The validator now rejects that contradiction even with scoped supporting decisions, while permitting a preserved `proposes` relationship. The new regression test exercises both outcomes. This does not claim that all thirteen section-11 behavioral gates are complete.

## Source and field-evidence review

[Source recheck](source-recheck.json) verifies retained source versions and all 511 baseline claim evidence bindings, including text/visual receipt checks. No sources were reacquired; matching source bytes and quote/render bindings is not field entailment or renewed legal acceptance. The initial use of an older Jay publication plan correctly stopped on its stale registry fingerprint; the successful check invokes the evidence auditor directly rather than the promotion replay shortcut.

El Dorado's existing three-sector value was confirmed against the unsigned proposal's physical page3, which explicitly includes cryptocurrency mining and separately addresses data centers and BESS. The frozen baseline's sectors decision cites the shorter notice. This is a field-evidence precision finding, not evidence that the sector value is wrong. The [separate correction packet](../el-dorado-sector-lineage/) appends a directly supported measure-scoped claim and superseding field decision; it preserves the old decision and field value. Its publication/validation receipts determine whether that correction is applied. The frozen manifest remains a record of what was found before the correction.

Reproduce the contract check without network/model calls:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python scripts/audit_pilot_contracts.py \
  work/research/2026-11-06/pilot-contract-review/manifest.json
```

The script is read-only unless an explicit output path is supplied. Missing cases, source-review drift, changed frozen records, wrong field expectations, invalid examples and cohort/dedup errors stop validation. The source-body recheck additionally requires the retained private corpus; its exact helper and full proof are preserved under `/data0/moratorium-refresh-2026/pilot-contract-review/` with public hashes, not redistributed bodies.

Historical replay uses the two pinned ID-only reference CSVs, including the retained moratorium alias. Those files are reference sets, not additional inventory records or status data. Legitimate future inventory edits do not alter this frozen baseline or require rewriting its expectations; current inventories remain subject to their separate live validation gates.
