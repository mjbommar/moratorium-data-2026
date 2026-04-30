"""Shared helpers for the LaTeX table generators.

The generators in this package read `research/analysis/moratorium_inventory.csv`
and `research/analysis/moratorium-analysis.json` and emit the corresponding
hand-rolled tables in `latex/tables/`. They replace what was previously a
manual edit pass after every data refresh.

Sector classification is intentionally identical to the logic used by
`src/moratorium_maps/maps.py::map_sector_composition` so that the maps and
tables agree on which row counts as which sector.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ANALYSIS_DIR = PROJECT_ROOT / "research" / "analysis"
TABLES_DIR = PROJECT_ROOT / "latex" / "tables"
INVENTORY_CSV = ANALYSIS_DIR / "moratorium_inventory.csv"
ANALYSIS_JSON = ANALYSIS_DIR / "moratorium-analysis.json"
SUMMARY_JSON = ANALYSIS_DIR / "summary_stats.json"


@dataclass(frozen=True)
class InventoryRow:
    state: str
    state_abbrev: str
    jurisdiction: str
    jurisdiction_type: str
    date_enacted: str
    duration: str
    legal_basis: str
    trigger: str
    current_status: str
    affected_projects: str
    outcome: str
    activity_level: str

    @classmethod
    def from_csv_dict(cls, d: dict) -> "InventoryRow":
        return cls(
            state=d.get("state", "").strip(),
            state_abbrev=d.get("state_abbrev", "").strip(),
            jurisdiction=d.get("jurisdiction", "").strip(),
            jurisdiction_type=d.get("jurisdiction_type", "").strip(),
            date_enacted=d.get("date_enacted", "").strip(),
            duration=d.get("duration", "").strip(),
            legal_basis=d.get("legal_basis", "").strip(),
            trigger=d.get("trigger", "").strip(),
            current_status=d.get("current_status", "").strip(),
            affected_projects=d.get("affected_projects", "").strip(),
            outcome=d.get("outcome", "").strip(),
            activity_level=d.get("activity_level", "").strip(),
        )


def load_inventory() -> list[InventoryRow]:
    """Load the moratorium inventory CSV."""
    with INVENTORY_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        return [InventoryRow.from_csv_dict(row) for row in reader]


def load_analysis() -> dict:
    """Load the moratorium-analysis.json summary."""
    return json.loads(ANALYSIS_JSON.read_text())


def load_summary() -> dict:
    """Load the summary_stats.json digest."""
    return json.loads(SUMMARY_JSON.read_text())


# ---------------------------------------------------------------------------
# Sector classification — must match maps.py::map_sector_composition
# ---------------------------------------------------------------------------

SECTORS = ["Data Center", "Crypto", "BESS", "Solar", "Wind", "Other"]


def classify_sector(row: InventoryRow) -> str:
    """Classify a row's primary sector based on the same heuristics used by
    the sector-composition map."""
    text = (
        f"{row.trigger} {row.legal_basis} {row.jurisdiction} {row.outcome} "
        f"{row.current_status}"
    ).lower()
    if "crypto" in text or "digital asset" in text or "mining" in text:
        return "Crypto"
    if "battery" in text or "bess" in text or "energy storage" in text:
        return "BESS"
    if "solar" in text:
        return "Solar"
    if "wind" in text:
        return "Wind"
    if "data center" in text or "data centre" in text:
        return "Data Center"
    if "industrial" in text or "general" in text:
        return "Other"
    return "Data Center"


def classify_all_sectors(row: InventoryRow) -> list[str]:
    """Return every sector mentioned in the row (multi-sector instruments)."""
    text = (
        f"{row.trigger} {row.legal_basis} {row.jurisdiction} {row.outcome} "
        f"{row.current_status}"
    ).lower()
    found = []
    if "data center" in text or "data centre" in text:
        found.append("Data Center")
    if "crypto" in text or "digital asset" in text or "mining" in text:
        found.append("Crypto")
    if "battery" in text or "bess" in text or "energy storage" in text:
        found.append("BESS")
    if "solar" in text:
        found.append("Solar")
    if "wind" in text:
        found.append("Wind")
    return found or ["Data Center"]


# ---------------------------------------------------------------------------
# Date parsing — many CSV rows have messy date strings
# ---------------------------------------------------------------------------

YEAR_PATTERN = re.compile(r"\b(20[12][0-9])\b")
YEAR_MONTH_PATTERN = re.compile(r"(20[12][0-9])-(\d{2})")


def parse_year(date_str: str) -> int | None:
    """Extract a 4-digit year from a date_enacted string."""
    if not date_str:
        return None
    m = YEAR_PATTERN.search(date_str)
    if m:
        return int(m.group(1))
    return None


def parse_year_month(date_str: str) -> str | None:
    """Extract YYYY-MM from a date_enacted string."""
    if not date_str:
        return None
    m = YEAR_MONTH_PATTERN.search(date_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


# ---------------------------------------------------------------------------
# Cleaning rules — produce the "cleaned" inventory subset used in the paper
# ---------------------------------------------------------------------------

NON_GOVERNMENTAL_HINTS = ("federal", "tva", "epa")


def is_governmental(row: InventoryRow) -> bool:
    """Filter out non-governmental rows (federal, advocacy groups, etc.)."""
    j = row.jurisdiction.lower()
    if any(h in j for h in NON_GOVERNMENTAL_HINTS):
        return False
    return True


def cleaned_inventory(rows: list[InventoryRow]) -> list[InventoryRow]:
    """Apply the cleaning rules used to derive the n=116 cleaned inventory:
    drop non-governmental rows, sort by state then jurisdiction.
    Extension dedup is left to per-row inspection in update_inventory.py."""
    kept = [r for r in rows if is_governmental(r)]
    kept.sort(key=lambda r: (r.state_abbrev, r.jurisdiction.lower()))
    return kept


# ---------------------------------------------------------------------------
# LaTeX escaping
# ---------------------------------------------------------------------------

_ESCAPE = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]


def latex_escape(text: str) -> str:
    if not text:
        return ""
    out = text
    for src, dst in _ESCAPE:
        out = out.replace(src, dst)
    return out


# ---------------------------------------------------------------------------
# Duration string normalization for the inventory table
# ---------------------------------------------------------------------------

DURATION_DAYS = re.compile(r"(\d+)\s*days?", re.I)
DURATION_MONTHS = re.compile(r"(\d+)\s*month", re.I)
DURATION_YEARS = re.compile(r"(\d+)\s*year|(\d+)\s*yr", re.I)


def normalize_duration(duration: str) -> str:
    """Compact representation for the inventory longtable."""
    if not duration:
        return "—"
    s = duration.strip()
    low = s.lower()
    if "indef" in low or "permanent" in low:
        return "Indef."
    if "propos" in low or "pending" in low:
        return "Proposed"
    m = DURATION_DAYS.search(s)
    if m:
        return f"{m.group(1)}d"
    m = DURATION_YEARS.search(s)
    if m:
        return f"{m.group(1) or m.group(2)}yr"
    m = DURATION_MONTHS.search(s)
    if m:
        return f"{m.group(1)}mo"
    # Fall through: take a short prefix
    return s.split(";")[0].split(",")[0].strip()[:14] or "—"
