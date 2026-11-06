# Ohio ballot wave 1 primary review — November 6, 2026

This reviews four pending candidates returned by the distributed `gpt-6.1-terra` job `ballot-oh-001`. Seven primary source versions support fifteen reviewed claims. No candidate is promoted automatically, and neither the canonical ballot count nor local moratorium count changes in this increment.

| Electorate and contest | Source-reported yes / no | Reviewed evidence and limits |
|---|---:|---|
| Ashville village referendum on a resolution | 331 / 1,469 | Official Pickaway feed recovered through pydoll; explicitly unofficial; 40 undervotes, 0 overvotes. Exact official question, resolution/project linkage and legal outcome remain open. |
| Conneaut city, Issue 10 charter proposal | 2,301 / 1,218 | Official sample ballot reproduces proposed Article XVI; county return explicitly unofficial. Certification, enacted charter and operative effect remain open. |
| Defiance city charter proposal | 3,823 / 2,083 | Official unofficial canvass reports 12 of 12 city precincts. Council agenda schedules a referral ordinance for first reading; actual adopted referral and exact ballot remain open. |
| Granville village charter proposal | 2,015 / 429 | Official unofficial canvass reports 98 undervotes, 0 overvotes. Filed issue summary identifies proposed Section 10.12 and three village precincts; full charter text, final ballot, qualification and current force remain open. |

## Conneaut proposal scope and column boundaries

The directly reviewed official sample ballot, physical page 44, labels the question Proposed Charter Amendment, Conneaut City, Issue 10. It supplies a majority-affirmative passage statement and the proposed Article XVI in full: prohibit construction of a defined data center; construction includes related preparations and modifications for a common purpose; digital-service facilities include equipment cooling; single parcels or contiguous, adjacent or otherwise aggregated parcels are covered; aggregate monthly demand or peak load must be **greater than 25 MW**, however derived from energy sources or their combination.

The proposal says the section is self-executing. The separate sentence saying an amendment would take effect immediately belongs to statewide Issue 3 in the left column. It must not be assigned to Conneaut. Neither sentence proves the city charter has actually become operative, and no force interval, adoption date or successor link is accepted here.

Conneaut's return, physical page 9, labels **Total Votes Cast 3,519** and **Contest Totals 3,585**. Its 64.18% yes figure corresponds to the latter; yes divided by yes plus no would be about 65.39%. Preserve both source totals and the source percentage. The 66 difference is not silently classified as blanks, undervotes, other votes or lost ballots. Countywide precinct/registration/ballot statistics are not city-specific denominators.

## Primary recovery and conflicts

Ashville: the earlier news observation of 330 yes / 1,468 no remains distinct from the official feed's 331 / 1,469. The official page labels the contest Referendum on Resolution Ashville Village, with a November 4 1:06:47 PM update and an unofficial-results banner. It does not supply the complete question or authenticate the underlying Resolution 06-2026/EdgeConneX linkage. No certified supersession or project cancellation is inferred. The page was acquired with bc-web's pydoll engine and a 2,000 ms settle.

Defiance: the newly recovered agenda's body schedules the meeting for **September 1**, despite the September 2 URL. It separately schedules a six-month data-center moratorium and a first reading of an ordinance proposing submission of charter Section 1.12 to the November 3 election. It records no adoption vote. The discovery label initiative and the older inventory's council-referral description remain unresolved until actual qualification/referral evidence is read. The county's 33 precincts, 25,923 registered voters and 14,795 total ballots are countywide; this charter contest reports 12 precincts and 5,906 Total Votes.

Granville: the county's filed-issues list, revised September 1 at 2:57 PM, describes the **village** Section 10.12 proposal and maps it to GRANVILLE VILLAGE A/B/C. Its text says City limits, which is retained as source wording rather than used to change the government type. A nearby township greenspace levy lists six precincts; it is another contest. The short summary does not resolve the secondary-reported 25 MW definition and is not a final ballot or adopted charter. The source labels the list Filed and subject to change. The original worker's Granville Township ballot does not establish village wording.

All four returns remain unofficial. A numeric yes majority, a precinct Election Night Complete label, a scheduled referral, or a proposed self-executing clause is not certification, a complete legal history or proof of current restriction.

## Acquisition and verification

The bounded follow-up used four Exa searches ($0.028 in reported fees) and eight fetch attempts. Two guessed sample-ballot paths returned 404; the actual Defiance lookup linked from its BOE homepage returned an unselected election form without a ballot. These failures remain in the ledger and do not establish absence of ballots. The remaining fresh sources include the two BOE homepages, the filed-issues PDF, the council agenda and the rendered Pickaway return. Retained official PDFs from the original Terra job supply the Conneaut ballot and three county result reports.

`review.json` pins source body/text hashes, exact text offsets, physical-page visual transcriptions and per-measure limits. `verification.json` records integrity checks and all fifteen claim proofs. Render hashes reproduce the reviewed pages; they do not independently perform legal judgment. All seven cited source versions are archived under the OH manifest; bodies, renderings and full source texts remain private.

Recheck without acquiring sources or changing canonical data:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/ohio-ballot-wave1-review/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-001 \
  --evidence-directory /data0/moratorium-refresh-2026/ohio-ballot-wave1-review
```

The frozen census remains 22 scoped publications and 34 pending groups. These four groups now have an explicit primary-review pointer while remaining pending canonical publication. The next publication must review identities and each accepted/unresolved field and preserve all previous rows; complete adopted texts, final canvasses and current legal force still require further evidence.
