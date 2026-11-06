# Ohio ballot wave 2 primary review — November 6, 2026

This reviews four pending candidate groups returned by the terminal distributed `gpt-6.1-terra` job `ballot-oh-002`. Eleven primary source versions support thirty scoped claims. Grove City's complete 13-page proposed charter text was read in native extraction; accepted claim scope is limited to the listed passages and visual transcriptions. This is not complete domain normalization, legal-validity review or canonical publication.

| Electorate | Source-qualified positive / negative votes | Primary evidence and remaining limits |
|---|---:|---|
| Grove City, Issue 28 | 11,317 / 9,411 | Official notice, certified-questions list and full proposal; fresh Franklin County Only unofficial return, 30/30 reported precincts, 638 undervotes, 2 overvotes. Final printed ballot, adopted charter, certification and current force remain open. |
| Hubbard city | 2,622 / 802 | County options explicitly say approval/rejection of the data-center ban; city petition notice and county listed question recovered. Complete ordinance, actual qualification/referral instrument, exceptions and operative effect remain open. |
| Monroe Township, Adams County | 148 / 100 | Official scanned return says For/Against the Zoning Resolution. Complete zoning plan, its data-center provisions, placement and restrictive/facilitating polarity remain open. |
| Monroeville village | 55 / 394 | Official return and filed-issues list explicitly classify an advisory contest. Exact official question, yes direction and adopted referral remain open. An advisory result does not enact a ban. |

## Grove City: proposal scope and source differences

The proposal applies to impact-defined heavy industrial development, including but not limited to data centers, server farms, power generation, warehousing and logistics. Its alternative initial tests are **at least 50 contiguous acres**, **more than 20 MW peak electrical capacity**, or **more than 500,000 gallons of water per day**. Aggregation includes common ownership/development agreement/operational purpose, certain separated parcels, all phases, and same/related-entity projects within one mile of a prior approval proposed within five years. Anticipated township-annexation acreage is addressed separately from actual annexation or jurisdiction findings.

The full proposal's cumulative expansion tests use **more than 10%** for acreage, peak electricity or daily water use. The fresh city FAQ instead says **10% or more**. The official notice describes a new Article XI, while the linked full proposal retains Article [X] placeholders. Neither discrepancy is silently harmonized into an accepted current-law boundary or article number. The city FAQ remains in pre-election future tense and is not a post-election implementation source.

Several different procedures have distinct anchors and effects:

- The proposed future project referendum requires a majority of votes cast (stated as 50% + 1). That is not independent evidence of Issue 28's own passage denominator or its exact printed ballot wording.
- Future project approval only permits normal zoning/permitting consideration; it does not guarantee permits. A failed project referendum carries a 24-month reapplication bar for the same or a Substantially Similar project. This is not a 24-month moratorium term for the amendment.
- The 180-day existing-facility Baseline Declaration window starts from the Article's unresolved effective date. Protection covers current operations only, not expansion or other duties. It is not an amendment expiration date.
- At-threshold operations owe quarterly reporting under the proposal regardless of registration. Registered facilities also face a 90-day ambient-baseline measurement window after the registration window closes.
- Material changes are measured cumulatively against the original Baseline. Continued baseline operations during expansion review and after a failed expansion vote are treated separately from the rejected expansion.
- Proposed township advisory fallback after 180 days without an intergovernmental agreement is a future process; it does not establish that any actual township ballot measure exists.
- The proposal's standard-adjustment clause permits certain Council action, while its general amendment clause reserves amendment/repeal to voters. Both clauses are retained; their legal construction and enforceability are not adjudicated here.

Noise, infrasound, lighting and vibration table values and the confirmation protocol are retained as proposed standards, not findings of actual violations. The remaining text on determination defaults/appeals, applicant funding, independent studies, quarterly oversight, penalties, financial security, private enforcement, conflicts, severability and anti-circumvention was read in the full native document; it has not all been normalized into typed domain fields or legally assessed. No claim of complete current-law exemptions or operative force follows from reading the proposal.

## Returns and denominators

All four returns remain unofficial. Adams' signed cover is expressly headed **Unofficial Certification of Results**; signing that form does not turn it into the final certified canvass. Its Monroe contest is physical PDF page 11, printed page 9, while the complete acquired payload has 16 physical pages.

Monroe reports Total Votes 248, Times Cast 255 / 401 (63.59%), and Unresolved Write-In 0. Preserve those labels; the seven-count difference is not assigned to blanks, undervotes or other votes. Nor are the slash values automatically relabelled as ballots cast and registered voters without source definitions. Approval of a generic zoning resolution is not automatically a data-center prohibition.

Monroeville reports Total 449, 760 registered voters and 59.61% turnout, with one of one precinct reported. The report does not explicitly provide a contest ballots-cast count. No count is reverse-calculated from the rounded turnout rate, and no residual is assigned to blanks or undervotes. Countywide 19,947 ballots, 35,656 registrations and 46 precincts are not village denominators.

Hubbard's source Total Votes Cast 3,424 and explicit approval/rejection labels are preserved. Hubbard City is distinct from Hubbard Township and the nearby township park-levy electorate. Grove City's report explicitly says Franklin County Only; no additional cross-county reconciliation or broader completeness is inferred from that label. Its earlier 54.61% news observation remains distinct from the official return's 54.60%.

## Acquisition, extraction and verification

The follow-up completed twelve fetch attempts and four Exa searches, with $0.028 reported Exa charges. HTTP recovery supplied official issue lists, municipal information and fresh proposal/result PDFs. The Grove proposal and the Franklin/Trumbull result payloads were independently reacquired and are byte-identical to the retained worker versions. The fresh city FAQ supplied the expansion-boundary difference.

The linked Huron ballot lookup was tested through bc-web/pydoll with an 1,800 ms settle but returned an unselected election form; the Adams HTTP lookup likewise yielded no selected ballot. Ballotpedia's HTTP acquisition returned a 202 challenge with no text. These failures remain in the ledger and do not establish absence of ballots, ordinances or litigation. No search snippet supplied an accepted fact. The original worker's four SerpAPI searches have unpriced cost and are not included in the follow-up's known Exa subtotal.

Separate registered derivations retain all 13 Grove native pages, all 16 Adams OCR pages and all five Huron OCR pages without overwriting original client text, including the two original empty-text versions. Extraction coverage is not substantive acceptance of every county contest. Selected worker images were independently read and their exact 140-DPI render hashes reproduced; newly rendered Grove/Hubbard pages use 150 DPI. All eleven cited source body/text versions are in the OH archive manifest. Full bodies, OCR and rendering artifacts remain private.

Recheck without reacquisition or publication:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/ohio-ballot-wave2-review/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-002 \
  --evidence-directory /data0/moratorium-refresh-2026/ohio-ballot-wave2-review
```

The verifier requires every claim to have located text or an accepted reproducible visual receipt, in addition to source integrity and exact archived versions. The earlier wave 1 verifier was given the same explicit guard and its existing fifteen claims rechecked.

Canonical counts remain **26 reviewed measures, 26 current results and five certified observations**; the frozen census remains **26 scoped publications / 30 pending groups**. These four groups now point to this review while remaining pending publication. Existing local moratoria in the four jurisdictions are possible predecessor/concurrent instruments, not accepted duplicate identities or successor links. Final canvasses, adopted texts, post-vote histories, implementation, complete clause extraction and the broader release remain unfinished.
