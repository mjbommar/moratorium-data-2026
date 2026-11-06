# Wisconsin ballot primary review

Seventeen scoped claims across seven exact source versions are reviewed, evidence-verified and archived. This packet does not publish canonical records: totals remain41 reviewed measures /15 pending frozen groups. Sources include official returns, an unsigned city proposal and reproduced petition/resolution documents; their authority and version limits remain distinct.

| Case | Reviewed scope | Unresolved |
|---|---|---|
| City of Janesville |Clerk memo reports3927qualifying petition signatures, January21certification. Unsigned File Ordinance2026-926 proposes prior electoral approval for covered GM/JATCO development/site transactions exceeding450millionUSD. Rock County unofficial return:16779yes/9932no,62.82%,40/40precincts. |Final ballot, completed referral/adopted text, actual effect and post-vote legal history. City is distinct from existing Town of Janesville moratorium. |
| Village of Wrightstown |Signed resolution reproduction schedules advisory vote August11,2026. Brown post-county-canvass slice106yes/899no; Outagamie unofficial slice45yes/134no. |Exact final ballot, original-host resolution/publication proof, complete village canvass, certification dates and operative histories. Secondary transcription omits “large-scale” found in reproduced resolution. |
| City of Port Washington |Watermarked unsigned TID petition/draft; official unofficial April7return2710yes/1371no,66.41%, TotalVotes4081, sourceTimesCast4201,8257registered. |Final ballot and adopted text, qualification and certification, interpretation of conflicting exception boundaries, subsequent litigation/force. City is distinct from town. |

## Proposal and authority distinctions

Janesville's five-page city packet contains a memorandum and unsigned proposal. It is a first-reading/scheduling packet, not proof council adopted or referred it. Section1 says costs **exceeding450million**;3(f) exempts **under450million**. Exact equality is not silently repaired. Project costs include construction/administration, adjacent cohesive campuses can be included, and phases are considered together. Routine/minimal changes after approval and new proposals after rejected plans have different referendum rules. The future project majority rule is not accepted as the passage rule of this ballot measure. The instrument covers general site development, not a categorical data-center ban. Blank adoption/signature/vote fields are preserved as a limit.

Port Washington's reproduced draft requires approval for a TID with base value projected to or exceeding10millionUSD, or project costs exceeding10millionUSD. Its3(b) exception instead uses disjunctive conditions including base value **not exceeding10million**. The equality/exception interaction remains unresolved. The adoption/date/signature fields are blank. The draft is not accepted as final enacted text or a data-center-only restriction.

The Ozaukee return's4201 **Times Cast** is retained under its own label. Its difference from4081yes/no votes is120unclassified; it is not declared blank/under/overvotes. Seven ward-report rows are not an accepted precinct count. CountyTotal on this particular contest page is the city-contest aggregate, not a global county denominator. No full105-page substantive review is claimed.

Wrightstown's two-page signed resolution is a reproduction hosted by Ballotpedia; the original municipal-host version remains missing. It schedules **August11**, correcting the frozen August8lead. It says the question should read substantially as printed, so its wording is not automatically the exact final ballot. The advisory result itself authorizes no specific contract, expenditure, zoning approval, development agreement or utility extension. The resolution's passage/publication condition does not establish an operative date without publication proof. A separate board-adopted moratorium must not be merged with the advisory vote.

## Wrightstown county reconciliation

| Source slice | Yes | No | Total Votes Cast | Undervotes | Overvotes | Contest Totals |
|---|---:|---:|---:|---:|---:|---:|
| Brown post-county-canvass official summary |106|899|1005|43|0|1048|
| Outagamie August11unofficial summary |45|134|179|15|0|194|
| **Derived sum of these versions** |**151**|**1033**|**1184**|**58**|**0**|**1242**|

The sum matches the secondary village-wide yes/no report. It is a computation from separately scoped sources with different status and timestamps, not a certified complete village canvass. Neither the Brown August17generation clock nor its OFFICIAL RESULTS label supplies an independently reviewed certification date. The Outagamie source is explicitly unofficial. County source percentages use **Contest Totals**, including undervotes: Brown10.11%yes and Outagamie23.20%yes must not be averaged or represented as percentages of yes/no votes. ContestTotals is not silently renamed village ballots. `wrightstown-county-reconciliation.json` pins the source claims and arithmetic.

## Retrieval and verification

The dedicated budget used all three Exa searches ($0.021 reported) and all ten fetch attempts; all are terminal. No SerpAPI or new model-extraction calls occurred, and completed distributed Terra jobs were not restarted.

Pydoll recovered Outagamie archive document links absent from the HTTP-only body. The downloaded summary has an ambiguous1126filename, but its actual header establishes August11,2026. Its physicalpage22 contains the relevant county slice. A separately fetched28-page official county-contest canvass is image-only and not yet substantively reviewed/OCR-registered; it supports no accepted claims here and is not asserted to be an archived nonempty reviewed source. Village resolutions navigation did not recover the original resolution, and loading navigation is not evidence of absence.

The two-page reproduced Wrightstown scan received separately registered150DPI OCR; original empty client text remains unchanged. All selected visual claim renderings were independently viewed and rechecked. Only seven claim-supporting source versions are asserted verified/archived; not every successful fetch has substantive acceptance.

```bash
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python work/research/2026-11-06/wisconsin-ballot-primary-review/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-wi-001 \
  --evidence-directory /data0/moratorium-refresh-2026/wisconsin-ballot-primary-review
```

`validation.json` confirms17verified claims and seven archived exact versions. Publication still requires normalization with the source-role and county-scope limits, identity/publication gates and regeneration. All final canvasses/qualification chains, full adopted texts, implementation, litigation, current-force histories, inventory freshness, consumer updates and release remain open.
