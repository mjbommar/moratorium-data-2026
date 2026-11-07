# Ohio and Illinois policy source review

All 23 current rows were reviewed within source-specific limits: 12 Ohio and 11 Illinois. Two disjoint Codex CLI jobs were invoked with `--model gpt-6.1-terra`; a third reviewed the initial 54-field candidate set. Coordinator corrections after that review produce the final 60-field change set. [Scope](scope.json), [review reconciliation](coordinator-review.json) and [exact diff](exact-diff.json) retain the distinctions. This is substantive scoped review, not full-freshness acceptance of all fields.

## Accepted corrections

| Area | Result |
|---|---|
| Official source links | Fill all 23 previously blank primary-source URLs with corresponding government bill/history pages. |
| Ohio HB 646 | Replace the study-only description with the Senate-recommitted substitute, preserving strict thresholds, digital/mining uses, parcel context and electric-contract exceptions. |
| Ohio SB 190 / SB 374 | Distinguish the proposed termination of exemptions notwithstanding agreements from a deadline for entering new exemption agreements. Neither is an enacted moratorium. |
| Ohio HB 706 / HB 710 | Preserve the commission’s just-and-reasonable cost-recovery exception and both conditions for the prime-farmland exception. |
| Ohio HB 96 | Record the latest listed Senate veto-item action while leaving the item unidentified; distinguish section-level code context from bill-wide dates and current force. |
| Illinois HB 3574 / HB 4319 | Preserve engrossed procurement exceptions and post-contract credits, and the compensation proposal’s material/proximate harm condition. |
| Illinois SB 0094 | Preserve ownership and headquarters alternatives in the introduced foreign-company definition. |
| Illinois HB 5513 / SB 4004 | Record later co-sponsor additions, October 23 and September 2 respectively; these are distinct from substantive re-referrals. |
| Classification | Correct reporting versus incentive-support/restriction labels where supported. Mixed packages remain explicitly lossy classifications; filed replacement amendments without recorded adoption are not treated as adopted bill text. |

All 442 policy IDs and every other value are preserved. No disposition category, legal-effect status or typed effective date changes. Counts of local instruments, state policies, ballot measures and enacted policies are unchanged. The existing HB 96 mechanism remains inherited and requires item-level/session-law review. Party, activity, companion equivalence, later developments, current force and unrelated omnibus provisions remain qualified.

## Sources and review limits

The retained integrity audit verifies 55 body/text versions across four original job roots, with zero integrity issues. [Selected sources](selected-sources.json) pin 32 original versions used for this change. All are archived without publishing raw bodies. Three new Illinois status acquisitions use existing remaining reservations, including one pydoll rendering; the other sources retain earlier observation dates. The three selected new observations are November 7 UTC / November 6 Eastern. They do not turn unchanged historical fields into newly verified current-force facts. No new search or extraction-model calls were made.

Coordinator visual inspection covers eight Ohio PDF pages. The large omnibus documents were reviewed for the indicated data-center clauses, not exhaustively for unrelated provisions. Introduced, engrossed, recommitted and filed amendment versions without recorded adoption remain distinct. Government website text is primary evidence for the reported proposal/history; it is not a substitute for authenticated enrolled acts or complete current legal history.

## Application

Use the exact baseline sidecar; it supplies whole-row expected-prior protection:

```sh
.venv/bin/python scripts/apply_legislation.py \
  --answers work/research/2026-11-06/oh-il-policy-review/oh-answers.json \
            work/research/2026-11-06/oh-il-policy-review/il-answers.json \
  --baseline work/research/2026-11-06/oh-il-policy-review/baseline.json \
  --dry-run
```

Actual application records 60 changes across 23 rows with no conflicts. Replay makes no changes. Per-field expected values are supplied through this baseline contract, not an invented unsupported answer property. [Validation](validation.json) records the completed full data/site/check: zero errors, 491 unchanged warnings, all 53 documented numbers matching, no tracked private source text and exact source/archive/answer replay. Broader all-state freshness, complete legal histories, sibling final alignment and final release remain open.
