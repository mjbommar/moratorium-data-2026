"""Recorded sector inputs, independent of optional plotting libraries."""
import json
from collections import defaultdict


def recorded_sector_inputs(rows):
    """Count each recorded sector once per row; prose never implies membership."""
    labels = {"data_center": "Data Center", "cryptocurrency_mining": "Crypto",
              "battery_storage": "BESS", "solar": "Solar", "wind": "Wind", "general": "Other"}
    counts = {}
    grouped = defaultdict(dict)
    for row in rows:
        values = json.loads(row["sectors"])
        if not isinstance(values, list) or any(not isinstance(v, str) or v not in labels for v in values):
            raise ValueError("Invalid recorded sector array")
        for sector in {labels[v] for v in values} or {"Unknown"}:
            key = (row["state_abbrev"], sector)
            counts[key] = counts.get(key, 0) + 1
    for (state, sector), count in sorted(counts.items()):
        grouped[state][sector] = count
    dominant = {}
    for state, sectors in grouped.items():
        peak = max(sectors.values())
        winners = [sector for sector, count in sectors.items() if count == peak]
        dominant[state] = winners[0] if len(winners) == 1 else "Mixed"
    return counts, dominant
