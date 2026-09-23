# QA round 3: research the gaps the external trackers name

Each packet item is a jurisdiction that at least one public tracker lists as
having adopted or formally proposed a temporary moratorium (data center,
battery storage, solar, wind or crypto) and that our inventory does not have.
`assessment` is a one-search verdict by the cross-check agent; treat it as a
lead, not a finding.

For each item, follow Process B of `work/research-process.md` for that one
jurisdiction: 2-4 searches (always include the state name), read the pages,
find the primary instrument where it exists, archive every cited URL with
`~/projects/bc/bc-modules/.venv/bin/python scripts/save_source.py --state <ST> --print URL`
(from the repo root; `--mode browser` for JS portals), and check
`python3 scripts/show_rows.py --state <ST> --list` to be sure the jurisdiction
is really absent (trackers split counties into townships and misfile states).

Then either:
- write a `new_candidates` entry (schema `work/schemas/research_decision.schema.json`,
  codebook rules: `date_enacted_iso` is the adoption vote date; `pending` for
  proposed-not-adopted; `expired`/`replaced` for older instruments that have
  ended, with the original date; `sectors` list; instrument number in
  `legal_basis` where known; confidence per the process doc), or
- record why it is not a row: a permanent ban or zoning rule, a failed vote,
  a misattribution, a duplicate of an existing row, or unverifiable. Put these
  in a top-level `"not_added"` list is NOT allowed by the schema, so instead
  list them in your final report and in a sidecar file
  `work/answers/qa3-gaps/<name>-notes.md`.

Output: `work/answers/qa3-gaps/<name>.json` with `state_abbrev` set to the
packet's first state (the coordinator splits by candidate state), `decisions: []`,
and your candidates. Validate with the schema check,
`python3 scripts/apply_research.py --answers <file> --dry-run` and
`python3 scripts/check_evidence_archived.py <file>`. Do the work yourself; do
not spawn subagents; keep helper files in your own scratchpad folder. Report:
candidates added (jurisdiction, status, confidence), items rejected and why.
