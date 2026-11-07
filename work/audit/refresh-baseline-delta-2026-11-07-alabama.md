# Working headline comparison — November 7, after Alabama adjudication

The baseline is source commit `dbaab04d84f8d679ba5a3d57bf45f32186109222`,
whose README describes September 23. Current CSV bytes and source revision are
pinned in the [row-level change ledger](refresh-baseline-delta-2026-11-07-alabama.json).
This is not a comparison with the last published GitHub release. The earlier November 6 and November 7
reports remain historical checkpoints and are not overwritten. This comparison
pins committed Alabama source corrections at `664edc9dc5ef30244242d4f29b869ee2880d6784`.

| Metric | September baseline | Current | Difference |
|---|---:|---:|---:|
| Local records | 1,291 | 1,330 | +39 |
| Active | 897 | 887 | −10 |
| Extended | 166 | 192 | +26 |
| Active plus extended | 1,063 | 1,079 | +16 |
| Pending | 77 | 79 | +2 |
| Replaced | 93 | 94 | +1 |
| Expired | 50 | 66 | +16 |
| Rescinded | 8 | 12 | +4 |
| State-policy records | 440 | 442 | +2 |
| State-policy records categorized enacted | 85 | 95 | +10 |
| Policy records typed as bills | 438 | 427 | −11 |

Forty local additions and one reviewed Seattle duplicate retirement produce the
net increase of 39. The registry preserves the retired permanent ID and original
row; the historical denominator is not backcast. Two state-policy additions are
California AB2469 and New Jersey A4696. The ledger identifies every addition,
removal and changed field: 669 surviving baseline local records and 115 surviving
baseline policy records have at least one changed value. These are edit counts,
not completed freshness reviews or new enactment counts.

The typed-bill decrease reflects thirteen reclassifications (ten legislative
resolutions and three precursor memos) and two added bill records. Current state
policy categories are 427 bills, ten resolutions, three precursors, one executive
order and one governor directive. Compound observations remain, so typed rows are
not a verified unique-bill denominator. The 95 enacted-category records include
94 bill-category records and one executive order; they are not 95 current
moratoria or an inventory-wide current-force finding.

## Separate ballot and proposal scope

The current expanded subset contains **51 records: 49 voted, one scheduled and
one litigated**. It retains **57 result observations**, of which **50 are current**
and **five current observations are certified**. Current observations need not be
certified, and observation counts are not a count of distinct measures that passed.

The frozen 56-group cohort retains 49 scoped publications and seven unresolved
groups. Jay's solar ballot and Wilmington's litigated initiative history are two
records outside those frozen publications. Wilmington adds no vote result; Jay's
1,464/723 count remains a secondary unofficial observation. The older frozen
projection's 50-record summary is preserved under `historical_projection`, while
current lifecycle/table counts are calculated separately. No national ballot-census
completeness or 0-to-51 nationwide change is claimed.

The cohort cutoff remains November 5, with later source retrieval/review dates
separately recorded. Legal force, source acceptance, all-record freshness,
consumer reconciliation and final release publication are not established by
this arithmetic or the matching CSV hashes.

Generate a new report without replacing any historical file:

```sh
python3 scripts/build_refresh_headline_delta.py --output /path/to/new-comparison.json
```

[Independent arithmetic review](../research/2026-11-07/headline-comparison-review/independent-review.md)
confirmed the counts and field changes. The [root adjudication](../research/2026-11-07/headline-comparison-review/root-adjudication.json)
records the subsequent header/schema and missing-registry fixes and six targeted
regressions. These checks validate comparison behavior, not all underlying facts.

The [Alabama source batch](../research/2026-11-07/alabama-source-adjudication/README.md)
changes no headline counts. Its 23 substantive cells plus one derived marker count
are included in this row-level ledger; earlier comparison receipts do not cover
these later fields. The prior independent arithmetic review covers the earlier
checkpoint; current counts and rows were recomputed from the pinned revision.
