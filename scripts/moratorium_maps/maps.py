"""All map implementations for the moratorium paper.

Each function generates one figure and saves it to latex/figures/.
Run as: uv run python -m moratorium_maps.maps [map_name|all]
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import seaborn as sns

from .basemap import BaseUSMap, PALETTE, HATCH, FIGURES_DIR, STYLE
from .dates import recorded_month
from .data import (
    moratorium_counts_by_state,
    AUTHORITY_TYPE,
    HOME_RULE_TYPE,
    PREEMPTION_TYPE,
    STATUTORY_DURATION_DAYS,
    ABBREV_TO_NAME,
    load_moratorium_inventory,
)


# ============================================================================
# Map 1: Moratorium Count Choropleth
# ============================================================================

def map_moratorium_counts():
    """Choropleth of moratorium instrument count per state."""
    print("Map 1: Moratorium Count Choropleth")
    counts = moratorium_counts_by_state()
    values = dict(zip(counts["state_abbrev"], counts["count"]))

    # Pick a vmax that always covers the actual maximum, rounded up to the
    # next multiple of 5. Avoids clipping when leading states (e.g. Michigan)
    # cross 30 between refreshes.
    actual_max = max(values.values()) if values else 0
    vmax = max(30, ((actual_max // 5) + 1) * 5)

    m = BaseUSMap(title="Recorded Moratorium Rows by State")
    fig, ax = m.choropleth(
        values,
        cmap=PALETTE["sequential"],
        vmin=0,
        vmax=vmax,
        legend_label="Number of Records",
    )
    m.save("map-moratorium-counts")
    m.close()


# ============================================================================
# Map 2: Legal Authority Classification
# ============================================================================

def map_legal_authority():
    """Categorical map of moratorium legal authority type per state."""
    print("Map 2: Legal Authority Classification")

    color_map = {
        "Express": PALETTE["express"],
        "Implied": PALETTE["implied"],
        "Procedural": PALETTE["procedural"],
        "Restricted": PALETTE["restricted"],
        "Prohibited": PALETTE["prohibited"],
    }
    hatch_map = {
        "Express": HATCH["express"],
        "Implied": HATCH["implied"],
        "Procedural": HATCH["procedural"],
        "Restricted": HATCH["restricted"],
        "Prohibited": HATCH["prohibited"],
    }

    m = BaseUSMap(title="Moratorium Legal Authority by State")
    fig, ax = m.categorical(
        AUTHORITY_TYPE,
        color_map,
        hatch_map=hatch_map,
        legend_title="Authority Type",
    )
    m.save("map-legal-authority")
    m.close()


# ============================================================================
# Map 3: Dillon's Rule vs. Home Rule
# ============================================================================

def map_home_rule():
    """Categorical map of home rule vs. Dillon's Rule."""
    print("Map 3: Home Rule vs. Dillon's Rule")

    color_map = {
        "Home Rule": PALETTE["home_rule"],
        "Hybrid": PALETTE["hybrid"],
        "Dillon": PALETTE["dillon"],
    }
    hatch_map = {
        "Home Rule": HATCH["home_rule"],
        "Hybrid": HATCH["hybrid"],
        "Dillon": HATCH["dillon"],
    }

    m = BaseUSMap(title="Home Rule vs. Dillon's Rule")
    fig, ax = m.categorical(
        HOME_RULE_TYPE,
        color_map,
        hatch_map=hatch_map,
        legend_title="Structural Rule",
    )
    m.save("map-home-rule")
    m.close()



# ============================================================================
# Map 5: Sector Composition by State
# ============================================================================

def recorded_sector_inputs(inv):
    """Count recorded sector arrays; prose and missing values never imply data centers."""
    labels = {"data_center": "Data Center", "cryptocurrency_mining": "Crypto",
              "battery_storage": "BESS", "solar": "Solar", "wind": "Wind", "general": "Other"}
    counts = {}
    for _, row in inv.iterrows():
        values = json.loads(row["sectors"])
        if not isinstance(values, list) or any(not isinstance(v, str) or v not in labels for v in values):
            raise ValueError("Invalid recorded sector array")
        for sector in {labels[v] for v in values} or {"Unknown"}:
            key = (row["state_abbrev"], sector)
            counts[key] = counts.get(key, 0) + 1
    frame = pd.DataFrame([{"state_abbrev": state, "sector": sector, "count": count}
                          for (state, sector), count in sorted(counts.items())],
                         columns=["state_abbrev", "sector", "count"])
    dominant = {}
    for state, group in frame.groupby("state_abbrev"):
        winners = group[group["count"] == group["count"].max()]["sector"].tolist()
        dominant[state] = winners[0] if len(winners) == 1 else "Mixed"
    return frame, dominant


def map_sector_composition():
    """Map showing sector breakdown of moratoria per state."""
    print("Map 5: Sector Composition")

    inv = load_moratorium_inventory()

    sector_counts, dominant_map = recorded_sector_inputs(inv)

    sector_colors = {
        "Data Center": PALETTE["data_center"],
        "Crypto": PALETTE["crypto"],
        "BESS": PALETTE["bess"],
        "Solar": PALETTE["solar"],
        "Wind": PALETTE["wind"],
        "Other": "#eeeeee", "Mixed": "#aaaaaa", "Unknown": "#ffffff",
    }
    sector_hatches = {
        "Data Center": HATCH["data_center"],
        "Crypto": HATCH["crypto"],
        "BESS": HATCH["bess"],
        "Solar": HATCH["solar"],
        "Wind": HATCH["wind"],
        "Other": "..", "Mixed": "++", "Unknown": "oo",
    }

    m = BaseUSMap(title="Recorded Moratorium Rows by Sector")
    gdf = m._load_and_project()
    fig, ax = m._setup_figure(gdf)

    # Draw base (no-data states)
    gdf.plot(ax=ax, color=PALETTE["no_data"], edgecolor=PALETTE["border"], linewidth=0.4)

    # For states with moratoria, color by dominant sector with hatching
    gdf["dominant"] = gdf["STUSPS"].map(dominant_map)
    for sector, color in sector_colors.items():
        subset = gdf[gdf["dominant"] == sector]
        if not subset.empty:
            hatch = sector_hatches.get(sector, "")
            subset.plot(ax=ax, color=color, edgecolor=PALETTE["border"], linewidth=0.4, hatch=hatch)

    # Legend
    patches = [
        mpatches.Patch(facecolor=color, edgecolor=PALETTE["border"],
                       hatch=sector_hatches.get(sector, ""), label=sector)
        for sector, color in sector_colors.items()
    ]
    patches.append(mpatches.Patch(facecolor=PALETTE["no_data"], edgecolor=PALETTE["border"], label="No recorded rows"))
    ax.legend(
        handles=patches, loc="lower right",
        title="Recorded sector (ties: Mixed)", title_fontsize=9, fontsize=8,
        frameon=True, fancybox=False, edgecolor="#cccccc", framealpha=0.95,
    )

    m._draw_inset_separators(ax, gdf)
    m._fig, m._ax, m._gdf = fig, ax, gdf
    fig.text(0.5, 0.015, "Multi-sector rows contribute to each recorded sector; general pauses are Other.",
             ha="center", fontsize=7)
    m.save("map-sector-composition")
    m.close()


# ============================================================================
# Map 6: Statutory Duration Limits
# ============================================================================

def map_statutory_duration():
    """Choropleth of maximum statutory duration for express-statute states."""
    print("Map 6: Statutory Duration Limits")

    # Convert days to months for readability
    duration_months = {k: v / 30.44 for k, v in STATUTORY_DURATION_DAYS.items()}

    m = BaseUSMap(title="Maximum Statutory Moratorium Duration")
    fig, ax = m.choropleth(
        duration_months,
        cmap=PALETTE["sequential"],
        vmin=0,
        vmax=24,
        legend_label="Maximum Duration (months)",
        missing_color=PALETTE["no_data"],
    )
    m.save("map-statutory-duration")
    m.close()


# ============================================================================
# Map 7: Timeline Heatmap (state × month grid)
# ============================================================================

def map_timeline_heatmap():
    """State × month heatmap of moratorium enactment timing."""
    print("Map 7: Timeline Heatmap")

    inv = load_moratorium_inventory()

    # Legacy display strings contain ranges and notes that are not month dates.
    inv["year_month"] = inv.apply(recorded_month, axis=1)
    dated = inv.dropna(subset=["year_month"])

    # Count by state × month
    pivot = dated.groupby(["state_abbrev", "year_month"]).size().reset_index(name="count")
    matrix = pivot.pivot(index="state_abbrev", columns="year_month", values="count").fillna(0)

    # Only keep states with at least 1 moratorium
    matrix = matrix.loc[matrix.sum(axis=1) > 0]
    # Sort by total count
    matrix = matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index]

    # Sort columns chronologically
    matrix = matrix[sorted(matrix.columns)]

    plt.rcParams.update(STYLE)
    fig, ax = plt.subplots(figsize=(12, max(4, len(matrix) * 0.35 + 1)))

    # Custom colormap: white for zero, then grayscale ramp for 1+
    from matplotlib.colors import LinearSegmentedColormap
    heatmap_cmap = LinearSegmentedColormap.from_list(
        "white_greys", ["#ffffff", "#d9d9d9", "#969696", "#525252", "#252525"]
    )

    sns.heatmap(
        matrix.astype(int),
        ax=ax,
        cmap=heatmap_cmap,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Records with Reported Month", "shrink": 0.6},
        annot=True,
        fmt="g",
        annot_kws={"fontsize": 7},
        vmin=0,
    )

    ax.set_title(
        "Recorded Moratorium Dates by State\n"
        f"{len(dated)} dated rows; {len(inv) - len(dated)} without a usable month",
        fontweight="bold", pad=12,
    )
    ax.set_xlabel("Recorded month (may be unverified or scheduled)")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.tick_params(axis="y", labelsize=8)

    fig.tight_layout()

    for fmt in ("pdf", "svg", "png"):
        outdir = FIGURES_DIR / fmt
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / f"map-timeline-heatmap.{fmt}"
        fig.savefig(path, format=fmt, bbox_inches="tight", pad_inches=0.1)
        print(f"  Saved: {path.relative_to(FIGURES_DIR.parent)}")

    plt.close(fig)


# ============================================================================
# Map 8: Preemption Spectrum
# ============================================================================

def map_preemption():
    """Categorical map showing state preemption posture."""
    print("Map 8: Preemption Spectrum")

    # Classify all states
    preemption_full = {}
    for abbr in ABBREV_TO_NAME:
        preemption_full[abbr] = PREEMPTION_TYPE.get(abbr, "None")

    color_map = {
        "Full Preemption": PALETTE["full_preemption"],
        "Incentive-Linked": PALETTE["incentive_linked"],
        "Sector Restriction": PALETTE["sector_restriction"],
        "None": PALETTE["no_preemption"],
    }
    hatch_map = {
        "Full Preemption": HATCH["full_preemption"],
        "Incentive-Linked": HATCH["incentive_linked"],
        "Sector Restriction": HATCH["sector_restriction"],
        "None": HATCH["no_preemption"],
    }

    m = BaseUSMap(title="State Preemption of Local Moratorium Authority")
    fig, ax = m.categorical(
        preemption_full,
        color_map,
        hatch_map=hatch_map,
        legend_title="Preemption Type",
    )
    m.save("map-preemption")
    m.close()


# ============================================================================
# CLI entry point
# ============================================================================

MAP_REGISTRY = {
    "counts": map_moratorium_counts,
    "authority": map_legal_authority,
    "home-rule": map_home_rule,
    "sector": map_sector_composition,
    "duration": map_statutory_duration,
    "timeline": map_timeline_heatmap,
    "preemption": map_preemption,
}


def main():
    args = sys.argv[1:]
    if not args or "all" in args:
        print(f"Generating all {len(MAP_REGISTRY)} maps...")
        for name, func in MAP_REGISTRY.items():
            func()
            print()
    else:
        for name in args:
            if name in MAP_REGISTRY:
                MAP_REGISTRY[name]()
            else:
                print(f"Unknown map: {name}. Available: {', '.join(MAP_REGISTRY)}")
    print("Done.")


if __name__ == "__main__":
    main()
