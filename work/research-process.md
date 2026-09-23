# Agent research process (refresh of 2026-09-23)

Instructions for one research agent assigned one state. Tested end to end on
2026-09-23 before fan-out. Follow it literally; the output contract is strict.

Reference date ("today") for every claim: **2026-09-23**.

## What you produce

One file: `work/answers/full/<ST>.json` (ST = USPS abbreviation), conforming
to `work/schemas/research_decision.schema.json`. Nothing else in the repo is
edited by you. Never touch `data/*.csv`.

The file has two parts:

1. `decisions` — one per item in your packet `work/packets/full/<ST>.json`.
   Every packet item must appear, even if the outcome is `unresolvable`.
2. `new_candidates` — moratorium instruments in your state that are **not**
   already in the inventory (adopted, extended, or formally proposed since
   roughly 2026-08-01, or older ones the inventory missed).

Set `"researcher"` to your model name (e.g. `"claude-sonnet-5 agent"`).

## Tools (all tested)

Search (Exa + Google fused, ~2 s). Run from the bc-modules directory:

```bash
cd ~/projects/bc/bc-modules
uv run bc-web search "Lowndes County Georgia data center moratorium" --fuse -n 10 --since 2026-08-01
uv run bc-web search "data center moratorium" --fuse -n 10 --site lowndescountyga.gov
uv run bc-web search "Georgia data center moratorium" --backend serpapi --engine google_news -n 10 --since 2026-08-15
```

Save every source you rely on (run from the moratorium-data-2026 repo root;
this goes through bc-web, so it escalates to a real browser for Cloudflare
and JS-only portals, and it archives the evidence for later reference):

```bash
PY=~/projects/bc/bc-modules/.venv/bin/python
$PY scripts/save_source.py --state GA --print "https://www.wtoc.com/2026/08/28/savannah-city-council-approves-155-day-moratorium-large-scale-data-centers/"
$PY scripts/save_source.py --state GA --print "https://applingcountyga.org/wp-content/uploads/2026/08/RESOLUTION-2026-40-Day-Moratorium-Data-Centers.pdf"
```

It writes `work/sources/<ST>/<hash>.pdf` + `.txt` (pdftotext, with OCR when
the PDF is a scan) or `<hash>.html` + `.md`, appends a line to
`work/sources/<ST>/manifest.jsonl`, and with `--print` shows the text
(default first 300 lines; `--lines 2000` for a long ordinance). Re-running on
the same URL is a no-op that re-prints the saved text.

If the result says `0 chars` or only a few chars, the page is JS-rendered or
challenged: re-run with `--mode browser` (DocumentCloud, Municode, Legistar,
Granicus, CivicClerk, most county agenda portals need this). If a browser
fetch is blocked by Cloudflare, add `--engine pydoll`. Several URLs can be
passed at once. **Every URL in your `evidence` arrays must have been saved
this way**; the coordinator checks the manifest. Quick look without saving:
`uv run bc-web fetch -f text URL` (from bc-modules), but save before citing.

Inventory lookups (run from the moratorium-data-2026 repo root):

```bash
python3 scripts/show_rows.py --state GA --list        # what we already have
python3 scripts/show_rows.py --id ga-savannah-2026    # exact field values for `from`
```

You may also use the built-in WebSearch / WebFetch tools as a fallback, but
prefer bc-web: it returns official sites and PDFs Google under-ranks.

## Process A: check a known row (each packet item)

1. Read the item's `context` and `questions` in the packet.
2. Search at least twice:
   - `"<Jurisdiction> <State> data center moratorium"` with `--since` set to
     ~30 days before the row's last confirmation date (usually 2026-07-01).
   - The same query restricted with `--site` to the jurisdiction's official
     domain, or to `legistar.com`, `granicus.com`, `civicplus.com`,
     `municode.com`, `civicclerk.com`, as appropriate.
   - If the row's end date has passed, add `"<Jurisdiction> data center
     ordinance adopted"` and `"<Jurisdiction> moratorium extended"`.
3. Fetch the best primary source (ordinance, resolution, agenda, minutes)
   and at least one news source if there is one. Read them; do not decide
   from snippets.
4. Decide, as of 2026-09-23:
   - Still within its term and no change found → `confirmed_unchanged`.
   - Extended → `status_changed`, `new_enacted_status: "extended"`, set
     `current_end_date_iso` (from: current value, to: new date) and update
     `current_status` and `duration` text.
   - Permanent regulations adopted → `replaced`. Lapsed without action →
     `expired`. Repealed early → `rescinded`. Pending item adopted →
     `active` (and fill `date_enacted`, `date_enacted_iso`, `duration`, etc.).
   - Term has passed but you cannot find what happened → `unresolvable`,
     cite what you checked, explain in `notes`. Do **not** guess `expired`
     on silence alone unless the instrument had a fixed end date, that date
     is past, and an official source (agenda, code, news) shows no extension
     was adopted; then `expired` with confidence ≤ 0.7 is acceptable.
5. For every `[VERIFY ...]` marker in the item, add a `verify_resolutions`
   entry (`confirmed`, `corrected`, or `still_unverifiable` with a note of
   which portals you checked).
6. `changes.<column>.from` must be the **exact** current CSV value. Use
   `show_rows.py --id` and copy it. Columns you may change: `date_enacted`,
   `date_enacted_iso`, `date_enacted_uncertainty`, `duration`,
   `duration_days`, `duration_kind`, `current_end_date_iso`, `legal_basis`,
   `trigger`, `current_status`, `affected_projects`, `outcome`, `sectors`,
   `trigger_categories`. `enacted_status` is set through
   `new_enacted_status`, not `changes`. Typed rules: `duration_days` is a
   string in `from`/`to` (e.g. `"180"`, or `""`); it must be non-empty if
   and only if `duration_kind` is `fixed_days`. `date_enacted_uncertainty`
   must match the precision of `date_enacted_iso` (`exact` for YYYY-MM-DD,
   `month_only` for YYYY-MM, `year_only` for YYYY).
7. When you change `current_status`, write it as a dated sentence:
   "Active as of 2026-09-23; ... " or "Expired 2026-08-30; ..." and remove
   any `[VERIFY]` marker you resolved from the new text.

## Process B: discover new instruments in the state

Run these searches (adjust wording to the state; run more if the state is
active). Use `--since 2026-08-01` unless noted.

```
"<State> data center moratorium"                       (fused, n=15)
"<State> data center moratorium" --engine google_news --backend serpapi
"<State> county commissioners moratorium data centers"
"<State> city council moratorium data center ordinance"
"<State> battery storage moratorium"      / "<State> BESS moratorium"
"<State> solar farm moratorium"           / "<State> wind moratorium"
"<State> cryptocurrency mining moratorium"
"<State> data center moratorium extended"
"<State> data center moratorium proposed" (pending items)
```

Also check any state-wide roundup you hit (e.g. "at least 17 Alabama cities
pause development"); fetch it and list every jurisdiction it names.

For every jurisdiction named:

1. `python3 scripts/show_rows.py --state <ST> --list` — if the jurisdiction
   is already a row, treat any news as Process A input for that row (and
   note it in that decision, even if the row was not in your packet: you may
   add decisions for rows outside the packet).
2. If not present, find the primary instrument (resolution/ordinance PDF,
   agenda item, minutes) plus a news source. Fetch and read them.
3. Write a `new_candidates` entry with every field you can support.
   `jurisdiction` is the bare name: "Marshalltown",
   "Boone County", "Lodi Township"; never "City of Marshalltown" or "Town of
   X". Disambiguate a city by its county in parentheses only when the state
   has two: "Fairfield (Jefferson County)". Follow
   the codebook: `date_enacted_iso` is the adoption vote date; `duration_days`
   for a fixed term (180 for 6 months, 365 for a year); `current_end_date_iso`
   when the instrument states or implies a calendar end date;
   `enacted_status` `pending` for proposed-not-adopted (first reading only,
   or hearing scheduled) and `active` once adopted. `sectors` is a list from
   `data_center, battery_storage, solar, wind, cryptocurrency_mining, general`.
   `legal_basis` should carry the instrument number where known
   ("Resolution 2026-14", "Ordinance No. 26-08").
4. Confidence: 0.85+ with a primary source in hand; 0.6–0.75 for two
   independent news sources; 0.5 for a single news report. Below 0.4 is
   discarded at merge time, so do not bother listing rumours.

A jurisdiction that merely *discussed* a moratorium, or a council member who
*called for* one, is not an instrument. A first reading, a scheduled public
hearing on a drafted ordinance, or a planning commission recommendation is
`pending`. Permanent zoning rules without a pause are not moratoria (they may
be the `replaced` outcome for an existing row).

## Lessons from the pilot agents

- Always include the state name in a query ("Wells Nevada", "Humboldt County
  Nevada"); many jurisdiction names exist in several states.
- `--site` restriction is unreliable for small municipal portals; if it
  returns nothing useful, run the unrestricted query with the jurisdiction
  and the words "resolution" or "ordinance" and "pdf".
- Lee Enterprises / BLOX CMS papers (elkodaily.com, many "*.com/news" local
  dailies) serve the article body ROT47-obfuscated; if the saved markdown
  looks like gibberish, decode it (Python: `codecs`-style ROT47 over ASCII
  33–126) or find a second source.
- Scanned resolutions are common; `save_source.py` OCRs them automatically.
- A permanent ban or permanent zoning rule adopted *instead of* a pause is
  not a new moratorium row: fold it into the existing row's `current_status`
  (and `outcome`), or, when there is no existing row, record it only if the
  instrument itself is framed as a moratorium/pause. Tribal governments count
  as jurisdictions (`jurisdiction_type: Tribal`).
- CivicClerk portal links (`*.portal.civicclerk.com/event/N/files/attachment/M`)
  are an empty JS shell. Use the API instead:
  `https://<city>.api.civicclerk.com/v1/Meetings/GetMeetingFileStream(fileId=M,plainText=false)`
  (the PDF) and `https://<city>.api.civicclerk.com/v1/Events/N` (lists a
  meeting's files).
- `--site` with a domain the backends have not indexed makes Google return
  nothing and Exa silently ignore the filter and return unrelated pages
  (dictionary entries, unrelated agencies). Treat that as "no results".
- Statewide roundups often carry the full list of jurisdictions only in an
  embedded Datawrapper map; its data is at
  `https://datawrapper.dwcdn.net/<id>/<version>/dataset.csv` (find the id in
  the page HTML). Archive the CSV with save_source.py; its dates can be off by
  a day or two, so confirm each against a local source.
- A `TargetClosedError` / `CDPSession.send` traceback printed by a browser
  fetch is noise when the line after it says `saved`; ignore it.
- bc-web is being edited in another session. If save_source.py prints a
  `SyntaxError`/`ImportError` from `bc_web`, it retries three times 20 s apart
  on its own; if it still fails, pass `--mode http` (works for most PDFs and
  news pages) and retry the browser fetch later.
- Akamai/other bot-check pages (WTOL and some TV-station sites) return no
  article text even in browser mode; find another source rather than citing
  the blocked page.
- save_source.py OCRs only pages that have almost no text, so mixed
  packets (typed agenda + scanned minutes) come out complete.
- Packets over 20 items are split into `<ST>-part1.json`, `<ST>-part2.json`;
  each part writes its own answer file named in the packet's `answer_file`.
  Process B (discovery) is done only by the agent holding part 1.

## Evidence entries

Every decision and candidate needs `evidence` with real URLs you fetched.
`source_type` from: ordinance, resolution, minutes, agenda, staff_report,
court_filing, legislature, news, other. Include a short verbatim `quote`
that establishes the claim (the vote, the term, the end date). Prefer the
primary source; a news source alone is acceptable but lowers confidence.

## Scratchpad hygiene

The scratchpad directory is shared by every agent in this run. Put all of
your helper files in your own folder, `<scratchpad>/<ST>_<random>/`, and
never run a script by a generic name (`assemble.py`, `ms.sh`) from the
scratchpad root: one agent's build script has already overwritten another
state's answer file this way.

## Before you finish

```bash
cd ~/projects/personal/moratorium-data-2026
python3 - <<'EOF'
import json, jsonschema
s = json.load(open("work/schemas/research_decision.schema.json"))
d = json.load(open("work/answers/full/ST.json"))   # your file
jsonschema.validate(d, s); print("schema ok", len(d["decisions"]), "decisions", len(d.get("new_candidates", [])), "candidates")
EOF
python3 scripts/apply_research.py --answers work/answers/full/ST.json --dry-run
```

The dry run must list no conflicts (a "Conflicts" section, or an "unknown moratorium_id" line). If it does, your `from` value is
wrong; re-copy it from `show_rows.py`. Do not run apply without `--dry-run`;
the coordinator merges.

Report back (in your final message) a short summary: counts by outcome,
the list of new candidates with jurisdiction and status, and anything you
could not resolve and why.
