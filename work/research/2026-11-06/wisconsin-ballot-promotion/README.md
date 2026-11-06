# Wisconsin ballot publication candidate

Status: full preflight passed and canonical publication applied. Apply/replay receipts are in `work/audit/wisconsin-ballot-canonical-*-2026-11-06.json`.

The candidate uses the [primary review](../wisconsin-ballot-primary-review/README.md) and [source-qualified development context](../wisconsin-ballot-context/README.md). It adds three measures/provisions/jurisdictions/elections, **four** result observations, nine source versions and36claims, allocating218identities. All prior canonical rows are preserved exactly.

| Case | Result coverage | Accepted scope and limits |
|---|---|---|
| Janesville city, November3 |Whole city;16779yes/9932no;62.82%;40/40precincts;unofficial |Unsigned GM/JATCO proposal and clerk memo. Exact final ballot, yes-policy polarity, bindingness/current force unresolved. Exceeding450million rule versus under450million exception not repaired. Adjacent/phase and change/rejection rules retained. Advocacy account is context only; city is distinct from town. |
| Port Washington city, April7 |Whole city;2710yes/1371no;66.41%;8257registered;unofficial |Unsigned TID petition/draft, not final enacted text. Base-value equality versus strict project-cost test and disjunctive exception unresolved. TimesCast4201 and TotalVotes4081 retained separately;120difference not blank/under/over. No inferred precinct count or current litigation disposition. |
| Wrightstown village, August11 |Brown portion only;106yes/899no;43under/0over;1/1precincts |Post-county-canvass OFFICIAL RESULTS source label retained; no accepted referendum certification date. TotalVotesCast1005 versus ContestTotals1048; source yes percent10.11 uses latter, not yes/no. |
| Same Wrightstown measure |Outagamie portion only;45yes/134no;15under/0over;1/1precincts |Unofficial source; TotalVotesCast179 versus ContestTotals194; source yes percent23.20 uses latter. Different observation and status/date from Brown. |

Reporting scope is explicit for each observation and displayed publicly. The two Wrightstown rows are separate county parts, not two measures or two whole-village tallies. No computed aggregate observation is added. The [derived reconciliation](../wisconsin-ballot-primary-review/wrightstown-county-reconciliation.json) remains separately auditable with mixed-version limits. County precinct counts and source percentages are not combined into invented village statistics.

Wrightstown's signed resolution is a reproduction with an advisory question scheduled August11, correcting the frozen August8lead. It says substantially as printed and does not establish exact final ballot wording; a secondary apparent transcription omits large-scale. The advisory vote itself authorizes no contract, spending, zoning approval, agreement or utility extension. Original-host resolution/publication proof and full village certification remain open. The [separate county-certificate scope review](../wisconsin-canvass-scope-followup/README.md) does not justify assigning August18certification to this referendum; its claims are not promoted as result certification.

All formal outcomes, statutory passage denominators and operative restrictions remain unresolved. No local moratorium row, force event or project-policy link is created. Primary source-role labels distinguish unofficial/official county returns, unsigned proposals, reproduced resolution and secondary advocacy/reporting. Source vote totals retain exact labels and scopes rather than being renamed ballots.

After successful preflight/application/replay/census reconciliation and public build, expected totals are **44measures,45current result observations,51retained results,five current certified observations**, with **44published/12pending frozen groups**. Only39reviewed measures would be November3records;44overall must not be confused with external November44tallies. These are working-data increments, not a complete election census, all-record freshness update, consumer handoff or GitHub release.

Actual totals after application: **44measures,45current result observations,51retained observations,five current certified observations**. Frozen correspondence: **44published/12pending**. Wrightstown has two named county-part observations, not a single certified village tally.

Validation passed: `make data site check PYTHON=.venv/bin/python TODAY=2026-11-05`, exit0, zero errors/282 warnings,49 documented counts match and generated ballot summary consistent. Replay returned `already_applied`. All428 retained claim proofs verify; both legacy CSV byte hashes remain unchanged. The39November3measure subset is distinct from44overall. No GitHub release or sibling deployment occurred.
