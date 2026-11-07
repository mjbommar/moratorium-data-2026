# Core publication-surface audit — 2026-11-07

Final release remains unfinished. Working counts independently read from CSVs: **1,330 local records, 442 state-policy records (427 bills), and 51 reviewed measure/proposal records**. GeoJSON contains 1,289 features. These are separate populations; source and legal-status dates vary.

Three read-only generator checks passed: summary statistics, GeoJSON, and landing-page substitutions. They establish consistency with generator inputs, not legal truth, full copy review, or release readiness. The repository changed concurrently; this audit is a point-in-time observation. No raw source bodies are included.

## Corrections possible now

- Correct the codebook unflagged subtotal **627 → 626** (1,330 − 704); reconcile generated HTML.
- Remove the unsupported ≥99% current geocode accuracy inference; 89 historical checks are not a representative current-population accuracy study.
- Replace “roughly half” wording for the historical clause cohort with the explicit 348 documents / 211 jurisdictions and its pre-April-28 cutoff; these are not directly comparable units to 1,330 instrument records.
- Fix the clean inventory table generator: its April caption conflicts with later rows and several formatted dates contain impossible months (13, 47, 83). Verify raw dates before attributing the defect.
- Qualify the scripts README claim of exhaustive headline coverage; the checker is pattern-based and selected. Scope the September-only gap statement as historical. Substantiate or temper the FAQ’s capital, replacement and causal claims and the landing page’s duration/trigger generalizations.

These are recommendations only; no repository edits were made. Historical paper statistics and dated changelog entries should not be globally rewritten.

## Surface register

### canonical-downloads

**Paths:** `data/expanded-csv/ballot_measures.csv`, `data/expanded-csv/claims.csv`, `data/expanded-csv/coverage_observations.csv`, `data/expanded-csv/elections.csv`, `data/expanded-csv/instrument_event_status.csv`, `data/expanded-csv/instrument_events.csv`, `data/expanded-csv/instrument_events_current.csv`, `data/expanded-csv/jurisdictions.csv`, `data/expanded-csv/local_restrictions.csv`, `data/expanded-csv/manifest.json`, `data/expanded-csv/measure_instrument_links.csv`, `data/expanded-csv/measure_provisions.csv`, `data/expanded-csv/measure_results.csv`, `data/expanded-csv/measure_results_current.csv`, `data/expanded-csv/review_decisions.csv`, `data/expanded-csv/search_attempts.csv`, `data/expanded-csv/search_runs.csv`, `data/expanded-csv/search_sightings.csv`, `data/expanded-csv/source_documents.csv`, `data/expanded/publication.json`, `data/moratorium_inventory.csv`, `data/state_legislation.csv`, `data/summary_stats.json`.

**Authoritative input:** Legacy CSVs for local and state records; pinned data/expanded canonical snapshot and expanded-csv projection manifest; source review receipts.  **Classification:** canonical inputs and generated downloads.  **Cutoff/version:** November 5 working cohort; source dates vary; expanded f1dbb869 and CSV bfc06507 observed via symlinks.

**Evidence and limits:** Direct CSV row counts 1330, 442, 51; summary reports 427 bills, 15 non-bill records, 704 verify-tagged and 626 untagged. These are records, not live force or election wins. summary --check passed; projection row content and every hash not independently reviewed.

**Reviewer role:** data curator and legal/elections reviewers.  **Completion:** working counts checked; record freshness and final freeze open.

**Validation:** `python3 scripts/build_summary_stats.py --check`

**Next action:** Reconcile record-specific sources, pin final snapshot and independently validate all exports and hash manifest.

### repository-readme

**Paths:** `README.md`.

**Authoritative input:** CSV, summary statistics, expanded snapshot, reviewed records; release remote metadata.  **Classification:** manual current copy.  **Cutoff/version:** November 5 working cohort; April paper and September prior baseline.

**Evidence and limits:** README distinguishes source dates, proposals and historical paper; pinning main in examples is moving, not reproducible. Remote tag/release statements dated November 5 were not checked live.

**Reviewer role:** data editor and release reviewer.  **Completion:** partial claim review; not release approved.

**Validation:** `python3 scripts/check_docs_numbers.py`

**Next action:** Pin examples to final release and recheck counts, links, historical claims and remote metadata.

### data-readme

**Paths:** `data/README.md`, `data/index.html`.

**Authoritative input:** CSV and expanded projection manifest.  **Classification:** manual source and generated HTML.  **Cutoff/version:** working snapshot; mixed per-record observation dates.

**Evidence and limits:** Data README states 1330 local, 442 state-policy, 51 ballot and 1289 coordinates; separates historical September baseline and unpublished release. HTML and all table rows not independently reconciled.

**Reviewer role:** data editor and elections reviewer.  **Completion:** partial; currently modified by another concurrent change.

**Validation:** `python3 scripts/check_docs_numbers.py`

**Next action:** Review final bytes and regenerate HTML after the snapshot is frozen; verify all export links and manifest totals.

### operator-readmes

**Paths:** `scripts/README.md`, `work/README.md`.

**Authoritative input:** actual scripts, workflow contracts, archival/privacy rules.  **Classification:** manual operational copy.  **Cutoff/version:** mixed historical and current workflow.

**Evidence and limits:** scripts README claims number checker verifies every headline and all LaTeX tables regenerate; plan says checker is selected patterns and table generation has historical cases. work README describes public-source body commits; present private/public archive policy requires current review. No raw source bodies copied.

**Reviewer role:** tooling maintainer and privacy reviewer.  **Completion:** correction identified; workflow not exhaustively verified.

**Validation:** `python3 scripts/check_docs_numbers.py --help`

**Next action:** Qualify checker coverage; inventory actual generators, current archival policy and commands against code.

### faq

**Paths:** `docs/FAQ.html`, `docs/FAQ.md`.

**Authoritative input:** reviewed canonical data, source evidence for economic claims, election results.  **Classification:** manual Markdown and generated HTML.  **Cutoff/version:** November 5 working cohort; historical original extraction.

**Evidence and limits:** FAQ separates 51 reviewed proposals/measures and original 348 extraction instruments; $1 trillion capital commitments and assertions that many pauses were replaced within 6–12 months lack substantiation in inspected text; exact current frequency and causal claim need evidence.

**Reviewer role:** subject-matter editor and elections/legal reviewers.  **Completion:** substantive claims need evidence; HTML not fully checked.

**Validation:** `rg -n "trillion|6 to 12|ballot|release" docs/FAQ.md`

**Next action:** Source and date capital figure; calculate qualified replacement distribution or soften/remove; reconcile current HTML.

### methodology

**Paths:** `docs/methodology.html`, `docs/methodology.md`.

**Authoritative input:** research protocols, canonical inventory, historical extraction and geocoding audit.  **Classification:** manual Markdown and generated HTML.  **Cutoff/version:** historical April collection; November 5 working cohort.

**Evidence and limits:** Methodology explicitly warns 89 geocode checks do not establish accuracy for current inventory; 1289 of 1330 coordinates; incomplete record-level force. Historical model/document counts are original collection, not refresh-wide.

**Reviewer role:** methods and geographic reviewer.  **Completion:** partial review; rendered version not verified.

**Validation:** `rg -n "historical|1330|89 verifications|geocod" docs/methodology.md`

**Next action:** Verify cohort denominators and collection phases, then inspect final rendered method and links.

### codebook

**Paths:** `docs/codebook.html`, `docs/codebook.md`, `docs/event-validity-publication.md`, `docs/expanded-data-contracts.md`.

**Authoritative input:** CSV schemas, summary_stats.json, expanded snapshot/contracts.  **Classification:** manual documentation and generated HTML.  **Cutoff/version:** working November; expanded event profile as selected in publication.

**Evidence and limits:** codebook line 150 says 627 without verify tags; summary and 1330-704 say 626. Lines 165–169 say historical 211-jurisdiction cohort covers roughly half the current inventory: incomparable units and stale framing. It distinguishes pending/adoption and current force.

**Reviewer role:** schema maintainer and legal reviewer.  **Completion:** specific corrections ready; expanded field contracts not exhaustively reviewed.

**Validation:** `python3 scripts/check_docs_numbers.py`

**Next action:** Correct 627 to 626 and replace half claim with dated 348 texts/211 jurisdictions without treating either as a fraction of 1330 instruments; reconcile HTML and field definitions.

### known-gaps

**Paths:** `docs/known-gaps.html`, `docs/known-gaps.md`.

**Authoritative input:** record review receipts, inventory, sweep logs, historical geocode study.  **Classification:** manual Markdown and generated HTML.  **Cutoff/version:** mixed historical releases and November reviews.

**Evidence and limits:** Line 370 infers ≥99% geocode accuracy from 89 historical checks; methodology explicitly says that sample does not establish current accuracy. Line 266 says roughly half the rows, inconsistent with current units/cohort. Lines 219–222 exclude post-September events in a historical section but need explicit historical scoping. Freshness acceptance remains open.

**Reviewer role:** methods, geographic and legal reviewer.  **Completion:** corrections identified; individual legal cases not re-adjudicated.

**Validation:** `rg -n "99%|roughly half|September 23, 2026 is not|freshness" docs/known-gaps.md`

**Next action:** Remove unsupported current accuracy inference, scope old snapshot text and replace old ratio; review examples and live gaps individually.

### ballot-publication

**Paths:** `docs/ballot-measures.html`, `docs/ballot-measures.md`, `docs/ballot-results.html`, `docs/ballot-results.md`.

**Authoritative input:** expanded reviewed measures/results/provisions/links and pinned generation manifest.  **Classification:** generated summary and rendered pages.  **Cutoff/version:** 51 reviewed measure/proposal records; separate election observation dates.

**Evidence and limits:** Results page states 49 voted, 1 scheduled, 1 litigated; labels bindingness, polarity, scope and certification with unknowns and unofficial observations. Partial county returns cannot stand for whole electorate; no current legal-force inference.

**Reviewer role:** elections and legal reviewers.  **Completion:** scoped inspection, not independent adjudication of 51 cases.

**Validation:** `python3 scripts/build_ballot_summary.py --check`

**Next action:** Check final generator output and source evidence for each promoted claim, including certification, reporting scope and effect.

### state-pages

**Paths:** `states/README.md`, `states/alabama.html`, `states/alabama.md`, `states/alaska.html`, `states/alaska.md`, `states/arizona.html`, `states/arizona.md`, `states/arkansas.html`, `states/arkansas.md`, `states/california.html`, `states/california.md`, `states/colorado.html`, `states/colorado.md`, `states/connecticut.html`, `states/connecticut.md`, `states/delaware.html`, `states/delaware.md`, `states/florida.html`, `states/florida.md`, `states/georgia.html`, `states/georgia.md`, `states/idaho.html`, `states/idaho.md`, `states/illinois.html`, `states/illinois.md`, `states/index.html`, `states/indiana.html`, `states/indiana.md`, `states/iowa.html`, `states/iowa.md`, `states/kansas.html`, `states/kansas.md`, `states/kentucky.html`, `states/kentucky.md`, `states/louisiana.html`, `states/louisiana.md`, `states/maine.html`, `states/maine.md`, `states/maryland.html`, `states/maryland.md`, `states/massachusetts.html`, `states/massachusetts.md`, `states/michigan.html`, `states/michigan.md`, `states/minnesota.html`, `states/minnesota.md`, `states/mississippi.html`, `states/mississippi.md`, `states/missouri.html`, `states/missouri.md`, `states/montana.html`, `states/montana.md`, `states/nebraska.html`, `states/nebraska.md`, `states/nevada.html`, `states/nevada.md`, `states/new-hampshire.html`, `states/new-hampshire.md`, `states/new-jersey.html`, `states/new-jersey.md`, `states/new-mexico.html`, `states/new-mexico.md`, `states/new-york.html`, `states/new-york.md`, `states/north-carolina.html`, `states/north-carolina.md`, `states/north-dakota.html`, `states/north-dakota.md`, `states/ohio.html`, `states/ohio.md`, `states/oklahoma.html`, `states/oklahoma.md`, `states/oregon.html`, `states/oregon.md`, `states/pennsylvania.html`, `states/pennsylvania.md`, `states/rhode-island.html`, `states/rhode-island.md`, `states/south-carolina.html`, `states/south-carolina.md`, `states/south-dakota.html`, `states/south-dakota.md`, `states/tennessee.html`, `states/tennessee.md`, `states/texas.html`, `states/texas.md`, `states/utah.html`, `states/utah.md`, `states/vermont.html`, `states/vermont.md`, `states/virginia.html`, `states/virginia.md`, `states/washington.html`, `states/washington.md`, `states/wisconsin.html`, `states/wisconsin.md`.

**Authoritative input:** moratorium_inventory.csv, state_legislation.csv, update_state_counts.py and build_site.py.  **Classification:** generated state Markdown/index and rendered HTML.  **Cutoff/version:** state index says generated November 7; source and status dates vary.

**Evidence and limits:** State index 1330, 1079 active/extended classification, 79 pending, 172 past; 47 states. Those are classified records, not present legal force. Index inspected and Pennsylvania examples sampled; individual narratives and rendered pages not exhaustively reviewed. 50-state coverage must not be inferred from existence of files.

**Reviewer role:** state data editors and legal reviewers.  **Completion:** group inventoried; per-state narrative and HTML verification outstanding.

**Validation:** `python3 scripts/check_docs_numbers.py`

**Next action:** Compare each page row/identity/status with frozen inputs, check formerly empty states and reviewed restrictions, inspect rendered HTML and links.

### landing

**Paths:** `index.html`, `scripts/build_index.py`.

**Authoritative input:** inventory, state policy and manually maintained landing copy.  **Classification:** generated substitutions plus manual HTML.  **Cutoff/version:** November 5 working cohort; April paper and September chart historical.

**Evidence and limits:** index --check passed; headline 1330/442 and 1289 mapped; April paper explicitly historical and timeline labeled September. Line 759 claims most terms 6–12 months and trigger almost always a zoning gap without inspected calculation; map wording does not explain all 41 missing coordinates. Metadata updated date is cohort rather than full record freshness.

**Reviewer role:** web editor, statistical and legal reviewers.  **Completion:** numeric generator passes; substantive and rendered review incomplete.

**Validation:** `python3 scripts/build_index.py --check`

**Next action:** Quantify or qualify duration and trigger claims, disclose 41 missing points, reconcile final links and inspect browser-rendered site.

### rendered-site

**Paths:** `data/index.html`, `docs/FAQ.html`, `docs/ballot-measures.html`, `docs/ballot-results.html`, `docs/codebook.html`, `docs/expanded-data-contracts.html`, `docs/expanded-identity-registry.html`, `docs/expanded-promotion.html`, `docs/known-gaps.html`, `docs/methodology.html`, `scripts/build_site.py`, `states/alabama.html`, `states/alaska.html`, `states/arizona.html`, `states/arkansas.html`, `states/california.html`, `states/colorado.html`, `states/connecticut.html`, `states/delaware.html`, `states/florida.html`, `states/georgia.html`, `states/idaho.html`, `states/illinois.html`, `states/index.html`, `states/indiana.html`, `states/iowa.html`, `states/kansas.html`, `states/kentucky.html`, `states/louisiana.html`, `states/maine.html`, `states/maryland.html`, `states/massachusetts.html`, `states/michigan.html`, `states/minnesota.html`, `states/mississippi.html`, `states/missouri.html`, `states/montana.html`, `states/nebraska.html`, `states/nevada.html`, `states/new-hampshire.html`, `states/new-jersey.html`, `states/new-mexico.html`, `states/new-york.html`, `states/north-carolina.html`, `states/north-dakota.html`, `states/ohio.html`, `states/oklahoma.html`, `states/oregon.html`, `states/pennsylvania.html`, `states/rhode-island.html`, `states/south-carolina.html`, `states/south-dakota.html`, `states/tennessee.html`, `states/texas.html`, `states/utah.html`, `states/vermont.html`, `states/virginia.html`, `states/washington.html`, `states/wisconsin.html`.

**Authoritative input:** corresponding Markdown and build_site.py.  **Classification:** generated HTML.  **Cutoff/version:** source-dependent; no single refresh cutoff.

**Evidence and limits:** Build-site source enumerates render targets and rewrites links; prior TODO reports 59 pages/953 references checked, not independently repeated here. Current working files changed during audit.

**Reviewer role:** web maintainer.  **Completion:** inventory only; no full rendered-content or live deployment check.

**Validation:** `python3 -m pytest -q tests/test_site_links.py`

**Next action:** Build in isolated copy after freeze; inspect rendered pages, links, fragments and hosted bytes.

### geojson

**Paths:** `scripts/build_geojson.py`, `site/moratoria.geojson`.

**Authoritative input:** inventory rows with coordinates.  **Classification:** generated.  **Cutoff/version:** current working inventory; individual source dates vary.

**Evidence and limits:** Parsed 1289 GeoJSON features; generator --check passed. Coordinates are reference points, not legal boundaries or proof of project applicability; individual feature identity not verified.

**Reviewer role:** GIS reviewer.  **Completion:** generator consistency checked; geographic correctness open.

**Validation:** `python3 scripts/build_geojson.py --check`

**Next action:** Review ambiguous coordinates and tooltips against documented overrides and primary jurisdiction evidence.

### timeline

**Paths:** `scripts/make_timeline.py`, `site/timeline.svg`.

**Authoritative input:** historical inventory export for existing graphic; generator reads current CSV date and first sector.  **Classification:** generated historical chart.  **Cutoff/version:** landing labels existing chart September 23 2026.

**Evidence and limits:** Landing explicitly calls graphic historical. Generator uses first sector, so multi-label sector distributions require that qualification; neither SVG rendered image nor generation provenance independently established.

**Reviewer role:** visualization and methods reviewer.  **Completion:** historical disposition plausible, visual verification open.

**Validation:** `rg -n "sector|date_enacted|Historical" scripts/make_timeline.py index.html`

**Next action:** Render and inspect chart; pin historical input or regenerate from final snapshot with primary-sector and missing-date caveats.

### figures

**Paths:** `figures/pdf/map-home-rule.pdf`, `figures/pdf/map-legal-authority.pdf`, `figures/pdf/map-moratorium-counts.pdf`, `figures/pdf/map-preemption.pdf`, `figures/pdf/map-sector-composition.pdf`, `figures/pdf/map-statutory-duration.pdf`, `figures/pdf/map-timeline-heatmap.pdf`, `figures/png/map-home-rule.png`, `figures/png/map-legal-authority.png`, `figures/png/map-moratorium-counts.png`, `figures/png/map-preemption.png`, `figures/png/map-sector-composition.png`, `figures/png/map-statutory-duration.png`, `figures/png/map-timeline-heatmap.png`, `figures/svg/map-home-rule.svg`, `figures/svg/map-legal-authority.svg`, `figures/svg/map-moratorium-counts.svg`, `figures/svg/map-preemption.svg`, `figures/svg/map-sector-composition.svg`, `figures/svg/map-statutory-duration.svg`, `figures/svg/map-timeline-heatmap.svg`.

**Authoritative input:** inventory and maps scripts plus embedded state classifications.  **Classification:** generated binaries and SVG.  **Cutoff/version:** mixed historical cohorts; no independent per-file provenance established.

**Evidence and limits:** 21 map files inventoried across seven maps and three formats; code loads inventory and static dictionaries. Landing cites older graphics as historical; graphic internals and rendered images not visually inspected.

**Reviewer role:** GIS, legal and visualization reviewers.  **Completion:** unverified figures; not release approved.

**Validation:** `rg -n "read_csv|savefig|2026" scripts/moratorium_maps`

**Next action:** Inspect all graphics and sources, date and label each, review legal classification assumptions and regenerate or retire stale maps.

### latex-tables

**Paths:** `scripts/generate_tables/__init__.py`, `scripts/generate_tables/__main__.py`, `scripts/generate_tables/_common.py`, `scripts/generate_tables/definitional_approaches.py`, `scripts/generate_tables/findings_impact.py`, `scripts/generate_tables/inventory_clean.py`, `scripts/generate_tables/sector_specific_clauses.py`, `scripts/generate_tables/state_sector_counts.py`, `scripts/generate_tables/temporal_distribution.py`, `scripts/generate_tables/top_states.py`, `tables/clause-prevalence.tex`, `tables/definitional-approaches.tex`, `tables/findings-impact.tex`, `tables/moratorium-inventory-clean.tex`, `tables/moratorium-inventory.tex`, `tables/sector-specific-clauses.tex`, `tables/state-sector-counts.tex`, `tables/temporal-distribution.tex`, `tables/top-states.tex`.

**Authoritative input:** inventory/summary and historical clause_extraction_analysis.json.  **Classification:** generated and historical tables.  **Cutoff/version:** mixed; extraction cohort pre-2026-04-28.

**Evidence and limits:** moratorium-inventory-clean.tex:23 says current through April yet includes August/September rows; lines 93,97,114 have impossible months 47,13,83, indicating malformed formatting. Source inventory_clean.py hard-codes April caption; inspect raw date fields before assigning cause. Clause sample uses 348 documents/211 jurisdictions, not current 1330-record population. Other table contents not independently reconciled.

**Reviewer role:** table maintainer and quantitative reviewer.  **Completion:** concrete defects; full table audit outstanding.

**Validation:** `rg -n "Data current through April|2026-(13|47|83)" tables/moratorium-inventory-clean.tex`

**Next action:** Fix date parsing and generator caption; compare every generated row and dated denominators in isolated build, then review clause tables as historical.

### citation-changelog-release

**Paths:** `CHANGELOG.md`, `CITATION.cff`, `work/audit/release-candidate-2026-11-06/manifest.json`, `work/audit/release-candidate-updated-2026-11-06/manifest.json`, `work/audit/release-package-closure-2026-11-07.json`.

**Authoritative input:** final pinned release inputs, change ledger, version/tag and public asset hashes.  **Classification:** manual metadata and generated candidate manifest.  **Cutoff/version:** CITATION 2026.07 / 2026-07-31; candidate marked unreleased_preparation, November 5 cutoff.

**Evidence and limits:** CITATION version/date refer to July working edition; README reports July label unpublished and latest remote tag April as of November 5; no live remote check performed. Candidate manifest is preparation, not final publication. Historical changelog entries must retain their dates.

**Reviewer role:** release manager and data curator.  **Completion:** version/citation reconciliation and final release open.

**Validation:** `python3 scripts/verify_release_candidate.py --help`

**Next action:** Verify remote refs and draft independently; choose final version after freeze, prepare asset manifest and checksums and update current citation without inventing DOI.

### bundled-paper

**Paths:** `paper/moratorium-nation-2026-04-30.pdf`.

**Authoritative input:** canonical moratorium-paper manuscript, original April cohort and source evidence.  **Classification:** historical PDF.  **Cutoff/version:** April 30 2026 edition.

**Evidence and limits:** PDF text inspected abstract: 222 communities in 30 states, 348 analyzed texts and 59%/77% clause claims. These are dated historical paper claims, not present inventory counts; abstract arithmetic or all 116 pages not independently checked. Landing labels paper historical and unsynchronized. Mirror not inspected.

**Reviewer role:** paper author and legal/methods reviewers.  **Completion:** historical abstract inspected; manuscript/mirror and entire PDF unverified.

**Validation:** `pdfinfo paper/moratorium-nation-2026-04-30.pdf && pdftotext paper/moratorium-nation-2026-04-30.pdf - | head -80`

**Next action:** Keep explicit historical edition label; compare mirror hashes, review body and tables, then either rebuild revised paper from pinned inputs or preserve dated edition.

### external-consumers-and-deployment

**Paths:** `work/audit/release-surfaces-2026-11-06.md`.

**Authoritative input:** sibling repositories and actual remote deployments.  **Classification:** external manual/generated/historical.  **Cutoff/version:** various corpus cutoffs and edition dates.

**Evidence and limits:** Plan 9.2 also names moratorium-paper, datacenter-paper-2026, integration, Server Country, Fight a Data Center, book and author sites. Prior catalogue is an inventory, not acceptance. These external checkouts and live sites were not inspected in this audit. TODO records partial delivery and separate outstanding consumer/deployment work.

**Reviewer role:** consumer owners and release manager.  **Completion:** outside core direct inspection; explicitly unverified.

**Validation:** `rg -n "sibling|hosted|deployment|consumer" TODO.md`

**Next action:** Audit each sibling and hosted release separately, pin distinct source cutoffs, review substantive claims and document historical/blocked dispositions.

## Scope and reproducibility

No live remote, deployment, all-page browser, complete figure visual inspection, full case adjudication, or exhaustive sibling audit was performed. A passing generator check does not verify claims in manually maintained spans. Recommended commands are read-only checks or inspection commands; run write-producing builds only in an isolated copy. The JSON register contains the same paths, observations and dispositions.

End-of-audit `git status --short` observation:

```
(clean)
```
