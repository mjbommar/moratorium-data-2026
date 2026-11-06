# Adams County zoning-plan follow-up — November 6, 2026

This targeted follow-up pursues the complete Monroe and Sprigg township zoning plans and resolves an erroneous Sprigg numerical conflict in one original worker narrative. Both townships remain pending canonical ballot publication; a generic zoning-plan return does not establish data-center provisions or a restrictive policy direction.

## Corrected Sprigg source reading

The official Adams County report, physical PDF page 12 / printed page 10, shows:

| Source quantity | Value |
|---|---:|
| For the Zoning Resolution | 330 |
| Against the Zoning Resolution | 297 |
| Total Votes | 627 |
| Times Cast | 646 / 1,156; 55.88% |
| Unresolved Write-In | 0 |
| Precincts reported | 1 of 1 |

The original `ballot-oh-002/report.md` narrative incorrectly stated 397 against. Directly reading the page resolves that error: it says 297 and total627. The separate `ballot-oh-004` return already reported the correct 330/297. The frozen original returns are preserved; `correction.json` pins their hashes and the corrected primary-source correspondence. No previously published canonical Sprigg count was changed.

The source's Times Cast figures are retained without assigning the nineteen-count difference to blanks, undervotes or another category. Its 55.88% is not the yes share. The signed cover, physical page1, expressly says **Unofficial Certification of Results**. It authenticates the submitted unofficial return, not a final certified canvass or an operative zoning plan.

Four scoped visual claims and their 140-DPI rendering receipts are in `review.json` and `verification.json`. Every claim has reproducible evidence support against the retained body; the exact source body/text version is already archived in the OH manifest. Current formal outcome, complete zoning provisions, actual qualification/effect and moratorium relationships remain unresolved.

## Plan recovery and source roles

Four Exa queries ($0.028 reported fees) and three fetches were completed within the separate eight-fetch cap. Five fetch reservations remain available; there are no live attempts at this checkpoint. The new browser acquisition used bc-web/pydoll with an 1,800 ms settle and returned the Monroe Ballotpedia page. It supplies secondary general-zoning context, not the complete primary plan or its infrastructure provisions.

Two NoticeRegistry pages claim to reproduce October21 election notices, but their titles call them public hearings. Their own site states that it is not the government/newspaper publisher and that its summaries are AI-generated. The purported notice text concerns the November3 election, not proof of a separate October21 hearing. Claimed June22/July6 prior-action dates and the purported BOE attributions remain unverified leads until matched to an original publication or government record.

The original extraction of these two HTML bodies captured only the legal disclaimer/footer. Separately registered full-visible-HTML derivations recover the article, its AI labels and its purported notice reproduction without changing original client artifacts. Better extraction does not authenticate the content or promote it to primary evidence. The two pages have identical original footer-only text hashes despite distinct bodies; they are not independent corroboration of a zoning-plan provision.

The copied notices still describe general zoning, rural/agricultural character and higher-impact-development review; they do not supply the complete plans. No primary data-center prohibition, resource threshold, term, actual effective date or post-election legal force is accepted from these commercial reproductions or the secondary page. No account, purchase or message to a third party was used.

The next evidence gates remain authentic original BOE/newspaper notices, complete adopted/proposed plan text with infrastructure provisions, the actual qualification/referral chain, final canvasses and implementation. Failure to recover them in this bounded pass is a collection gap, not evidence that they do not exist.

Recheck the accepted primary claims without reacquisition or publication:

```sh
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python \
  work/research/2026-11-06/adams-zoning-followup/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-002 \
  --evidence-directory /data0/moratorium-refresh-2026/adams-zoning-plan-recovery
```

The three unaccepted lead versions are archived privately with metadata; no copyrighted secondary full text is published. This follow-up itself adds no canonical measure, result, restriction or legacy inventory row.
