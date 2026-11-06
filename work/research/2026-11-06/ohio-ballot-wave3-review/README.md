# Ohio ballot wave 3 primary review — November 6, 2026

This reviews Oregon city, Pataskala city, Perry village and Piqua city from the terminal distributed `gpt-6.1-terra` job `ballot-oh-003`. Nine primary source versions support seventeen scoped claims. Visual question transcriptions normalize line breaks and quotation-mark typography and preserve the printed Pataskala heading Prohibiting of a Data Center. Exact official questions were recovered or directly read for the first three; Piqua's full primary ballot/charter text remains open. This packet does not publish canonical measures, certify results or establish current legal force.

| Electorate and contest | Official unofficial yes / no | Reviewed scope and remaining limits |
|---|---:|---|
| Oregon city, Lucas County, Issue25 | 4,994 / 3,235 | Official sample reproduces proposed Article XIII Section8 and >25 MW definition; official aggregate return recovered through HTTP. Qualification, final canvass, adopted charter and operative dates remain open. |
| Pataskala city, Licking County, Section11.09 | 5,418 / 1,941 | Official sample reproduces construction prohibition/definition and its own effective-immediately question; county report gives 474 undervotes and 1 overvote. Actual effect and certification remain open. |
| Perry village, Lake County, Issue16 | 946 / 140 | Official question concerns Chapter133.01 Fiscal Officer duties before certain hyperscale tax agreements. Complete ordinance, definition, guarantee/noise terms and policy polarity remain open. |
| Piqua city, Miami County, charter Data Centers contest | 4,061 / 2,027 | County report explicitly provides 6,242 ballots, 12,551 registered voters, 153 undervotes and 1 overvote. Primary Section138/25 MW wording, placement and yes policy direction remain unaccepted. |

## Proposal wording and identity

Oregon's four-page official sample contains Issue25 on physical page3. It proposes Article XIII Section8(A)-(D): construction prohibition; construction includes related preparations/modifications for a common purpose; the defined facilities are used primarily or exclusively for digital information services, including equipment cooling; single or contiguous, adjacent or otherwise aggregated parcels are covered; aggregate monthly demand or peak load must be **greater than25 MW**, however derived from energy sources or their combination. It says self-executing; it does not supply an accepted operative date. Oregon city is not Oregon state.

Pataskala's official two-page sample prints Section11.09(A)-(D) in its own right-hand question block on physical page2. Its greater-than25-MW aggregate demand/peak-load definition is directly reviewed. Its own adoption question ends **effective immediately**, and its proposed section says self-executing. Those proposal clauses remain distinct from certification, actual charter adoption/effect, the other Pataskala charter questions, and statewide Issue3's separate immediate-effect language. The source questions do not establish a general prohibition on operating every existing facility.

The community publication PataskalaOH.com was not established as the City's publisher and supplies no accepted primary claim here. In particular, its descriptions of different effective dates for other charter questions are not substituted for the data-center question's own official wording. The newly recovered county ballot and official county return supply the accepted evidence.

Perry's official master sample contains Issue16 on physical page326, printed page2 of2 for Perry Village AA. It asks adoption of an ordinance amending Chapter133.01, Established; Power and Duties, concerning Village Fiscal Officer duties before signing agreements with a hyperscale data center involving tax abatements, PILOT Programs or a special tax designation. This is not another copy of the 25 MW construction-ban proposal. Neither the hyperscale definition nor the exact financial guarantee, fine or noise rules is supplied by this short ballot description; no numeric threshold or restrictive/facilitating polarity is imported from secondary coverage.

The village's ordinance index separately describes Ordinance2026-13 as a one-year application moratorium excluding Champion Farm. That is a different council instrument, already represented in the legacy inventory, rather than Issue16. The village-linked code host is locally current only through November20,2025, despite a 2026 Replacement Pages heading and later state-law cutoff. It cannot establish implementation of the November2026 ballot proposal. The publisher's City label does not change the official village electorate. The legacy record's precise force interval and independently verified Lake County coordinates remain open.

Piqua's official return establishes the named Data Centers charter contest and its counts. Its separate recall elections are not infrastructure measures. Section138, the complete definition and the precise proposed legal effect were not accepted merely from secondary reproductions.

## Counts, coverage and source times

All four official returns expressly identify unofficial results or an unofficial canvass. No final certification, formal reported/calculated outcome, actual operative interval or measure/instrument successor link is accepted.

| Contest | Source-labelled quantity | Value |
|---|---|---:|
| Pataskala Data Centers | Total Votes Cast | 7,359 |
| Perry Issue16 | Total Votes Cast | 1,086 |
| Piqua charter Data Centers | Total | 6,088 |
| Piqua charter Data Centers | ballots | 6,242 |
| Piqua charter Data Centers | registered voters | 12,551 |

Oregon's city aggregate was selected from the summary contest node, not the thirteen repeated precinct contest sections. The source header's 280 county precincts, 155,454 ballots and 292,699 registrations are not assigned to Oregon city. Its countywide Absentee Ballots: Partially Reported label also prevents treating 100% precinct reporting as proof of a completed final count; city-specific reporting completeness remains unresolved.

Piqua prints both 1 over voted ballots and 1 overvotes. Those are two labels, not two additional overvotes. Its 6,088 yes/no votes +153 undervotes +1 overvote reconcile to the explicitly printed 6,242 ballots; no blank count is inferred. Countywide 46,122 ballots, 77,679 registrations and87 precincts remain separate. Perry's one of one precinct and Pataskala's own data-center row are likewise not replaced with nearby contest or countywide totals.

Source clock labels remain literal with unspecified timezone; no UTC publication time is invented. The freshly reacquired Pataskala, Perry and Piqua reports are byte-identical to the retained worker payloads, as pinned in `source-version-check.json`; this is an independent reacquisition, not independent corroboration by a different publisher.

## Collection and reproducibility

The follow-up completed four Exa searches ($0.028 reported charges) and sixteen fetch attempts. Newly recovered primary sources include the Pataskala sample, Lake County's 340-page master sample and Oregon's HTTP return. Only the identified proposal/return pages were substantively accepted; collecting a 340-page file does not imply review of all its ballot styles.

The initial pydoll acquisition of the Oregon feed was flagged as challenged and remains recorded as unsuccessful. An ordinary HTTP acquisition succeeded. Default readability extraction on that successful response still returned only the contest menu, so a separate full-visible-HTML derivation was registered, preserving the original extraction and all acquisition flags. The accepted counts are proved against that successful HTTP body, not by silently changing the failed browser attempt. Full retained HTML includes repeated precinct material; claim offsets and the summary node distinguish aggregate values.

Miami's ballot lookup returned an unselected form with no chosen ballot. The Lucas elections homepage returned a403 challenge. Those failed acquisitions remain in the ledger and do not establish absence of public records. The village-linked code overview was also tested with pydoll at1,800 ms settle; its explicit older local cutoff is retained. No search snippet supplied an accepted fact.

`review.json` pins the source versions, exact located excerpts and reproducible150-DPI visual transcriptions. All nine cited body/text versions are archived under OH. Bodies, full text, scanned pages and renderings remain private. The additional fetched moratorium scan is not treated as a new reviewed source merely because its URL returned200; its existing legacy identity is preserved.

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/ohio-ballot-wave3-review/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-003 \
  --evidence-directory /data0/moratorium-refresh-2026/ohio-ballot-wave3-review
```

Canonical totals remain29 reviewed measures,29 current results and five certified observations; the frozen census remains29 scoped publications /27 pending groups. These four pending groups now have primary-review pointers. Canonical identity/field review, complete remaining proposal/qualification text, adopted implementation, all-inventory freshness, sibling handoff and release remain unfinished.
