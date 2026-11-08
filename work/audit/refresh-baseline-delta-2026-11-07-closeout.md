# Working-data changes against the historical source baseline

Baseline: `dbaab04d84f8d679ba5a3d57bf45f32186109222`. Observed current commit: `eac139c088835f486e4bd613cdcee809067292dc`. The JSON pins exact current CSV hashes. This is the historical source baseline, **not the last public release or the later frozen 1,772-record research queue**. It does not establish complete freshness or current legal force.

| Dataset | Baseline rows | Current rows | Added IDs | Retired IDs | Existing rows with changed values | Existing rows with unchanged values |
|---|---:|---:|---:|---:|---:|---:|
| Local moratoria | 1291 | 1330 | 40 | 1 | 698 | 592 |
| State policy | 440 | 447 | 7 | 0 | 264 | 176 |

The local net increase is 39: forty additions and one explicit duplicate retirement. `wa-seattle-2026-2` is retained through the identity registry as an alias to `wa-seattle-2026`; its history is not erased. All state-policy baseline IDs remain. The seven new policy IDs are:

- `ca-ab2469-2025-2026`
- `ia-hf2799-2026`
- `md-executive-order-01-01-2026-16-2026`
- `md-sb0427-2026`
- `md-sb0596-2026`
- `md-sb0841-2026`
- `nj-a4696-2026-2027`

| Classification | Baseline | Current |
|---|---:|---:|
| Local active/extended classifications | 1063 | 1079 |
| Local pending classifications | 77 | 79 |
| Local replaced/expired/rescinded classifications | 151 | 172 |
| Bill-type policy rows | 438 | 428 |

Six bill-type records were added and sixteen retained records were retyped to resolutions, an amendment, statutes or legislative precursors. That produces the bill-only decrease while raw policy rows increase from 440 to 447. These are record/form counts; they do not count unique legal outcomes or enacted moratoria. The current enacted bill-only count is 92. The general-water and research-data-platform scope questions retain their separate review decisions; this table applies no analytical scope filter.

The exact existing-row diff contains 3,164 changed local cells and 1,143 changed policy cells. It includes verification annotations, classifications, historical qualifiers and normalized values. **Changed is not a researched-confirmed count; unchanged values are not confirmation of current law.** Source-unavailable, unresolved, attempted and independently accepted denominators still require the full record-freshness accounting.

The current expanded snapshot retains 53 measure records: 49 voted, three scheduled and one litigated. It retains 58 result observations, with 50 current observations and five current certified observations. The staged Trenton classification correction is not applied or included here. The current mapping retains 51 published measure IDs from the frozen election groups plus two outside those publications; these are different grains from the 56 frozen groups and do not establish a complete national election census.

The [full JSON diff](refresh-baseline-delta-2026-11-07-closeout.json) preserves every added/retired ID and changed existing field, schema comparison, source hashes, status/type counts and frozen/current ballot mapping. Earlier reports remain unchanged.
