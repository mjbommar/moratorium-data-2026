# Full object worklists and sparse search previews

`scripts/build_sparse_refresh_worklist.py` accounts for every current local, state-policy and ballot ID before planning searches. It uses native bc-spec points, validation, selection and estimates through the existing search-batch adapter. Generation performs no network calls and does not revise research dispositions, source dates or canonical records.

The [November 6 development packet](../work/research/2026-11-06/sparse-refresh-worklist/README.md) contains 2,322 work items: 1,330 local records, 442 state policies, 50 measures, 250 state/sector discovery items and 250 independent state/sector election-discovery items. All five existing sectors are represented. The resulting frame has 2,713 explicit search cells; multi-sector records can have multiple cells. State sweeps are not a census of municipalities.

## Registry and identity boundaries

The registry contains 1,377 search coordinates. Existing expanded jurisdiction UUIDs remain unchanged. Legacy locality coordinates hash the exact state, government-type and locality tuple; they are search keys, not allocated canonical identities or assertions that differently named governments are equivalent. Even a matching legacy/expanded place remains separate until a reviewed crosswalk. State/county context and existing aliases are retained where available; unknown county context stays unknown.

Canonical election-result URLs are retained as portal candidates requiring authority review. They never silently become official-host filters. The one reviewed host binding in this development packet is Seattle's clerk legislative-document host. Its explicit review record identifies jurisdiction, role, original body hash and the authority basis. The generator verifies the exact retained manifest version and actual source body, then pins the review file and preserves it in the plan. This human source assessment does not prove complete host coverage or automatically validate every later document on that host. Election and records roles remain distinct.

The broader reviewed government/election-host registry remains unfinished. Missing bindings are visible, and unrestricted discovery remains separate from official-host recovery.

## Sector uncertainty and coverage

Every state-policy ID receives a sector-neutral designation/state query: the legacy table has no reviewed sector column. Those 442 tasks retain a separate sector-review requirement. The 34 mixed/unknown-sector tasks preserve their unresolved terms and also receive neutral recovery cells. `sector_unresolved` is a reserved planning coordinate, not an added canonical sector. `cryptocurrency_mining` is preserved as a source term alongside its translation to the search adapter's broader `cryptocurrency` vocabulary; this is not an equivalence assertion.

The full explicit frame is selected by default. Optional `--per-lane 1` generates a tiny seeded preview with three selected cells, 2,710 exclusions, exact selected-provider caps and selection accounting by state/lane/sector. It is not full-refresh coverage. All exclusions remain visible; generating a task or selecting a cell does not mean that the object was researched. Existing historical review ledgers are not reset by the new worklist's `not_attempted_by_this_worklist` statuses.

Queries preserve state context, aliases and known bill/measure designations. Publication windows are omitted to permit undated-source recovery. Templates are development defaults: exact identifiers, ballot titles/dates, instrument-reference chasing, polarity-specific families, query repair and calibration still need further work before accepting absence findings or broad collection quality.

## Reproduce without spending

```sh
BCPY=/home/mjbommar/projects/bc/bc-modules/.venv/bin/python
"$BCPY" scripts/build_sparse_refresh_worklist.py --cutoff 2026-11-06 \
  --bindings work/research/2026-11-06/sparse-refresh-worklist/host-bindings.json \
  --output /tmp/moratorium-full-scope-review
```

Use a new output path; the generator refuses to overwrite an existing directory. Omitting `--output` prints the summary without writing files. Add `--per-lane 1` only for the explicitly limited sample. The expanded generation is pinned for the read, and loaded input hashes and the pointer are rechecked before returning. Input hashes, the seed, exclusions and canonical generation are retained.

Generated plans have `allow_unpriced: false`. Call caps equal the selected variants, but these are estimates of planned calls, not account pricing, campaign authorization, a provider invoice or completed searches. Whole-run/per-stage dollar budgets, account-specific prices and calibration remain open. The November 6 planning cutoff does not relabel the November 5 canonical election cohort or certify freshness through either date.

## Search-plan version 2

New executions require `refresh-search-plan-2`. Domain filters require a scoped authority review; execution verifies the actual review file's hash and contents before creating a reservation marker or dispatching transport. Historical version-1 plans remain readable for preview and retained replay using their pinned runtime; they cannot initiate new runs. Runtime changes still require retained-result review and do not trigger an automatic restart.

The generator rejects unknown binding coordinates, unavailable/changed source bodies, conflicting review scopes and reserved review fields that could overwrite verified paths or hashes. Behavioral tests cover disjoint place identities, complete ID accounting, translations/unknown terms, deterministic full/sample selection, host candidates versus filters, pinned authority records and failure before transport. These controls do not establish factual acceptance or complete the remaining P2/P4/P5 gates.
