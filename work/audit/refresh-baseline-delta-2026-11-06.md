# Working refresh: baseline comparison

Baseline: `dbaab04d84f8d679ba5a3d57bf45f32186109222`, whose README describes September 23, 2026. Current source revision: `4638318` (with current working-tree CSV hashes pinned in the JSON report). This compares working repository data, not the last public release. The refresh cohort cutoff remains November 5; individual later reviews do not renew all-record freshness.

| Metric | Baseline | Current | Delta |
|---|---:|---:|---:|
| Local instruments | 1291 | 1293 | +2 |
| Active | 897 | 879 | -18 |
| Extended | 166 | 192 | +26 |
| Active plus extended | 1063 | 1071 | +8 |
| Pending | 77 | 67 | -10 |
| Replaced | 93 | 94 | +1 |
| Rescinded | 8 | 11 | +3 |
| Expired | 50 | 50 | 0 |
| State-policy records | 440 | 442 | +2 |
| State-policy records classified enacted | 85 | 95 | +10 |

The current enacted policy total comprises 94 records typed as bills and one executive order. The policy tracker covers multiple mechanisms; it is not a count of enacted state moratoria. The legacy bill type also includes a resolution, so it should not be represented as a fully audited bill denominator.

Two local instruments were added: `ca-hayward-2026` and `ia-dubuque-county-2026-2`. Two policy records were added: `ca-ab2469-2025-2026` and `nj-a4696-2026-2027`. No baseline IDs were removed. Of surviving baseline records, 443 local and 30 policy records have at least one changed CSV field. These are edit counts, not completed substantive reviews or newly enacted instruments.

The separate ballot snapshot contains 49 reviewed measures. Of 56 frozen logical candidate groups (58 observations), 49 have scoped canonical publication and 7 remain pending. This is a reviewed subset, not a complete election census. Ballot records, unofficial returns, certification, and operative legal restrictions remain distinct.

The historical November 5 accounting report remains a historical collection/edit snapshot. Its 440-policy denominator must not be reused as the current total.

Reproduce the machine-readable comparison from the repository root:

```bash
python3 scripts/build_refresh_headline_delta.py
```

The [JSON report](refresh-baseline-delta-2026-11-06.json) pins both CSV byte hashes, identifies every added/removed ID and changed field, and pins the ballot projection and snapshot. Regeneration against later data produces a new observation and requires updating this prose. No result here establishes complete current legal-force verification, consumer synchronization, or release publication.
