# Wisconsin ballot development context

Two verified claims from two retained and archived reporting versions supplement the primary Wisconsin packet. They supply thematic context only, without accepting legal force, project identity or an instrument/project coverage link.

The commercial real-estate association connects Janesville's referendum to a proposed data center and describes broader development scope. It participated in the campaign against the measure, so its account is explicitly source-qualified. Its submitted-signature figure must not replace the clerk's independently reviewed qualifying-signature count. The reported separate September city moratorium remains a discovery lead requiring its own primary review.

Wisconsin Public Radio connects Port Washington's April referendum to the data-center/TID debate. Its report describes future-district voter approval rather than reversal of an existing project TID. This is context, not an accepted current legal effect or litigation disposition. Its summary flattens both thresholds to10million-or-more; the reviewed draft distinguishes base-value equality from strict project-cost exceedance, with an unresolved exception clause. The draft version must not be silently rewritten from that report.

`validation.json` verifies both exact source versions and both context claims. No new API/model spending occurred. Canonical publication, exact final ballot, adopted text, current litigation and operative force remain open.

```bash
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python work/research/2026-11-06/wisconsin-ballot-context/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-wi-001
```
