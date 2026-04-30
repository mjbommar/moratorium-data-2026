"""Run all table generators, or a specific one by name.

Usage:
    python -m scripts.generate_tables           # regenerate all tables
    python -m scripts.generate_tables top_states temporal_distribution
"""

from __future__ import annotations

import importlib
import sys

# Order matters only in that some generators depend on the latest
# moratorium-analysis.json having been written by analyze_extractions.py.
GENERATORS = [
    "top_states",
    "temporal_distribution",
    "state_sector_counts",
    "inventory_clean",
    "findings_impact",
    "definitional_approaches",
    "sector_specific_clauses",
]


def main():
    targets = sys.argv[1:] or GENERATORS
    bad = [t for t in targets if t not in GENERATORS]
    if bad:
        print(f"Unknown generator(s): {', '.join(bad)}", file=sys.stderr)
        print(f"Available: {', '.join(GENERATORS)}", file=sys.stderr)
        sys.exit(2)
    for name in targets:
        mod = importlib.import_module(f"scripts.generate_tables.{name}")
        mod.main()


if __name__ == "__main__":
    main()
