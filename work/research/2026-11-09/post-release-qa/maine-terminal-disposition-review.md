# Maine terminal-bill disposition audit

Three records should remain **unresolved** because their sponsor-party values are specific, unverified historical leads in the accepted full-field review. For LD 307, recommend **confirmed_unchanged**: the supported terminal veto and current proposed-only end condition leave no identified bill-specific gap. These recommendations concern the named rows at their retained source observations, not later or other measures. No field correction is proposed.

The prior full-field review compared all 19 fields and requires exact row guards. Its guard matches the assigned current row for each older bill. LD 307 differs only in `end_condition`: the earlier guard was blank, whereas the current value records a proposed repeal of section 1 on 2027-11-01 and the veto. The amendment directly supports the current value; the old blank-field decision is not reused. All four accepted packets say `unperformed_checks: []`, but that does not erase the earlier explicit party-field gaps.

All four rows retain the dataset-wide Maine `activity_level` of Medium provisionally, pending statewide reconciliation. This qualification is not an independent source finding for an individual bill. Preserve every original ID, source observation timestamp, and action date; a capture is not a legal event date. No later-law census is implied.

## Case findings

### LD 1259 / SP 380 — unresolved

Introduced tax refund or exemption for eligible data-center purchases and services, with employment and recapture conditions. Final action: 2011-05-17. Sponsor Roger Sherman: the retained review does not establish the historical Republican affiliation and district stated in the party field.

Current row SHA-256: `f3f82e91ff6840ad584d906e40e7b422c92570c84d6299fd71a3d6c8ad085c73`. Retained evidence:

- [official bill history](https://legislature.maine.gov/legis/bills/display_ps.asp?LD=1259&snum=125): SHA-256 `29169c704bb3b354bfb3fd0e36f55816ab45a97a1b49b38eafd19fec37f65181`; official bill history: final disposition; text: Documents and Disposition and committee action; captured 2026-11-05T16:31:09.235532Z.
- [introduced bill HTML](https://legislature.maine.gov/legis/bills/bills_125th/billtexts/SP038001.asp): SHA-256 `80abcde1895c6794a94bc6a622f63e144f15cec2983e4c46a17e552260247888`; introduced text summary: proposal and conditions; captured 2026-11-05T16:32:28.078312Z.

### LD 1722 / HP 1202 — unresolved

Introduced tax refund or exemption for eligible equipment and services, with full-time employment and recapture conditions. Final action: 2018-03-22. Sponsor Stephen Stanley: the retained review does not establish the historical Democratic affiliation and locality stated in the party field.

Current row SHA-256: `244fdd5916907d6a5d425601da3ea03e4c919327e0a694cd99cc004b9856baf4`. Retained evidence:

- [official bill history](https://legislature.maine.gov/legis/bills/display_ps.asp?LD=1722&snum=128): SHA-256 `d76c24b2a6c770e39bb536f5733a310176d9f7ab6cfef20ba1b766075ff10df5`; official bill history: final disposition; text: Documents and Disposition and committee action; captured 2026-11-05T16:31:12.792546Z.
- [introduced bill HTML](https://legislature.maine.gov/legis/bills/bills_128th/billtexts/HP120201.asp): SHA-256 `10f1a568296710039a3e88d6b25b974771a5cb560345341f19bc652f7132da22`; introduced text summary: proposal and conditions; captured 2026-11-08T00:13:52.860614Z.

### LD 192 / HP 169 — unresolved

A concept draft proposed a program encouraging a renewable-energy-powered data center; it did not supply operative program provisions or enact a moratorium. Final action: 2011-03-15. Sponsor Cynthia Dill: the retained review does not establish the historical Democratic affiliation and locality stated in the party field.

Current row SHA-256: `31c7808ff5ddb1a7b3e9ad1d371c96f1cf47f9d71a9d32233d9c3d3d959abae0`. Retained evidence:

- [official bill history](https://legislature.maine.gov/legis/bills/display_ps.asp?LD=192&snum=125): SHA-256 `4bec77e9752dff3ed66339d30c5fb82dd73f1cb771f0bbf72de1baceb46761f1`; official bill history: final disposition; text: Documents and Disposition and committee action; captured 2026-11-05T16:31:11.142686Z.
- [introduced concept HTML](https://legislature.maine.gov/legis/bills/bills_125th/billtexts/HP016901.asp): SHA-256 `06e40379fb1e7deda61a6522c5be7b220e030eba73c563ffdda60313404cebf3`; introduced text summary: proposal and conditions; captured 2026-11-05T16:32:29.401541Z.

### LD 307 / HP 207 — confirmed_unchanged

The adopted committee amendment proposed an application and approval restriction for data centers of at least 20 MW, repeal of that restriction on 2027-11-01, and a separate council report. The governor vetoed the bill and the House sustained the veto, 72–65. Final action: 2026-04-29. The earlier field review independently supports the other matched fields, including party; the changed endpoint has been checked against the amendment. The bill created no operative pause.

Current row SHA-256: `d76e3fab7800e7a798dcacae253963e09bea8b31ebb959f2485a6a647985f1ba`. Retained evidence:

- [official bill history and amendment markup](https://legislature.maine.gov/legis/bills/display_ps.asp?LD=307&snum=132): SHA-256 `b1ab11a8be5c1f789e5cc3b09b68b17029caea55e4b90cf8e487d314ecec19d5`; official bill history: final disposition; HTML lines 235-244 since text extractor omits disposition; captured 2026-11-05T16:31:14.123299Z.
- [committee amendment A H-881 PDF](https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP0207&item=2&snum=132): SHA-256 `e77b202fb527bd7c402614a913cfd4b81c69a26a700d53f2af19a0f0e47df880`; committee amendment A H-881 PDF page 1 printed lines 9-25; extraction has reversed line order; captured 2026-11-08T00:13:52.984662Z.
- [official chamber status](https://legislature.maine.gov/LawMakerWeb/summary.asp?paper=HP0207&SessionID=16): SHA-256 `4c1968fca97f62f106e1300e3eff982b645975f6ff257af58ad757da60e6edac`; chamber status: April 29 roll call 828, veto sustained and dead; captured 2026-11-05T16:32:15.369050Z.
- [original concept bill PDF](https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP0207&item=1&snum=132): SHA-256 `98de4c0ca0920c8f9dfcdf3636b506f3144165fbb093412fa898f3ce84b6713b`; PDF page and printed line or HTML physical line/section as cited in field ledger; captured 2026-11-08T00:14:36.288118Z.
- [House amendment B H-1051 PDF](https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP0207&item=14&snum=132): SHA-256 `4fbe3029308d15dd918cf341c8c9c7c1d418b5b86aaa83301d3666dcb03a5cfa`; PDF page and printed line or HTML physical line/section as cited in field ledger; captured 2026-11-05T16:32:19.464552Z.
- [official House roll call PDF](https://legislature.maine.gov/house/Repository/Documents/132/RollCalls/026.790.132R2.pdf): SHA-256 `85e248d0c23d82367d0e8f238f410c75b10643e0a5cb1b2b9d16bd042accfce5`; PDF page and printed line or HTML physical line/section as cited in field ledger; captured 2026-11-08T00:15:00.090608Z.
- [official House veto roll call and member party](https://www.mainelegislature.org/LawMakerWeb/rollcall.asp?ID=280096138&chamber=House&serialnumber=828): SHA-256 `542b07bc4860f69061682059499894f556fa007c7c672ba742484829a770f10a`; PDF page and printed line or HTML physical line/section as cited in field ledger; captured 2026-11-08T00:16:49.057109Z.

For LD 307, the history HTML identifies both adopted amendments and the veto; its extracted text omits final disposition, so the raw HTML is decisive (physical lines 235–244). Committee amendment H-881 page 1 printed lines 17–25 supplies the proposed restriction and section-specific repeal; page 3 lines 21–24 supplies the report date. House amendment H-1051 replaces the funding section (page 1 printed lines 10–19), leaving that restriction intact. The separately retained House roll call and chamber summary support the vote.

The full-field review SHA-256 is `49ea2e1a31b8aab94df44b3e967f4b063eba7f17498da6ff23ae089ec4db66c7`; its field ledger is `1c8ab921c74ad0ed1f14fb2cf33a090f663fddbd4c6e57e322db7d2c1685d7ca`. Source-body and extracted-text hashes used above were recomputed locally. No network or canonical data changes were made.
