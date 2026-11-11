# Ballot follow-up routing and duplicate prevention

Recorded November 11, 2026 UTC, following the November 10 accounting. This is an
operator overlay, not a new factual assessment or publication. Qualified post18 /
consumer V33 remains the delivered edition. All 97 original tasks remain intact:

| Operator state | Tasks | Meaning |
|---|---:|---|
| Prior-work check required | 89 | Inspect retained work before admitting collection; not an assertion that no work exists. |
| Distinct evidence required | 6 | Five measures already have bounded certification follow-ups; resume with a distinct record or explicitly admitted changed version/transport. |
| Not due | 2 | Preserve future operator priorities, which are not legal deadlines. |

`prior-review-register.json` pins prior reviews for Port Washington, Wrightstown,
Canterbury, Nottingham and Bethel, together with current measure/result identities.
Only certification/recount lookup is gated. Implementation and other obligations
remain separate. Scheduled canvasses, general clerk duties, sample ballots,
precinct completion and unchanged indexes do not establish certification. This
register is intentionally partial; it is not a comprehensive index of prior work.

`plan.json` preserves every original task in its original order. The builder fails
closed when the snapshot, due-work bytes, native task inputs, current result IDs,
measure row or prior-review bytes change. Rebuild explicitly after substantive
updates rather than carrying stale routing decisions forward.

## Duplicate request accounting

One Exa query and one HTTP fetch were made before finding the prior certification
follow-up. The query was `"Port Washington" "April 7, 2026" canvass certified
referendum`, restricted to the county/city domains. Exa returned six hits and
reported $0.007. HTTP fetched the already retained city elections index:
https://www.portwashingtonwi.gov/departments/city-clerk/elections .

The new extracted text is byte-identical to the retained November 10 capture
(text SHA256 `60957c6b73d77997cc99abeaa2a1e7a6d44f18a61dde9f2ff46b92a61774cbe5`).
Raw body bytes differ; that does not establish a substantive source change.
The index establishes no referendum certification. No new accepted source,
canonical result, certification, closure or headline change resulted. Private
attempts `091bb2271b98479980c267ef86c9125b` (Exa) and
`9c043f8b82404265a77994acf7e1a390` (HTTP) remain in the original persistent ledger;
caps were not reset. This duplicate was an execution error, not new research coverage.

The new opt-in `research_client.py fetch --new-source-only` guard rejects retained
request/redirect URLs and prior reservations within the same job before reserving
budget or calling the network. An actual probe against this retained URL was
blocked: the attempts ledger stayed byte-identical, retained body file set stayed
unchanged, and no network request or budget reservation occurred. URL aliases,
functional query variants and other running jobs still require operator review.
Explicitly admitted version/transport reviews can omit the flag.

## Verification and reproduction

Thirteen research-client/privacy/novelty tests passed, including concurrent
same-job reservations, retained redirects, explicit refresh, query distinctions
and corrupt-manifest rejection. `verify.py` replays the exact 97-task plan and
rejects five deliberately stale or overbroad register variants. Native and legacy
canonical files are unchanged by this work.

Run from the repository root:

```sh
.venv/bin/python work/research/2026-11-10/ballot-followup-operator-plan/verify.py
.venv/bin/python -m unittest discover -s tests -p 'test_research*.py' -q
.venv/bin/python scripts/build_ballot_followup_plan.py \
  --due-work work/research/2026-11-10/ballot-current-accounting/due-work.json \
  --review-register work/research/2026-11-10/ballot-followup-operator-plan/prior-review-register.json \
  --output /tmp/ballot-followup-plan.json
```

Broader factual QA remains open. This tooling-only change requires no new data
release or Pages deployment.
