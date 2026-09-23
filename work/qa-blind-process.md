# QA round 2: blind re-verification

You receive a list of jurisdictions (state, name, type, and a sector hint) and
nothing else: no dates, no status, no sources. For each one, independently
establish from the public record what moratorium instrument(s) on data
centers, battery storage, solar, wind or cryptocurrency mining that body has
adopted or formally proposed, and report:

- `instrument`: what it is (ordinance/resolution/motion number if any)
- `adopted_on`: the adoption vote date (YYYY-MM-DD, or YYYY-MM if only the
  month is known; empty if only proposed)
- `status_on_2026_09_23`: one of active, extended, expired, replaced,
  rescinded, pending, none_found
- `term`: the original term and, if extended, the current end date
- `sectors`: list from data_center, battery_storage, solar, wind,
  cryptocurrency_mining, general
- `is_temporary_pause`: true/false (false if what you found is a permanent
  ban or a zoning rule with no pause)
- `evidence`: URLs you actually read, each archived with
  `~/projects/bc/bc-modules/.venv/bin/python scripts/save_source.py --state <ST> --print URL`
  (run from the repo root; `--mode browser` for JS portals)
- `confidence`: 0 to 1
- `notes`

Tools: `cd ~/projects/bc/bc-modules && uv run bc-web search "<Jurisdiction> <State> data center moratorium" --fuse -n 10`
(always include the state; many names repeat across states). Read pages, do
not decide from snippets. Spend at most ~4 searches per jurisdiction; if you
find nothing, say `none_found` and list the queries.

Do NOT open data/moratorium_inventory.csv, states/, work/answers/ or
work/sources/ manifests: the point is an independent reading. (Archiving
with save_source.py is fine.)

Output: a JSON list at the path the coordinator gives you, one object per
input item, keeping the `blind_id`. Do the work yourself; do not spawn
subagents. Keep helper files in your own uniquely named scratchpad folder.
