#!/usr/bin/env python3
"""Generate site/timeline.svg — monthly stacked bar chart of moratorium adoptions.

X axis: month (2018-01 through 2026-04)
Y axis: number of moratoria adopted that month
Stacking: by primary sector (data_center, cryptocurrency_mining, battery_storage,
          solar, wind, general)
Overlay: cumulative-total dashed line.

Reads `data/moratorium_inventory.csv` (using date_enacted_iso and sectors[0]).
Writes a single self-contained SVG (no JS, no external fonts) that embeds
in the GitHub Pages site or anywhere else.

Run:
    python3 scripts/make_timeline.py
"""

from __future__ import annotations

import csv
import json
from collections import OrderedDict, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
OUT = REPO / "site" / "timeline.svg"


SECTOR_ORDER = [
    "data_center",
    "cryptocurrency_mining",
    "battery_storage",
    "solar",
    "wind",
    "general",
]
SECTOR_COLORS = {
    "data_center":           "#1f6feb",   # blue (primary brand)
    "cryptocurrency_mining": "#7d3cb5",   # purple
    "battery_storage":       "#cb2431",   # red
    "solar":                 "#d4a017",   # amber
    "wind":                  "#2d8f4f",   # green
    "general":               "#6a737d",   # gray
}
SECTOR_LABELS = {
    "data_center":           "Data center",
    "cryptocurrency_mining": "Cryptocurrency mining",
    "battery_storage":       "Battery storage",
    "solar":                 "Solar",
    "wind":                  "Wind",
    "general":               "General zoning",
}


def month_iter(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            m = 1
            y += 1


def collect() -> tuple[list[str], dict[str, dict[str, int]], list[int]]:
    monthly: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with open(INV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            iso = (r.get("date_enacted_iso") or "")[:7]
            if len(iso) != 7 or iso[4] != "-":
                continue
            try:
                sectors = json.loads(r.get("sectors") or "[]")
            except json.JSONDecodeError:
                sectors = []
            primary = sectors[0] if sectors else "general"
            if primary not in SECTOR_ORDER:
                primary = "general"
            monthly[iso][primary] += 1

    if not monthly:
        return [], {}, []

    months = list(month_iter(date(2018, 1, 1), date(2026, 4, 1)))
    cumulative: list[int] = []
    running = 0
    for m in months:
        running += sum(monthly.get(m, {}).values())
        cumulative.append(running)
    return months, monthly, cumulative


def main():
    months, monthly, cumulative = collect()
    if not months:
        raise SystemExit("No dated rows found.")

    # Layout
    W, H = 1100, 420
    pad_l, pad_r, pad_t, pad_b = 60, 24, 100, 90
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    bar_w = plot_w / len(months)

    # Y scale (single axis: monthly count). Round up to next multiple of 10
    # AND add headroom so the tallest bar isn't flush with the top axis.
    max_month = max(sum(monthly.get(m, {}).values()) for m in months)
    y_max = ((max_month + 9) // 10 + 1) * 10
    y_max = max(y_max, 10)
    y_step = 10 if y_max <= 50 else 20

    cum_max = cumulative[-1]

    def x_at(i: int) -> float:
        return pad_l + i * bar_w

    def y_at(value: float) -> float:
        return pad_t + plot_h - (value / y_max) * plot_h

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="100%" height="auto" font-family="ui-sans-serif, system-ui, '
        f'-apple-system, Helvetica, Arial, sans-serif" font-size="12" '
        f'role="img" aria-label="Monthly moratorium adoptions, 2018 through April 2026">'
    )
    # Background
    parts.append(f'<rect width="{W}" height="{H}" fill="white"/>')

    # Title
    parts.append(
        f'<text x="{pad_l}" y="28" font-size="18" font-weight="600" fill="#0f1419">'
        f'Moratorium adoptions per month, 2018–April 2026</text>'
    )
    parts.append(
        f'<text x="{pad_l}" y="48" font-size="13" fill="#4a5460">'
        f'Each bar = one calendar month. Height = moratoria adopted that month. Color = primary sector.'
        f'</text>'
    )
    parts.append(
        f'<text x="{pad_l}" y="68" font-size="13" fill="#4a5460">'
        f'{cum_max} adoptions across {sum(1 for m in months if monthly.get(m))} months with at least one adoption.'
        f'</text>'
    )

    # Y gridlines + labels (left axis = monthly)
    parts.append(f'<g stroke="#e5e7eb" stroke-width="1">')
    for v in range(0, y_max + 1, y_step):
        y = y_at(v)
        parts.append(f'<line x1="{pad_l}" x2="{W - pad_r}" y1="{y:.1f}" y2="{y:.1f}"/>')
    parts.append('</g>')
    parts.append(f'<g fill="#4a5460" text-anchor="end">')
    for v in range(0, y_max + 1, y_step):
        y = y_at(v)
        parts.append(f'<text x="{pad_l - 6}" y="{y + 4:.1f}">{v}</text>')
    parts.append('</g>')
    parts.append(
        f'<text x="{pad_l - 44}" y="{pad_t + plot_h / 2:.1f}" '
        f'fill="#4a5460" text-anchor="middle" '
        f'transform="rotate(-90 {pad_l - 44} {pad_t + plot_h / 2:.1f})">'
        f'Moratoria adopted</text>'
    )

    # Stacked bars
    parts.append('<g>')
    for i, m in enumerate(months):
        cells = monthly.get(m, {})
        if not cells:
            continue
        x = x_at(i)
        y_acc = pad_t + plot_h
        for sector in SECTOR_ORDER:
            count = cells.get(sector, 0)
            if not count:
                continue
            h = (count / y_max) * plot_h
            y_acc -= h
            parts.append(
                f'<rect x="{x:.2f}" y="{y_acc:.2f}" width="{bar_w - 0.5:.2f}" '
                f'height="{h:.2f}" fill="{SECTOR_COLORS[sector]}">'
                f'<title>{m}: {count} {sector.replace("_"," ")}</title></rect>'
            )
    parts.append('</g>')

    # X-axis labels (year ticks)
    parts.append(f'<g fill="#4a5460" text-anchor="middle">')
    seen_years = set()
    for i, m in enumerate(months):
        year = m[:4]
        if year in seen_years:
            continue
        seen_years.add(year)
        # tick at January position
        x = x_at(i) + bar_w / 2
        parts.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{pad_t + plot_h:.1f}" y2="{pad_t + plot_h + 5:.1f}" stroke="#4a5460"/>')
        parts.append(f'<text x="{x:.2f}" y="{pad_t + plot_h + 20:.1f}">{year}</text>')
    parts.append('</g>')

    # Bottom axis line
    parts.append(
        f'<line x1="{pad_l}" x2="{W - pad_r}" y1="{pad_t + plot_h:.1f}" '
        f'y2="{pad_t + plot_h:.1f}" stroke="#4a5460"/>'
    )

    # Legend (bottom)
    parts.append('<g font-size="12">')
    legend_y = H - 28
    legend_x = pad_l
    for sector in SECTOR_ORDER:
        # Skip sectors that never appear
        total = sum(monthly[m].get(sector, 0) for m in months)
        if not total:
            continue
        parts.append(
            f'<rect x="{legend_x}" y="{legend_y - 10}" width="14" height="14" '
            f'fill="{SECTOR_COLORS[sector]}"/>'
        )
        label = f"{SECTOR_LABELS[sector]} ({total})"
        parts.append(
            f'<text x="{legend_x + 20}" y="{legend_y + 2}" fill="#0f1419">{label}</text>'
        )
        legend_x += 20 + 7 * len(label) + 24
    parts.append('</g>')

    parts.append('</svg>')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"  monthly max = {max_month}; cumulative = {cum_max} across {len(months)} months")


if __name__ == "__main__":
    main()
