# `work/` — the refresh machinery

A moratorium is a time-bounded instrument. A row that is correct today becomes
wrong on a date already written into the record, and nothing external tells us
when that happens. Keeping this dataset true therefore needs a repeatable cycle,
not occasional edits. This directory holds that cycle's contracts and its paper
trail.

## What is tracked here

| Path | What it is |
|---|---|
| `schemas/` | The output contract every research pass must satisfy. `research_decision.schema.json` covers inventory rows; `legislation_decision.schema.json` covers state bills. |
| `answers/` | The research record. One JSON file per state per pass, with the evidence — URLs actually fetched, source types, and quoted operative language — behind every change we made. |
| `audit/` | One file per merge run: every field changed, its before and after value, the stated reason, and which answer file it came from. |
| `sources/` | The evidence archive (added 2026-09-23). One folder per state holding the extracted text or markdown of every URL cited in an answer file, and a `manifest.jsonl` with the final URL, HTTP status, fetch tier, body sha256 and saved paths. Raw PDFs and HTML are kept on disk but not committed (1.8 GB); the hash lets a copy be verified. |
| `research-process.md` | The procedure each research agent follows: tool commands, decision rules, output contract. Tested on two pilot states before fan-out. |
| `progress-2026-09-23.md` | The coordinator's log for the September pass: which agent took which state, gate results, merge-time follow-ups. |

## What is not tracked

`packets/`, `worklist-*.json`, `chronology/`, and `sibling-gaps.json` are derived
from the CSVs and regenerable with `make worklist`. They are inputs to research,
not evidence, so they are gitignored.

## Why answers are JSON and not edits

Research never writes to a CSV. It emits a decision file, and
`scripts/apply_research.py` merges it. That indirection buys three things:

1. **A conflict guard.** Every proposed change carries the value it expects to
   find. If the CSV no longer holds that value, the change is refused and
   reported rather than applied — which is how a stale answer, written against a
   revision that another pass has since corrected, gets caught. This fires in
   practice; it is not theoretical.
2. **Idempotence.** Re-running a merge over already-applied answers is a no-op,
   so answers can be applied as they land, state by state.
3. **Auditability.** Every value in the published CSVs can be traced to a source
   URL through `audit/` and `answers/`.

## Reading an answer file

Each decision records an `outcome`:

- `confirmed_unchanged` — the record was checked and is still accurate. This is a
  real finding, not a no-op.
- `status_changed` — the instrument was extended, replaced, expired, or rescinded.
- `corrected` — a non-status factual error was fixed.
- `unresolvable` — no adequate source was found, and the record was left alone.

`unresolvable` is deliberately first-class. Many small jurisdictions simply do
not publish signed ordinances, and a dataset that says so is more useful than one
that quietly asserts something it cannot support. The same applies to
`verify_resolutions`, where `still_unverifiable` keeps the `[VERIFY]` marker in
place and records which portals were checked, so the next pass does not repeat
the work.
