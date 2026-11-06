# Madison County township advisory questions

Scoped primary-source review of four distinct Illinois township questions on
November 3. This packet records the initial review; their [subsequent canonical
publication](../illinois-township-promotion/README.md) is separately recorded.
Neither step creates an enacted moratorium, development prohibition or instrument
link. Granite City Township remains distinct from the City of Granite City.

| Township | Yes | No | Source ballots cast | Source registrations | Precincts reporting |
|---|---:|---:|---:|---:|---:|
| Chouteau | 365 | 1,817 | 2,224 | 4,862 | 6 / 6 |
| Granite City | 1,959 | 5,703 | 7,819 | 17,759 | 17 / 17 |
| Nameoki | 602 | 2,117 | 2,796 | 6,391 | 8 / 8 |
| Venice | 311 | 978 | 1,350 | 3,289 | 4 / 4 |

Each question asks whether construction and operation of new data centers should
be permitted in its named township. All four appear under **ADVISORY** on the
[official county question sheet](https://www.madisoncountyil.gov/document_center/CountyClerk/2026%20Election/REFERENDA%20QUESTIONS.pdf?t=20260924105821428),
whose complete one-page image was reviewed. A yes vote favors advisory permission,
so its direction is `facilitates` and proposed mechanism `advisory_support`.
A larger no count is not automatically an enacted ban. Formal placement,
qualification, certification and passage/outcome evidence remain unresolved.
No numeric threshold, exemption or duration is specified by these questions;
that does not establish absence from independent ordinances.

## Fresh collection and report versions

A fresh bc-web/pydoll visit, using a headed browser and 2,000 ms settle, found
the [current results page](https://results.enr.clarityelections.com/IL/Madison/127555/web.345435/).
It displayed November 5, 2026, 5:41:25 PM, without an explicit timezone, and linked
report version **385789**. The linked [summary ZIP](https://results.enr.clarityelections.com//IL/Madison/127555/385789/reports/summary.zip)
was independently fetched. Its `summary.csv` bytes match the older version
**385067** exactly, although the ZIP bodies differ. The four counts are therefore
freshly reacquired but unchanged, rather than assumed current from a prior file.
Both observations and member hashes are preserved.

The CSV supplies ballot, registration and precinct fields in each named township
contest's rows. These are source-labelled values, not inferred yes/no sums.
No difference is assigned to blank, under- or overvotes. Full precinct reporting
does not establish certification or complete ballot accounting, so the packet
keeps certification and overall reporting completeness unknown.

Exa located the [county results page](https://www.madisoncountyil.gov/departments/county_clerk/elections/election_results.php),
which endorses the Madison County Clarity portal. Its links labelled “Official”
refer to the **2026 General Primary**, not the November general election. Those
links are not accepted as certification of these questions. This bounded search
is not evidence that no November certificate exists elsewhere.

Four of five allowed fetches and the single allowed Exa search were used. The
known search cost was $0.007; one fetch remains unused. Discovery snippets were
not accepted as source facts.

## ZIP extraction lineage repair

The completed worker had overwritten the client text files for both Madison and
Bloomington ZIP responses with extracted CSV, while the acquisition ledger still
recorded empty extraction. Both worker files were backed up and proved byte-for-byte
equal to the corresponding retained `summary.csv` ZIP members. Their ledger-described
empty acquisition text was restored only after checking the zero-character count
and SHA-256 of empty bytes. The CSVs were separately registered as reviewed
derivations. Raw retrieved payloads and acquisition ledgers were unchanged.

`zip-lineage-repair.json` records the reconstruction basis, backup locations,
member CRC/size/hash and derivation records. Bloomington's repair establishes
extraction lineage only; its electoral-government identity and substantive facts
were not newly accepted. The fresh Madison ZIP was extracted into a separate
file from the outset, preserving its empty client extraction.

Both original Illinois job evidence indexes now pass integrity checks. Thirty-three
archive versions were added across those jobs and the recovery run; that archival
work does not mean all archived sources were substantively reviewed. The five
versions used here have independent body/text archive checks. Seventeen claims
pass exact-text or reproducible visual evidence checks, including four explicit
advisory/polarity classifications.

## Additional sector lead and census boundary

The same primary sources contain a wind-and-solar local-zoning-control advisory
question, with source-reported **58,799 yes / 18,657 no**. It is absent from the
frozen v3 measure seed set. [Additional-lead evidence](additional-leads.json)
preserves two verified source claims, including the wording and counts, without
allocating a canonical identity or changing the census denominator. Its actual
electorate, qualification and policy direction require review: supporting local
zoning authority does not itself establish opposition to development or a ban.

The four township reviews are linked to their existing frozen groups, including
the already-reconciled Chouteau/Granite City duplicate observations. At the initial
review stage the ledger recorded **12 scoped publications / 44 pending groups**.
The subsequent publication records **16 scoped publications / 40 pending groups**.
These counts apply to the frozen baseline; the additional sector lead demonstrates
why it must not be presented as a complete election census.
