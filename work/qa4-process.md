# QA round 4: label consistency

Each packet item is an inventory row with one or more `flags` from deterministic
checks. Resolve every flag with evidence, as of 2026-09-23. Read
`work/qa-process.md` for tools, archiving and the output contract; the same
rules apply (archive every cited URL with `save_source.py --state <ST>`, exact
`from` values from `show_rows.py --id`, no new_candidates).

Flag meanings and what "resolved" looks like:

- `EXTENDED_NO_END_DATE`: find the extension instrument and set
  `current_end_date_iso` (YYYY-MM-DD). If the extension is event-based (until
  regulations are adopted), leave it blank, set `duration_kind` to
  `until_event`, and say so in `current_status`. If you cannot find the
  extension's endpoint after ~3 searches, `unresolvable` with the portals checked.
- `END_DATE_PASSED` / `COMPUTED_EXPIRY_PASSED`: the row is in force but its
  term has run out. Find what happened: extended (`status_changed` ->
  `extended`, new end date), replaced, lapsed (`expired`, only if an official
  agenda/minutes or news shows no extension), or still pending a vote (note it).
- `PENDING_WITH_DATE`: either the instrument was adopted on that date (status
  -> `active` and fill the term) or the date is a hearing/first reading (blank
  `date_enacted_iso`, set `date_enacted_uncertainty` to `unverified`).
- `DURATION_MISMATCH`: `duration_days` must be the ORIGINAL term in days (180
  for six months, 365 for a year). Extensions go in `current_end_date_iso`
  and text. Fix whichever side is wrong; if the text's first number is an
  earlier proposal or an extension, the typed value may already be right:
  then `confirmed_unchanged` with a note.
- `SECTOR_CHECK`: read the instrument (or best source). Add the sector only
  if the moratorium's operative scope covers it. A trigger mention, an
  exclusion ("does not apply to solar"), or a separate instrument does not
  count. `sectors` is a JSON list string, e.g. `["data_center","battery_storage"]`
  in the order data_center, battery_storage, solar, wind, cryptocurrency_mining, general.
- `DUP_MARKER`: two or three rows share a jurisdiction and none carries an
  instrument number, so the validator cannot tell them apart. Put the
  resolution/ordinance number (or, failing that, "(first instrument, <month
  year>)" / "(second instrument, <month year>)") at the start of `legal_basis`.

Output: one file per state, `work/answers/qa4/<ST>.json`, one decision per
packet row for that state (a row with several flags gets one decision
addressing all of them). Validate each with the schema check,
`apply_research.py --dry-run` and `check_evidence_archived.py`. Do the work
yourself; do not spawn subagents; keep helper files in your own scratchpad folder.
Report per state: flags resolved, changes made, anything unresolvable.
