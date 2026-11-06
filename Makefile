# Moratorium Data 2026 -- build and refresh targets.
#
# Legacy inventory artifacts are derived from two canonical CSVs:
#   data/moratorium_inventory.csv
#   data/state_legislation.csv
# Reviewed ballot tables use data/expanded and its immutable snapshot history.
# `make check` validates generated outputs and the expanded publication.
# `make validate` checks the legacy CSV contracts.
#
#   make install     install Python dependencies
#   make validate    check the CSVs against docs/codebook.md (exit 1 on error)
#   make all         regenerate every derived artifact, then validate
#   make apply       merge research decision files into the CSVs
#   make worklist    emit the research worklist and per-state packets
#   make check       verify generated artifacts are in sync (CI-friendly)

PYTHON ?= python3
TODAY  ?= $(shell date +%F)

.PHONY: all install validate check apply worklist data figures site clean help

help:
	@grep -E '^#   make' $(MAKEFILE_LIST) | sed 's/^#   /  /'

install:
	$(PYTHON) -m pip install pandas matplotlib seaborn geopandas shapely markdown pymdown-extensions jsonschema pillow

# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

validate:
	$(PYTHON) scripts/validate_dataset.py --today $(TODAY)

# Confirms generated artifacts match the CSVs. Use in CI: it fails if someone
# edited a CSV without regenerating, or edited a generated file by hand.
check: validate
	$(PYTHON) scripts/build_summary_stats.py --check
	$(PYTHON) scripts/build_geojson.py --check
	$(PYTHON) scripts/check_docs_numbers.py
	$(PYTHON) scripts/expanded_identity.py --registry data/identities/expanded.jsonl --check
	$(PYTHON) scripts/check_expanded_publication.py
	$(PYTHON) scripts/build_ballot_summary.py --check
	$(PYTHON) scripts/build_index.py --check
	$(PYTHON) scripts/classify_sources.py --check

# ---------------------------------------------------------------------------
# Refresh cycle
# ---------------------------------------------------------------------------

# Emit the set of rows needing research as of TODAY, then split into packets.
worklist:
	$(PYTHON) scripts/build_worklist.py --today $(TODAY) --pretty
	$(PYTHON) scripts/make_packets.py --worklist work/worklist-$(TODAY).json \
		--buckets expired_in_force,until_date_stale,calendar_end_unverified,stale_pending --tag status
	$(PYTHON) scripts/make_packets.py --worklist work/worklist-$(TODAY).json \
		--buckets verify_backlog,unverified_date --tag verify \
		--exclude-dir work/packets/status --max-items 12
	$(PYTHON) scripts/make_legislation_packets.py --as-of $(TODAY)

# Merge research answers, then normalize. Each step is idempotent, so this is
# safe to re-run as answers land state by state.
apply:
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/status
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/verify
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/chronology
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/gaps
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/decisions
	$(PYTHON) scripts/apply_research.py --answers-dir work/answers/full
	$(PYTHON) scripts/apply_legislation.py --answers-dir work/answers/legislation
	$(PYTHON) scripts/normalize_vocab.py
	$(PYTHON) scripts/reconcile_durations.py
	$(PYTHON) scripts/geocode_inventory.py
	$(PYTHON) scripts/apply_geo_overrides.py
	$(MAKE) validate

# ---------------------------------------------------------------------------
# Generated artifacts
# ---------------------------------------------------------------------------

data:
	$(PYTHON) scripts/build_summary_stats.py
	$(PYTHON) scripts/build_geojson.py
	$(PYTHON) scripts/build_ballot_summary.py

figures: data/geo/cb_2023_us_state_5m/cb_2023_us_state_5m.shp
	$(PYTHON) -m scripts.generate_tables
	PYTHONPATH=scripts $(PYTHON) -m moratorium_maps all
	$(PYTHON) scripts/make_timeline.py

data/geo/cb_2023_us_state_5m/cb_2023_us_state_5m.shp:
	$(PYTHON) scripts/fetch_basemap.py

site:
	$(PYTHON) scripts/build_index.py
	$(PYTHON) scripts/update_state_counts.py --as-of $(TODAY)
	$(PYTHON) scripts/build_site.py

all: data figures site validate
	@echo
	@echo "All artifacts regenerated and validated."

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
