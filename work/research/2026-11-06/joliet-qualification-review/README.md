# Joliet Township primary advisory and referral review

On November 6, a bounded Exa search located a township-hosted county-clerk legal notice. The township's election page links that exact PDF; its resolutions index separately links signed Resolution 2026-08. Both reference chains were checked against retained HTML. Four primary sources, seven claims and six visual receipts are pinned in `review.json`; `verification.json` records exact source/text hashes and independently reproduced visual proofs.

| Source event | Primary evidence | Accepted scope |
|---|---|---|
| April 14, 2026 | Resolution page 2 recites electors' annual township meeting voice vote | Source-reported approval to place an advisory question on the November ballot; underlying minutes not independently recovered |
| May 19, 2026 | Resolution page 4 has five yes marks, Supervisor signature and clerk attestation/seal | Board adoption/approval of ballot-submission authorization |
| May 19, 2026 | Resolution page 5 has signed/sealed clerk true-copy certificate | Certification of the resolution copy, not election results |
| September 29, 2026 | Signed Will County Clerk notice, page 1 | November 3 general-election advisory questions for Joliet Township electors |
| November 3, 2026 | Prior retained official county question list and result CSV | Previously reviewed source counts; result certification still unknown |

The notice and resolution contain:

> Should the Joliet City Council approve construction of AI data centers?

The electorate is **Joliet Township**, while the addressed actor is the **Joliet City Council**. These are not merged as one government. The notice explicitly calls the questions advisory; the resolution's title and recital agree. A yes vote favors approval, so `yes_direction=facilitates`. The resolution authorizes ballot submission, not construction and not a moratorium.

The referral chain has two stages: electors' annual-meeting approval, as recited by the adopted resolution, followed by Supervisor/Board authorization and a clerk filing instruction. The canonical placement vocabulary does not precisely name that hybrid route; the proposed reviewed classification is `other` with the original source terms retained. The resolution cites 60 ILCS 1/30-205. That citation is accepted as a source term, not an independent current-statute or complete qualification opinion. An instruction to file a certified resolution does not prove actual delivery by itself; the later legal notice independently confirms the scheduled question.

The five-page signed resolution is scanned and the original client text was empty. Each page was rendered at 150 DPI, fully inspected and OCRed with Tesseract. The combined extraction is separately registered; original payload/text hashes remain intact. The notice's signed officer/date, resolution roll call and clerk certificate were reviewed directly from images rather than inferred from OCR. The election-page native extraction omitted the current notice section; a separately registered complete HTML derivation restores it while preserving the original extraction.

The existing CSV count review remains unchanged: 3,800 yes, 14,207 no, 32 overvotes, 557 undervotes, and 18,601 source ballots cast. `18601 - (3800 + 14207 + 32 + 557) = 5` remains an unresolved source arithmetic difference. It is not classified as blank/other votes or evidence of missing physical ballots. Precinct completion is not certification. The 2025 township-election certification appearing elsewhere on the election page does not certify this November 2026 result.

Acquisition used one Exa search ($0.007 reported cost) and four HTTP fetches, within caps of two searches/six fetches. No model extraction, new distributed queue or negative statewide coverage finding is involved. Raw full source copies and OCR/render artifacts remain private; public source manifests preserve lineage. Official municipal documents on this `.net` host are retained as primary evidence without automatically publishing their full archived text.

This review resolves primary advisory wording and bounded referral evidence, but leaves the full petition/transmittal history, underlying annual-meeting minutes, independent current-statute review, result reconciliation, final certification/outcome and later legal implementation open. It does not itself promote a canonical ballot record or change headline totals. The frozen review ledger links this packet for the next publication decision; the canonical subset remains 17 measures with 39 frozen groups pending publication/review.
