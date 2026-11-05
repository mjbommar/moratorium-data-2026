# Ohio ballot pilot: candidate research

Reference date: November 5, 2026. These are six provisional candidates, not accepted facts. The election was November 3. The source bodies and extracted text are private pending rights classification. This is a bounded pilot, not an election census.

The only election return recovered directly from a board of elections is the [Clinton County unofficial canvass](https://www.boe.ohio.gov/clinton/c/elecres/20261103results.pdf), labeled final on election night but explicitly **unofficial**. It is not certification. The precise official ballot language for all six questions, the Miami and Franklin official returns, certified canvasses, and adopted legal text remain outstanding. The downloaded Clinton return is `clinton-results.private.body`, SHA-256 `5cfff145c261a87c96cbbd187c5b9132ef05132f617c3b5d087959c250c28c80`; the extracted text and other evidence are identified in `candidates.jsonl`.

## Piqua, Miami County

A [local report](https://miamivalleytoday.com/piqua-commissioners-ousted-in-recall-effort-data-center-ban-approved/) reports the separate general-election charter amendment restricting data center construction passed 4,061 to 2,027, unofficially. [WYSO](https://www.wyso.org/government-politics-news/2026-11-04/piqua-voters-reject-data-centers-recall-city-commissioners) describes the question as prohibiting data center construction. The scope, definition, exemptions, effective date, precise wording, qualification mechanism and certification need official evidence. A reported recall election is a distinct event. No predecessor pause or successor link is established by the sources read.

## Grove City, Franklin County

[WOSU](https://www.wosu.org/politics-government/2026-11-04/grove-city-approves-issue-28-to-force-votes-on-developments-including-data-centers) reports Issue 28 passed with 54.61% approval, using unofficial county results, and describes a city charter amendment requiring a citywide vote for developments above a certain size. A [campaign page](https://protectgrovecity.org/updates/) describes it as a citizen initiative. This applies more broadly than data centers on the available description; exact thresholds, exemptions, triggering approvals, ballot wording, counts, certification and legal effect need official records. The existing inventory has `oh-grove-city-2026` for Ordinance C-22-26, a 12-month moratorium adopted June 1; this is a possible related prior instrument, not a verified replacement or termination link.

## Wilmington, Clinton County

The county's unofficial canvass lists four distinct referendum contests; parcel descriptions and voting direction below are from the [Wilmington News Journal](https://www.wnewsj.com/2026/11/03/wilmington-voters-reject-four-rezoning-ordinances/). The report says yes approved each change from rural residential to light industrial. The ballots and ordinances must be checked to independently confirm wording, parcel scope and polarity.

| Ordinance | Reported land | Yes | No | Question votes |
| --- | --- | ---: | ---: | ---: |
| O-26-04 | 119.373 acres, State Route 730 | 739 | 2,885 | 3,624 |
| O-26-05 | 65.29 acres, 1957 State Route 730 | 732 | 2,886 | 3,618 |
| O-26-06 | 191.12 acres, McGuinn Road | 724 | 2,887 | 3,611 |
| O-26-07 | 170.11 acres, U.S. 68 South | 716 | 2,909 | 3,625 |

The paper reports each rezoning defeated and describes nearby or adjacent proposed data center development. These four votes do not establish a citywide prohibition, a project's cancellation, or legal effect before the applicable process is verified.

## Coverage and execution limitations

Both Exa and SerpAPI were used through `bc_web.Searcher`; `bc_web.Retriever` was used for 12 retrievals. Primary ballot texts were not recovered. Ballotpedia returned HTTP 202 for both requested pages. County landing pages did not establish the missing texts or returns. The search limit was inadvertently exceeded: six queries ran twice after a failed script edit, for 12 total searches including six SerpAPI searches, versus the authorized limits of eight and four. The repeat overwrote the initial provider response artifacts; only the second six responses remain. Exa reported $0.042 across six calls; SerpAPI pricing for six calls is unknown, so total spend is unknown. See `run.json` for retrievals, hashes, failures, and the incident.
