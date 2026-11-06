# Ohio wave 5: Urbana and four Wilmington referendums

Status: scoped review, not canonical publication. Nineteen claims across six source versions are evidence-verified and archived. Five source versions are official primary/code-host material; one is a newspaper transcription, explicitly treated as secondary. Canonical totals remain36 reviewed measures /20 pending frozen candidate groups.

| Candidate | Official question/result reviewed | Limits |
|---|---|---|
| Urbana charter, Champaign County |2978yes/877no;77.25%yes;source Total3855;7197registered;8/8precincts;source turnout55.44%. |Full official ballot, definition and exemptions remain unrecovered. Recall and mayor contests are separate. No ballots/blank/under/over inferred. |
| Wilmington O-26-04 |119.373acres on SR730;739yes/2885no;Total3624. |Parcel rezoning, not a citywide ban; acreage is not a regulatory threshold. |
| Wilmington O-26-05 |65.29acres at1957SR730;732yes/2886no;Total3618. |Same source and scope limits. |
| Wilmington O-26-06 |191.12acres on McGuinn Road;724yes/2887no;Total3611. |Same source and scope limits. |
| Wilmington O-26-07 |170.11acres on US68South;716yes/2909no;Total3625. |Separate seed from Ohio006; not duplicated as a new discovery. |

The [official Clinton sample ballot](https://www.boe.ohio.gov/clinton/c/upload/Election_SampleBallots.pdf), physical page2 of96, contains all four Wilmington questions in one Wilmington1-A ballot style. Each is by petition, describes RR(Rural Residential) to LI(Light Industrial) rezoning, states a majority affirmative rule, and says yes approves/no rejects the ordinance. The ballot reports council adoption on February19,2026; signed original ordinances and legal effect are not independently accepted. Only the selected style/page was substantively reviewed, not all96pages. Exact question transcriptions preserve O-26-07's “in Wilmington” wording rather than copying the other questions' city-name phrase.

The [Clinton return](https://www.boe.ohio.gov/clinton/c/elecres/20261103results.pdf), physical page3, labels itself **Unofficial Canvass – Summary Report – Final**. Final is not certification. It gives7383registered and rounded50.89%turnout for each Wilmington contest; no municipal ballots, precinct counts, blanks or under/overvotes are inferred. County15623ballots/27368registration/36precincts are not municipal denominators. AB/ED/EV/PR column values are not under/overvotes. No source yes-percent is printed for these rows. A fresh retrieval matches the retained pilot body SHA; it is not evidence of revised totals. The fresh extraction version is separately fingerprinted.

The [Champaign return](https://www.boe.ohio.gov/champaign/c/elecres/20261103results.pdf), physical page3, is unofficial and timestamps22:12:08 on November3 without timezone. Urbana's data-center charter contest is separate from the mayoral recall and replacement election. County totals and rounded city turnout are not used to invent city ballots or residuals.

## Urbana text and scope gaps

The [local newspaper transcription](https://www.urbanacitizen.com/2026/10/26/anti-data-center-issue-requires-yes-for-passage/) reports a conjunctive exception for certain wholly owned dedicated single-enterprise facilities below7.5MW aggregate monthly demand or peak load, from any energy source/combination. The enterprise must not otherwise conduct the specified digital-information-services business. This is retained as a secondary reported exception, not primary exact wording, an operative exemption, a universal7.5MW definition or the25MW definition in other cities.

The official city site links the [American Legal code overview](https://codelibrary.amlegal.com/codes/urbana/latest/overview). Its local cutoff is July21,2026, state cutoff March25. It cannot establish November implementation. The pydoll county ballot-display attempt returned HTTP200 but `ok:false` with only an unselected form; its contents are not accepted as ballot text. Original failed evidence is preserved.

## Separate excluded Wilmington initiative

The recovered [Supreme Court slip opinion2026-Ohio-3663](https://www.supremecourt.ohio.gov/rod/docs/pdf/0/2026/2026-Ohio-3663.pdf), *State ex rel. Kidd v. Clinton Cty. Bd. of Elections*, case2026-1165, concerns proposed zoning Chapter1161 with data-center standards and private enforcement. It is distinct from all four voted parcel referendums.

The court's procedural account records July13petition transmission, July28determination of425valid signatures, August4auditor sufficiency certification, August12BOE refusal of placement and August26reaffirmance. On September18 the court denied mandamus to compel ballot placement. Sufficient signatures and auditor certification did not establish final placement. The opinion discusses the private-cause-of-action issue; this packet does not treat it as a general holding that all data-center regulation is unlawful. The recovered opinion is a slip version subject to formal revision; subsequent case history remains unreviewed.

`excluded-initiative-candidate.json` keeps this candidate in a separate qualification-history queue. It has no vote/result observation and is not added to the frozen56-group correspondence or counted as a defeated voted measure. Original proposal, petition, BOE and auditor instruments remain unrecovered.

## Reproduction and acquisition accounting

The initial review used all three configured Exa calls ($0.021 reported) and six of ten fetch slots, all terminal. Two fetches used pydoll: the unsuccessful county ballot form and successful code overview. No SerpAPI/model calls or original distributed-queue restarts occurred. Provider payloads, acquisition versions and failures remain private; existing client artifacts were not overwritten. The later [development-context follow-up](../wilmington-association-review/README.md) used two more slots: current usage is eight of ten, all terminal, with two remaining. Available slots do not imply completed endpoint coverage.

```bash
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python work/research/2026-11-06/ohio-ballot-wave5-review/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-005 \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-006 \
  --evidence-directory /data0/moratorium-refresh-2026/ohio-ballot-wave5-review
```

`validation.json` verifies19claims and six archived body/text versions. Publication still requires infrastructure-association review for generic Wilmington rezoning, field normalization, identity/publication gates and public-output checks. Final canvasses, original instruments, operative histories, implementation, court follow-up, all-record freshness, sibling consumers and release remain open.
