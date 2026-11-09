# Process reset: minimize elapsed time without losing quality or coverage

> November 9 update: the user explicitly authorized publishing the current state with qualifications on pending QA, followed by continued checking and clearing outstanding questions. [v2026.11.9 is published](https://github.com/mjbommar/moratorium-data-2026/releases/tag/v2026.11.9). That authorization supersedes the publication prerequisite below; it does not declare failed experimental trials successful. Source review and guarded correction requirements continue.


Date: 2026-11-08
Status: implementation started after the user reactivated the goal on November 8.

This replaces the execution strategy, not the scope of
[the research and ballot expansion plan](research-and-ballot-expansion-plan.md).
The objective is the shortest end-to-end wall clock for a complete, evidence-backed
refresh and release, without materially reducing accuracy or coverage. Model cost
and token volume are constraints to observe, not the optimization target.

## 1. What changes immediately

The previous 591-task queue of three-record, every-column reviews is retired as the
mandatory execution path. Preserve its outputs and interrupted attempts. Do not
restart its controllers. A task's completion is not a record's freshness acceptance.

The main delays were repeated reading of the same sources, verbose repeated
26-field row dumps, high reasoning effort for every task, serial coordinator
rechecking, and regeneration/deployment of tiny correction batches. Existing
research and approvals were not being reused systematically. Changing models alone
will not fix that: recent CLI workers were already using GPT-6.1 Terra.

Replace that sequence with four overlapping activities:

1. Account for every record using existing research and actual freshness gaps.
2. Collect each necessary source once, then share its immutable version.
3. Independently review material factual/legal decisions, not mechanical metadata.
4. Merge validated changes in substantial batches while preparing all delivery surfaces.

No source collection, model evaluation, data promotion, consumer mutation or release
publication resumes merely because this document exists.

## 2. Scope and gates remain intact

Keep all current raw local and state-policy IDs, all five sectors, all 50 states,
new-discovery coverage, the entire ballot seed/current-measure population, identity
reconciliation, source provenance, consumer dispositions, prose/figures, the GitHub
release and actual download/hosted verification. Preserve historical observations
and releases. Do not turn unofficial results into certification or electoral
approval into operative law. Do not turn project association into applicability.

The latest committed starting point is `15c344ca108efd01f66a14ad5a5495407a2bc3e4`:
1,330 local observations, 447 raw policy observations and 53 canonical measures.
These are different denominators. The current policy scope registry has one
exclusion and 446 unreviewed observations; the candidate pool is not accepted scope.
The separately frozen 1,772-ID baseline and subsequent five policy additions remain
traceable. Revalidate these starting facts at resumption rather than assuming them.

The original P4 extraction thresholds, calibration/holdout separation, trial caps,
review requirements and unresolved delivery gates are not silently waived. A manual
reviewed data path can progress while automation is evaluated, but the full goal
cannot be marked complete with an explicitly required gate still unfulfilled.
Any proposal to change such a requirement must be explicit, not hidden in batching.

## 3. Model and reasoning policy

Use `gpt-6.1-terra` for collection interpretation, independent review, bounded code
work, reconciliation and publication copy. This model is present in the local Codex
model registry checked November 8 and in the
[official model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-terra).
Before starting a new cohort, resolve the newest available Terra from the current
CLI registry, record the selected model/client version, and pin it for that cohort.
Do not silently fall back to Sol or Astra. Report an availability problem instead.

Set reasoning explicitly rather than inheriting product defaults:

| Task | Initial effort | Escalation |
|---|---|---|
| Evidence indexing, straightforward extraction, ordinary writing | medium | high for a demonstrated ambiguity |
| Reconciliation of existing accepted evidence | medium | high for conflicting versions or identity |
| Material legal/electoral decisions and disputed PDF interpretation | high | adjudication against primary evidence |
| Derived counters, schema checks, hashing, joins and file generation | deterministic code | no model call |

Medium effort is a starting configuration to measure, not a claim of equal quality
on every task. Retain high effort for known difficult cases. Previously exposed
examples may test workflow regressions; they cannot become a fresh P4 holdout.
Changing an API extraction model requires its own pinned configuration and proper
evaluation; a CLI model preference does not validate a different production profile.

## 4. Establish the remaining work once

Build one compact record ledger from existing CSVs, canonical tables, research
packets, source-attempt journals and approvals. Reuse the existing scripts and
stores. Do not create another general orchestration framework.

For every in-scope ID, record:

- Dataset, stable ID and current-row hash; keep the complete baseline row outside
  the model output so it can still be checked before application.
- Latest relevant supported observation and its source version/role.
- Existing acquisition attempts, actual dates, failures and remaining caps.
- Existing primary and independent decisions and whether they still match the row.
- The precise unanswered freshness question and required endpoint, if any.
- Material proposed changes, review state, and next action.

Join accepted evidence by exact ID, source version and decision scope. A batch-wide
hash, a source URL somewhere in a directory or another model's agreement is not a
freshness proof. Reuse valid work; explicitly reconcile stale guards rather than
replaying old values. Preserve interrupted outputs without counting them complete.

Use a mutually exclusive terminal-disposition partition:
`corrected_resolved`, `confirmed_unchanged`, `superseded_duplicate`, `unresolved`,
`not_attempted`. Track `has_changes`, `retrieval_succeeded`, `source_unavailable`,
review completion and publication separately. For example, a corrected historical
term with unknown present force is changed but still unresolved for current force.
Publish clearly defined denominators rather than adding overlapping counters.

Every record still receives a supported freshness disposition. An old source
reread is not a fresh confirmation. Unresolved dispositions require real documented
attempts/limitations and the earlier supported date; they are not a shortcut for
unperformed work. Immutable coordinates and editorial metadata need not be
semantically re-researched on every pass unless evidence or identity raises a concern.

Freeze the release's actual research cutoff and collection window at resumption,
with source-specific observation times where necessary. Do not move the completion
boundary forward on every status update and repeatedly reopen an otherwise closed cohort.

## 5. Productive batches and shared collection

Group work by jurisdiction, source family and question. Start ordinary batches at
15–30 IDs, with smaller groups for dense or disputed legal histories. Pack source
context to a bounded size rather than forcing the same count on every job. Avoid
mixing unrelated jurisdictions merely to fill a batch. A long case becomes an
explicit specialist item; it must not force the other completed items to restart.

Models return compact dispositions and actual proposals, not three copies of every
baseline row. A proposal needs ID, baseline hash, field, exact before/after, evidence
version, literal locator, rationale and uncertainty. The merge step reconstructs and
checks the full candidate row. Additional coupled changes must be explicit.

A shared acquisition queue deduplicates requests while preserving requested/final
URLs, capture context, event/publication/acquisition clocks and version lineage.
Reuse the same source body across records and across primary/review jobs. Share
prepared PDF page renders when they are tied to the original body hash; inspect
actual pages for signatures, draft/final distinctions and extraction completeness.
An empty text extract does not mean a blank original.

Use existing bc-modules capabilities:

- Exa/Serp and provider-specific query variants for genuine discovery gaps.
- bc-web HTTP collection first, Pydoll escalation for missing rendered content or
  portals that require a browser; ordinary PDFs do not require browser repetition.
- bc-research collection/document handling, and existing evidence/store adapters
  for immutable bodies, citations and provenance.
- Existing recorded API/browser tests as evidence of capability; repeat them only
  for a regression or an actual research need, not to demonstrate the tools again.

A cached response does not renew origin or factual currency. A hash verifies bytes,
not legal support. Respect all existing provider/run caps and reservations. Never
create a new namespace, switch providers or reset a ledger merely to evade a spent
cap. Route genuine exhausted/blocked cases with their limitations and any explicit
additional authorization needed. Raw bodies and private derivations remain private.

## 6. Parallelism and allocation

Remove the arbitrary three-CLI-worker ceiling. The proposed initial operating
range is 8–12 Terra jobs, subject to actual account, provider, memory and I/O limits.
This is a configuration to validate, not a claim that the account admits 12 jobs.

A twelve-job allocation would be:

| Lane | Jobs | Work |
|---|---:|---|
| Freshness/discovery | 6 | Two local, two state-policy and two ballot/election jobs; redistribute as queues drain |
| Independent evidence review | 3 | Material decisions from all datasets; disagreements have priority |
| Delivery/consumer reconciliation | 2 | Copy, figures, consumers and package preparation on owned paths |
| P4 required closure | 1 | The smallest remaining evaluation/integration work needed by the original gate |

A single canonical writer applies approved batches. Other jobs write separate
packets or isolated owned paths/worktrees. In particular, preserve the concurrent
`datacenter-paper-2026` campaign and its dirty files.

Separate model concurrency from collection concurrency. Begin with bounded shared
HTTP admission and at most two browser contexts; raise those only when actual
service and machine behavior supports it. Model workers should not all start a
browser or duplicate the same fetch. Honor provider backoff and existing budgets.

Use the first productive work after authorized resumption to compare admission at
4, 8 and, if supported, 12 jobs. This must finish real outstanding work rather than
become another throwaway pilot. Measure validated dispositions/hour, review backlog,
p95 task latency, retries, throttling, browser wait, merge delay and quality flags.
Increase admission until throughput stops improving or limits/quality require
backoff. Do not guess that more jobs automatically improve elapsed time.

Round-robin states and sectors within lanes. Keep local, policy and election work
moving concurrently; do not defer all policy records behind the local inventory.
Use workload stealing between lanes when a worker would otherwise be idle.

## 7. Quality controls without duplicated serial passes

### Material decisions: independent evidence review required

Independently review every new or changed material assertion: identity/merger,
adoption/repeal/status, term/effective/expiry dates, scope/exemptions/thresholds,
qualification/question wording, vote counts, certification, bindingness,
implementation and project applicability. Reconfirming current legal force is also
a material assertion even when the stored value does not change.

Use a different Terra job with the actual sources. For difficult cases, have it
extract the relevant fact before seeing the proposed answer, then compare. Require
source/role/locator support; agreement alone is insufficient. Escalate conflicts,
contradictions and ambiguous signatures to coordinator adjudication. Do not require
a third complete reread by the coordinator for every uncontroversial accepted cell.
The coordinator owns exceptions, cross-record consistency and canonical application.

### Carry-forward and mechanical work

Script exact row guards, typed dates/durations, arithmetic, marker counts, identity
uniqueness, supersession, scope filtering and source-reference integrity. Reuse
previously accepted spans and reviews where their actual scope still applies.
Do not spend model calls explaining unchanged latitude, file size or counters.

Audit a stratified sample of lower-risk unchanged/carry-forward decisions, plus all
risk flags. This sampling does not replace any required record's freshness check
or the independent review of current-force assertions. A material error expands
review to the affected cohort/source family; it does not silently pass the rest.

Retain sentinel checks for known failure modes: signed Monterey versus unsigned
Covina copies, Pima direction-to-draft versus adoption, same-name jurisdictions,
month/year versus fixed days, missing-source versus no action, and unofficial versus
certified results. Sentinels are regression checks, not an unseen extraction holdout.

## 8. Merge and validation cadence

Apply a substantial reviewed batch, initially around 100 record dispositions or a
bounded hourly checkpoint, rather than committing and deploying every few rows.
Urgent material public corrections may still be published sooner. Record the
before/after deltas once; derive statistics and prose counters once per checkpoint.

Per batch run only affected checks: schema, guards, IDs, coupled typed fields,
source/decision links, arithmetic, scope registry, and the relevant regression tests.
Regenerate each affected surface. The existing timeline byte check must run when
normalized dates change. Stop cosmetic rewriting and unrelated infrastructure work.

Reuse validated immutable generations when their bytes, schema and validator have
not changed. Do not recursively replay all 43 historical generations for each raw
prose edit. Full historical integrity remains required at the frozen candidate,
and protocol/schema/history changes invalidate the affected cached validation.

At one frozen release candidate run the complete data/site/figure/table checks,
full historical replay, clean portable restoration and handoff verification. Then
verify remote refs, release downloads and required hosted outputs against that exact
manifest. If a relevant input changes afterwards, invalidate the affected proof.
Do not present an earlier portable checkpoint as the final current asset.

## 9. Keep delivery on the critical path

Prepare the release title/body, change ledger, freshness funnel, unresolved-case
appendix, citation metadata, summaries, figures and consumer matrix in parallel
with research. Draft claims carry explicit dependencies; do not fill unknowns with
assertions just to finish copy. Only freeze numbers after canonical merge.

Each of the seven consumers needs an explicit, evidenced disposition:
`moratorium-paper`, `servercountry.org`, `datacenter-data-integration`,
`fightadatacenter.com`, `datacenter-paper-2026`, `datacenter-2026-book`, and
`michaelbommarito.com`. Either update and verify the affected surfaces, or retain an
explicitly dated historical edition where the original scope permits that. A local
notice that readers cannot actually see is not verified delivery. Existing project
and disclosure corpus cutoffs remain separate; this does not silently launch or
claim a full project-corpus refresh. New project claims still need their own evidence.

P4 work runs alongside this flow with a concrete list of remaining requirements,
a fixed intended model/settings profile, existing thresholds, frozen references,
fresh unexposed evaluation and retained spend. Do not reopen transport architecture
unless an observed defect blocks an actual gate. Do not call offline/mock tests an
actual quality pass. If this required lane remains blocked, identify the exact
unmet requirement; do not claim the whole goal complete or silently waive it.

## 10. Minimal implementation after resumption

Implement only the wiring needed to use existing tools:

1. One ID/evidence/disposition ledger with source-specific freshness dates.
2. Reconciled reuse of existing completed packets, approvals and interrupted attempts.
3. Source-grouped worklists and compact result contracts.
4. A configurable launcher and shared collection admission using existing mechanisms.
5. A merge gate for approved deltas and a single release/consumer checklist.

No new general framework, bulk rewriting of historical artifacts, new model SDK,
large source migration project or more elaborate reporting system is a prerequisite
unless a concrete release requirement cannot otherwise be met.

Log model, task IDs, input hashes, start/finish times, request/cap state, review result
and application state. Validate the actual completion envelope and ID coverage,
not just the existence of a last-message file. Preserve cancelled work as interrupted.
On controller loss, inspect actual processes/handles and adopt live work; do not
blindly relaunch. During the user's pause, no controller may admit research jobs.

## 11. Completion and ETA

The full objective is unchanged. Completion requires an accounted-for population,
properly researched dispositions and bounded unresolved gaps, independent review
of material assertions, all required model/evaluation gates, coherent derived/copy
surfaces, explicit consumer delivery, and the published verified release. No graph,
review count, test suite or green package verifier alone proves that end state.

Do not reuse the old 591-job count to estimate this design. After the evidence reuse
pass and productive concurrency measurement, estimate the critical path as the
maximum remaining lane time plus the unavoidable final merge/verification time.
Report assumptions, measured throughput, stragglers and unresolved external gates.
Do not promise a speedup or a completion date before measuring the new workflow.

## 12. Resume boundary

The user reactivated the goal on November 8. Work is resuming under this revised
process; the retired controllers remain stopped with admission zero. The initial
productive cohort uses Terra for evidence reuse, ballot accounting, consumer
integration and the required P4 gap in parallel. Reactivation does not erase
provider/model-evaluation spend or authorize bypassing existing caps. New
collection admission must respect the original ledgers and explicit scope.
