# Ohio wave 3 publication candidate

Status: full preflight passed and canonical publication applied. Apply and replay receipts are in `work/audit/ohio-wave3-canonical-*-2026-11-06.json`.

Four cases from the [primary review](../ohio-ballot-wave3-review/README.md): Oregon city (Lucas County), Pataskala city (Licking County), Perry village (Lake County), and Piqua city (Miami County). Proposed charter norms and unofficial election returns remain separate from certification, implementation and current legal force.

The candidate preserves all prior canonical rows and adds four jurisdictions, four elections, four measures, four provisions, four result observations, nine source versions and 38 scoped claims. Its identity plan allocates 245 identities. The publication plan pins the candidate fingerprint and a preview of the identity registry. The visual-review list inherits the prior publication's checks and appends the new claim-specific checks.

Oregon and Pataskala printed questions are transcribed from primary ballots; their construction definitions include monthly demand or peak load above 25 MW. Exact definitions remain in reviewed claims; full threshold and implementation normalization is unfinished. Perry's printed question concerns Fiscal Officer duties for village agreements involving hyperscale data centers and specified tax arrangements; the full ordinance, hyperscale definition and yes direction remain unknown. Piqua's official named charter contest supports topic and return identity, but full primary wording, placement and yes direction remain unknown.

All four returns are unofficial. Countywide numbers are not assigned to municipal electorates. Piqua's 6242 ballots are explicit; its duplicate overvote counter labels do not create two overvotes. Source-labelled vote totals retain their labels without assuming statutory valid-vote denominators. No local moratorium rows, certified results or operative restrictions are added.

Before publication: inspect preservation and field-support checks, apply the reviewed identity and publication plans, verify idempotent replay, update the frozen-census correspondence only after application, regenerate public derivatives, and record successful checks. Unverified fields must remain unresolved. This packet alone does not close comprehensive refresh or release requirements.

Canonical totals after application: **33 measures, 33 current result observations, 39 retained result observations and five current certified observations**. Frozen census correspondence: **33 scoped publications / 23 pending groups**. Legacy local and state-policy CSVs are unchanged. Public build/check results are recorded separately; publication of these records does not establish certification or current legal force.

Validation passed: `make data site check PYTHON=.venv/bin/python TODAY=2026-11-05` (exit 0), including all 49 documented counts and generated ballot summary consistency. `post-publication-check.json` confirms all 313 retained claim proofs are evidence-verified and both legacy CSVs remain byte-identical. Replay returned `already_applied`.
