# Headline review

**Result: arithmetic and retained ledger match the current working data; two generator robustness gaps need attention.** This review does not establish final freshness, legal force, complete coverage, or downstream compatibility.

- **Medium — schema loss:** `scripts/build_refresh_headline_delta.py:23-25` accepts duplicate CSV headers and silently discards earlier values. A synthetic `id,value,value` row retained only the last value. Header-only changes also escape row-level diffs. Validate headers and report schema differences explicitly.
- **Medium — retirement check bypass:** `scripts/build_refresh_headline_delta.py:83-90` skips unexplained-removal validation if the registry is absent. The current registry is present and resolves `wa-seattle-2026-2` to `wa-seattle-2026`; the gap concerns missing-registry runs.

Independent comparison with source commit `dbaab04` confirms 1,291 → 1,330 local records (40 additions, one retirement), **666 surviving local rows changed**, and 440 → 442 state-policy records (two additions), **111 surviving policy rows changed**. Typed bills are **438 → 427**: 13 existing rows reclassified and two bill rows added. The retained JSON exactly equals a fresh in-memory build, and its CSV byte hashes match. Current and baseline headers match.

The retained frozen projection has 49 published IDs and seven pending groups; all 49 IDs remain, with two additional current IDs. Current data contain 49 voted, one scheduled and one litigated measure. All 57 retained results relate to voted measures; 50 are current by supersession and five of those are certified. Historical projection total 50 is distinct from current 51. The reviewed prose distinguishes the historical source baseline from the last public release and qualifies legal force and results appropriately.

All three targeted tests passed with the existing BC Python and bytecode disabled. Import and comparison were performed without source mutation; exclusive creation protects an existing output file. Working-file SHA-256 hashes and details are in `review.json`. This is an arithmetic and representation review, not independent verification of every underlying source or consumer.
