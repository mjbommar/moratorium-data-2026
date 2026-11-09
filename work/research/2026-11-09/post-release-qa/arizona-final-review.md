# Arizona official final-disposition review

The official disposition index and seven rendered bill histories resolve previously missing bill-specific procedural evidence. Sixteen guarded cells change across seven existing records. All primary introduced-version provision texts remain retained.

| Bill | Official final disposition | Recorded dated action now supported |
|---|---|---|
| HB 2467 | Held in Committees | Commerce withdrawal / AI and Innovation assignment, January 22 |
| HB 2631 | Held in Committees | Commerce withdrawal / AI and Innovation assignment, January 22 |
| HB 2820 | Held in Committees | House second reading, January 26 |
| HB 2949 | Held in Committees | House second reading, February 5 |
| SB 1463 | Held in Committees | Senate second reading, February 2 |
| SB 1467 | Held in Committees | Senate second reading, February 2 |
| HB 4009 | Failed in House on Third Reading | February 26: 29 ayes, 25 nays, six not voting; marked FAILED |

The official HB 4009 page explicitly marks the vote FAILED and the index independently lists the failed final disposition. Its category changes from unknown to failed_died and legal effect from unknown to failed. This resolves the exact final-action gap recorded by its prior independent whole-field review, with other previously reviewed fields retained. One corrected-resolved closure is applied. This is a recorded historical bill outcome, not an assessment of every possible successor measure.

The six held-in-committee records retain unknown terminal categories: the official held labels establish their recorded procedural disposition, but no unreviewed adjournment rule is inferred. Their status narratives and last-action dates now use direct official histories instead of qualified tracker leads. HB 2452 is also directly listed in the held-awaiting-third-reading-on-reconsideration index; its existing status/date remain unchanged and its terminal-consequence question remains open.

Retrieval follows observed portal routes and scripts, not guessed bill identities. Session 130 and exact BillIds are returned by the official disposition lists. The portal’s script supplies `/api/Disposition/` and `/api/BillStatus/`; its calls include an empty body parameter. Omitting that parameter returned a 404; the successful observed form returns XML bodies, which were parsed directly. A 200 search form or script alone is not bill evidence. The official lists contain eight reconsideration-held entries, 994 committee-held entries and eighteen House-third-reading-failed entries; named rows are matched by session, BillId and bill number. These list sizes are portal observations, not dataset census totals.

[Source clocks and hashes](arizona-final-sources.json), [exact applied cells](arizona-final-field-application.json), and [current guards and residual questions](arizona-final-adjudications.json) preserve the evidence chain. No local record, ballot record, scope partition or immutable release asset changes.

[Validation](arizona-final-validation.json) confirms nine focused checks, 0 dataset errors and 621 retained warnings. The status restoration reduces net existing-record status differences from September to 156 (94 local, 62 policy), because HB 4009 again matches its September failure classification.
