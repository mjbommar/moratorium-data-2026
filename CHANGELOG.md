# Changelog

## v2026.04.1 — 2026-04-30 (data-quality patch)

Five fixes after community review of the v2026.04 initial release.

### Data changes

- **Deduplicated Arkansas/Harrison.** Dropped the duplicate "City of Harrison, AR" row that the Feb 2026 baseline `update_inventory.py` was re-injecting on top of the April codex extract. The April record (jurisdiction = "Harrison") had the better disposition data — confirming the moratorium was *repealed* on 2023-11-28 — while the Feb stub was still flagged `[VERIFY]`. The fix: remove the Feb baseline entry from `get_new_entries()` and rely on the April extract. **Headline 223 → 222.**
- **Normalized New Jersey's activity_level.** The `summary_stats.json` value `"None for formal moratoria; High for non-moratorium restrictions"` violated the codebook's closed vocabulary. Replaced with `None` (this dataset specifically tracks formal moratoria); the qualifying narrative moves into `state_details["New Jersey"].activity_notes` so it remains discoverable.

### Schema additions

- **New column `enacted_status`** in the inventory CSV — closed-vocab classification derived from the free-text `current_status` and `outcome` fields. Values: `active`, `extended`, `replaced`, `expired`, `rescinded`, `pending`. Use this for filtering rather than parsing the free-text status.
- **New column `moratorium_id`** in the inventory CSV — stable identifier of the form `<state>-<jurisdiction-slug>-<year>`, with `-pN` appended for explicitly-numbered phases (e.g., Oliver County, ND has `-p1`, `-p2`, `-p3`). Use as a primary key for joins across releases.
- **New `enacted_status_breakdown` object** in `summary_stats.json` — counts of rows by status bucket.

### Documentation

- **Rewrote the `state_legislation.csv` section of the codebook** to match the actual CSV columns (`bill`, `sponsors`, `party`, `status`, `key_provisions`, `activity_level`). The previous codebook described columns that didn't exist.
- **Clarified `structured_extractions.jsonl` wording** in README and `data/README.md`. The file contains 864 lines (526 successful extractions + 338 LLM-call errors). The n=348 cohort cited in the paper is the confidence-≥-0.4 subset of the successful extractions.
- **README headline split** into "in force / pending / past" so the 222 isn't read as "222 moratoria currently in force." It's "222 moratorium instruments tracked: 100 in force, 71 pending, 51 past."

### Status of headline counts

- **222 moratorium instruments** total
- **100 currently in force** (active + extended)
- **71 pending or proposed** (not yet adopted)
- **51 past** (replaced, expired, or rescinded)
- **30 states** with at least one instrument

### Audit trail

A targeted dedup audit across all 30 states (normalized jurisdiction comparison + same-date + same-ordinance signals) found exactly one structural duplicate in v2026.04: the Harrison/AR pair fixed in this release. The other duplicate-shaped pairs flagged by the audit (Oliver County ND Phase 1/2/3, Lamar+Pike GA, Dundee+Sylvan Townships MI, Saginaw+Saline cities MI) were verified as **not duplicates** — separate instruments at different jurisdictions or in different time periods.

---

## v2026.04 — April 2026 (initial public release)

**Cutoff:** 2026-04-29

### What's in this release

- **223 moratoria** across 30 states in the cleaned inventory (later corrected to 222 in v2026.04.1)
- **413 state-level bills** tracked in 2025–2026
- **348 moratorium texts** structurally extracted with the 44-clause taxonomy (cohort filtered at confidence ≥ 0.4)
- **~4,400 original source documents** used to build the corpus

### Top states (initial)

1. Ohio — 35
2. Michigan — 34
3. Georgia — 24
4. North Carolina — 19
5. Iowa — 12
6. Indiana — 11
7. Washington — 11
8. Kansas — 8
9. North Dakota — 7
10. Tennessee — 6

### Notable findings

- The pace is accelerating: 130 moratoria were enacted in just the first four months of 2026 — more than in all of 2025.
- Ohio overtook Michigan as the highest-volume state.
- Most moratoria target data centers (~93%). Cryptocurrency mining, battery storage, solar, and wind appear at smaller but non-trivial volumes.
- 58.9% of analyzed moratoria provide no formal definition of the regulated use; 77.3% include no exemptions; only 23.6% contain detailed legislative findings.
- One tribal moratorium (Sault Tribe of Chippewa Indians, April 2026) is the first such record in our corpus.
- One utility-authority moratorium (Ypsilanti Community Utilities Authority, April 2026) is the first such record on water/sewer hookups for hyperscale data centers.

### Coming in the next release (planned ~Q3 2026)

- Searchable, filterable web table on a GitHub Pages site
- Zenodo DOI minted for this release and all future ones
- Geocoding of every jurisdiction
- Outcome tracking: each moratorium followed from enactment through replacement/extension/expiration/rescission
