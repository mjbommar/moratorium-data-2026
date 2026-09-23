# QA round 1: audit of the 520 rows added on 2026-09-23

You are an auditor, not a researcher. Assume each row may be wrong. Your job is
to try to break it, and to write down what you find. Reference date: 2026-09-23.

The coordinator's specific doubt: 281 of the 520 new rows carry adoption dates
before 2026-08-01, which means they were adopted before the last snapshot and
missed. That is plausible for small townships, but each one must be shown to
be (a) a temporary pause (moratorium), not a permanent ban or a zoning rule,
(b) dated by the vote that adopted THIS instrument, not an earlier instrument it
extended and not a first reading, and (c) not already in the inventory under a
different name (city vs county, "Charter Township" vs "Township", a utility
authority, an aggregate row). Items marked `OLDER_INSTRUMENT` in your packet
are these.

## Inputs

- Your packet: `work/packets/qa1/<name>.json`. Each item has the row as it is
  in the inventory, the evidence the research agent cited, and
  `archived_text`: local paths to the saved text of each source. Read those
  files first (`cat`/`sed -n`); no network is needed to start.
- `python3 scripts/show_rows.py --state <ST> --list` lists every row in the
  state, so you can check for an existing row covering the same instrument.
- `python3 scripts/show_rows.py --id <moratorium_id>` gives exact field values.
- For new searches and archiving, the same tools as `work/research-process.md`:
  `cd ~/projects/bc/bc-modules && uv run bc-web search "..." --fuse -n 10` and
  `~/projects/bc/bc-modules/.venv/bin/python scripts/save_source.py --state <ST> --print URL`
  (from the repo root; `--mode browser` for JS portals). Archive anything you
  cite that is not already archived.

## For each item

1. Read the archived evidence. Does the text actually say what the row says:
   a moratorium/pause, adopted (not just introduced) by this body, on this
   date, for this term, covering these sectors? If `quote_mismatch` is true,
   the cited quote was not found in the archived text; find out why
   (paywall stub, obfuscated text, agent paraphrase, or fabrication).
2. Check for a duplicate: same state, same body, same instrument as an
   existing row (ignore rows for a different body with a similar name).
3. If the evidence is news-only, spend one or two searches looking for the
   primary instrument (ordinance/resolution/minutes) and, for OLDER items,
   for coverage that would date the instrument differently. Do not spend more
   than ~3 searches per item.
4. Decide:
   - `confirmed_unchanged`: the row is right. Cite the evidence you checked
     (you may reuse the archived URLs) and set confidence.
   - `corrected`: a field is wrong (date, duration, sectors, legal_basis,
     jurisdiction_type, current_status...). Give `changes` with exact `from`
     values from `show_rows.py --id`.
   - `status_changed`: the enacted_status is wrong (e.g. it lapsed, or it
     was only a first reading so it is `pending`).
   - `unresolvable` with `notes` beginning `REMOVE: ...` when the row should
     not exist (permanent ban, zoning amendment, never adopted, not a
     government action, wrong state), or `DUPLICATE_OF: <moratorium_id>; ...`
     when it duplicates an existing row. The coordinator removes these by
     hand; apply_research.py skips them.
   - `unresolvable` with any other note when you cannot tell.
5. Confidence reflects the evidence you personally verified, not the
   original agent's number.

## Output

`work/answers/qa1/<name>.json` following `work/schemas/research_decision.schema.json`
(`researcher`: your model name plus "QA1"). One decision per packet item, in
packet order, and no `new_candidates`. Validate:

```bash
python3 -c "import json,jsonschema;jsonschema.validate(json.load(open('work/answers/qa1/NAME.json')),json.load(open('work/schemas/research_decision.schema.json')));print('ok')"
python3 scripts/apply_research.py --answers work/answers/qa1/NAME.json --dry-run
python3 scripts/check_evidence_archived.py work/answers/qa1/NAME.json
```

Report back: counts by outcome; every REMOVE and DUPLICATE with a one-line
reason; every date correction on an OLDER item (from -> to); and your honest
read on whether the OLDER items in your packet look like genuine misses or like
an artifact (e.g. dates copied from a roundup that listed original adoption
dates for instruments that had since been extended).

Do the work yourself; do not spawn subagents. Keep helper files in your own
uniquely named scratchpad folder.
