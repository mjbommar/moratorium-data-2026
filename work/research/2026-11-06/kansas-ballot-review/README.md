# Kansas five-measure primary review — November 6, 2026

This reviews the three Kansas discovery seeds and two omission-recovery seeds together: El Dorado, Emporia Question 2, Emporia Question 3, Ottawa and Americus. Emporia's two questions are distinct measures sharing a city/election; Americus is another city. Neither city is Lyon County's unincorporated territory, and Ottawa, Kansas is distinct from Ottawa, Illinois.

Nine primary source versions and fourteen scoped claims are pinned in `review.json`, with reproducible text/visual checks in `verification.json`. Fresh bc-web/pydoll acquisitions include Emporia's official ballot-information page and Butler County's election-night feed, both with 1,800 ms settle; fresh HTTP acquisitions include two county return PDFs and El Dorado's full petition/proposed ordinance. Earlier official resolutions/notices remain separately versioned evidence. The distributed `gpt-6.1-terra` candidate returns supply leads, not accepted legal conclusions.

| Measure | Source-qualified yes / no | Primary evidence and unresolved fields |
|---|---:|---|
| El Dorado mixed data-center/BESS proposition | 2,972 / 1,183 | City notice plus four-page unsigned petition/proposal; ten-year version discrepancy and full operative history unresolved |
| Emporia Question 2, high-impact data centers | 4,346 / 2,891 | City wording and resolution with explicit prior-court condition; final judicial disposition, enactment and certification unresolved |
| Emporia Question 3, Tier 2/3 BESS | 4,067 / 3,117 | Separate city wording/resolution; reserved judicial remedies differ from Q2's explicit gate; final legal force unresolved |
| Ottawa city question | 2,882 / 1,129 | County unofficial return says City of Ottawa Question; exact official wording, Question 2 designation linkage and qualification remain open |
| Americus mixed data-center/BESS proposition | 274 / 127 | Signed official notice addresses city electors and cites Resolution 313; full ordinance/thresholds, qualification and force unresolved |

The Lyon County report explicitly says **Unofficial Final**. Its source labels are retained separately:

| Contest | Total Votes Cast | Contest Totals |
|---|---:|---:|
| Emporia Q2 | 7,237 | 7,338 |
| Emporia Q3 | 7,184 | 7,338 |
| Americus | 401 | 411 |

These are not silently reclassified as ballots cast, valid votes or blank/under/overvotes. Franklin County's return explicitly says Unofficial Results. Butler's election-night feed supplies source counts but no accepted final certification. A separate earlier news observation of 2,966 El Dorado yes votes remains distinct from the official feed's 2,972; it is not a certified revision, nor grounds to sum observations or fabricate a supersession chain.

## Material source distinctions

El Dorado's August 31 city notice says the ordinance would remain in effect for ten years and restrict amendment/repeal during that period. The newly recovered four-page document is a petition and unsigned proposed ordinance: blank ordinance number and execution lines, ten operative sections, and a publication/elector-approval clause. All four pages were directly reviewed and separately OCRed; those ten sections contain no ten-year expiration clause. The document menu's Published 10-14-2026 label is not proof that a signed law took effect on that date. Preserve both versions and leave expiration/current force unresolved rather than choosing either ten-year expiry or indefinite effect.

The same El Dorado proposal also shows why a single >80 kWh battery threshold is incomplete. Tier 2 includes 81–600 kWh **or** more than one storage-system technology in a room/enclosed area, while other tiers and aggregation provisions have additional conditions. Proposed accessory-computing, standalone car-battery and electric-vehicle exclusions require their own clauses. This review accepts the directly read definition passages, not an exhaustive current exemption determination.

Emporia Resolution 3799, physical PDF page 3, expressly says that even a yes majority does not permit publication/enactment until a district-court validity determination or further order. Resolution 3800, physical page 3, instead deems majority approval an elector approval and reserves the city's ability to seek declaratory relief, stays, injunctions and other remedies before or after election. Its generic article heading does not make its operative clause identical to Question 2. Neither the resolution's immediate effective date nor a post-election news approval report proves the proposed substantive prohibition is in force.

The Americus signed notice establishes a mixed-sector city question and November 3 election. It cites an adopted Resolution 313, but the notice does not supply the complete ordinance's thresholds or expiration. Emporia's thresholds are not imported into Americus merely because both use High Impact Data Center and Tier 2/3 labels.

## Coverage and next dispositions

The five measures have bounded primary review, not complete legal histories or canonical publication. Current court orders, adopted ordinances and actual publication, complete qualification/exhibits, certified canvasses, duration and source-denominator interpretation remain required work. Existing city/county moratorium records are contextual predecessor candidates only; no duplicate instrument, successor link or legal-force interval is created.

Four Exa searches used $0.028 in reported charges. Five fetches were used within an eight-fetch cap. Ottawa official-domain and broader searches did not recover exact primary ballot wording; that is a collection gap, not evidence of absence. Emporia court searches returned older reporting leads, not a verified current court disposition. Searches did not establish absence of later litigation. No additional distributed queue or API model extraction was launched.

This packet does not change canonical ballot or legacy inventory counts. The frozen census remains 18 scoped publications / 38 pending groups, with five of the pending groups now linked to this multi-record review. All acquisition bodies, OCR and rendered images remain in the private archive; public manifests retain source lineage. Existing source versions and worker candidates are preserved.

Archive validation initially caught three text-empty scanned PDFs skipped by the importer. Separate retained OCR derivatives are now registered for those bodies and all nine source payload versions are present in the archive manifest. Original acquisition hashes, including empty-text versions, remain retained and indexed; all fourteen claims reverify. OCR coverage does not establish substantive review of every page or completeness of referenced exhibits. `validation.json` records the repaired archive check.
