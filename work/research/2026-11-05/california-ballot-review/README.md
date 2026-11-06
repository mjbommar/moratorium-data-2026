# California ballot evidence review

Scoped primary-source review of two distinct permanent-prohibition measures.
Neither is a new temporary moratorium row. This packet updates candidate
evidence; canonical promotion and complete legal-status histories remain open.
The frozen census payload is unchanged, and the correspondence ledger still
reports ten scoped canonical publications and 46 pending groups.

## Results and observation scope

| Measure | Election | Reviewed yes / no | Status and limits |
|---|---|---:|---|
| Alhambra DB | November 3 | **15,237 / 3,132** | County snapshot updated November 5, 16:34:21; certification and reporting completeness not established |
| Monterey Park NDC | June 2 | **10,388 / 1,372** | Final official canvass, county and city-clerk certification, and council declaration reviewed |

The Alhambra snapshot was acquired afresh through **bc-web/pydoll**, with an
explicit 1,500 ms settle and headed browser. It replaces the worker's November 4
candidate observation of 13,314 / 2,889 as the newer candidate evidence. Both
source versions remain retained. The latest source reports 82.95% yes; the
reported yes/no sum is 18,369, not an asserted ballot/turnout denominator. Blank
votes and ballots cast remain unknown. Do not silently carry forward the worker's
`partial` reporting flag: the reviewed current page establishes neither partial
nor complete reporting, and no final certification was acquired.

For Monterey Park, the entire eleven-page city certification/ordinance packet
was visually reviewed. Page 8 explicitly identifies the Measure NDC contest and
reports a grand total of 32,781 registrations, 12,381 ballots cast, 10,388 yes and
1,372 no. The citywide ballot total is also stated separately in resolution
section 2. This contest-labelled canvass supplies the context missing from a
generic election-total statement. Neither the 621 difference from yes/no nor any
other arithmetic is accepted as blank, under- or overvotes. County text returns
independently corroborate the yes/no transcription and 88.33% yes. The native/OCR
table text misreads digits, so the page image controls the reviewed table values.

## Alhambra instruments and source limitations

[Official county returns](https://results.lavote.gov/text-results/4348) provide
the actual Measure DB designation and question. A yes vote adopts an ordinance
affirming a council-adopted prohibition and restricting data centers in every city
zone. The city attorney's analysis says a failed measure leaves the existing
council ban in place, subject to later council action. Preserve this distinction
from a new ban created only by the election.

The calling-ordinance text and analysis are **DOCX**, not PDFs, despite their
DocumentCenter URLs. They contain unsigned/blank certification and vote fields;
the analysis also has an unfinished measure label and phone placeholder. Their
proposed November adoption language does not certify voter enactment.

Exa located separate official minutes, which were fetched through bc-web:

- [June 22 minutes](https://www.alhambraca.gov/AgendaCenter/ViewFile/Minutes/_06222026-1593),
  pages 35–36, item 51: council adoption of predecessor Ordinance O2M26-4863,
  with five ayes and no noes or absences. This establishes an adoption observation,
  not the complete content/current force of that broader zoning amendment.
- [July 27 minutes](https://www.alhambraca.gov/AgendaCenter/ViewFile/Minutes/_07272026-1609),
  pages 14–15, item 20: actual adoption of election-calling Ordinance O2M26-4868
  and consolidation Resolution R2M26-26, with five ayes and no noes or absences.
  The narrative has a November 2 date, while the adopted action explicitly says
  November 3 and agrees with the actual county contest. Preserve the discrepancy;
  do not invent a rescheduling event from it.

The proposed definition excludes facilities only where they are incidental to
another primary use **and** strictly support that use's on-site operations. No
acreage threshold is stated in the reviewed Alhambra definition. Voter approval,
execution, later codification and current legal status require further review.

## Monterey Park dates and clauses

The [city certification packet](https://montereypark.ca.gov/DocumentCenter/View/19275/2026-R56-Certifying-Election-June-2-2026)
contains separate acts that must not collapse into one date:

| Event | Date | PDF page |
|---|---|---:|
| County certificate of canvass | June 26 | 6 |
| City-clerk certification | June 30 | 4 |
| Council Resolution 2026-R56 declaring the result | July 1 | 1–3 |
| Signed Ordinance 2280, printed adoption/execution date | July 2 | 11 |

Resolution R56 says NDC received the required majority for adoption. Ordinance
2280 amends the General Plan prohibition across land-use designations. Its data
center definition includes facilities occupying **one or more acres**. The
smaller-facility exclusion requires both **less than one acre** and accessory or
incidental use. Preserve land area rather than substituting building floor area.
Section 2 directs implementing zoning action; exact implementation history is
still open.

Section 9 supplies a ten-day rule tied to **City Council certification**. County
certification, the city clerk's certificate and the ordinance's printed execution
date are distinct observations. No operative-date/legal-force interval is accepted
by this packet. Ordinance 2280 also remains distinct from council Ordinance 2278
and prior moratorium Ordinances 2272/2274. Later amendments, implementation and
challenges were not comprehensively searched. The ordinance's section 9 calls
June 2 a general election while the result resolution/canvass call the municipal
election special; preserve the source terminology without changing the confirmed
June 2 election date.

## Verification and remaining work

`review.json` pins eight reviewed source versions and seventeen claims, including
nine value-specific visual receipts. The evidence audit locates supporting text
or reproduces the reviewed page image for every claim. All eight body/text
versions were checked against the source archive; three new archive versions were
added, with raw copies remaining private. Original client text was preserved
when separately registering full native layout extractions of the minutes.
Only the identified minutes pages received substantive review.

The recovery budget used four of four fetches and one of one Exa search; known
search cost was $0.007. The source-qualified candidate reviews are linked from
the census correspondence ledger. They do not close canonical publication,
full-document model extraction or current legal-force review.
