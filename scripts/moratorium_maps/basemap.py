"""Reusable US state map framework for the moratorium paper.

Provides a BaseUSMap class that handles:
- Loading and projecting state geometries (Albers Equal Area)
- Inset positioning for Alaska and Hawaii
- Consistent styling (fonts, borders, background)
- Choropleth and categorical fills
- Proportional symbol overlays
- Legend generation
- PDF and SVG output
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from shapely.affinity import translate, scale

from .data import load_states_geo, ABBREV_TO_NAME

# --- Constants ---

# Output directory for figures
FIGURES_DIR = Path(__file__).resolve().parent.parent.parent / "latex" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Albers Equal Area Conic projection for CONUS
ALBERS_CRS = "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +datum=NAD83"

# Paper-quality style settings
STYLE = {
    "font.family": "serif",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.linewidth": 0.5,
    "hatch.linewidth": 0.6,
    "hatch.color": "#252525",
}

# Grayscale palette — print-safe, distinguished by fill shade + hatch pattern
PALETTE = {
    # Sequential colormap for choropleths and heatmap
    "sequential": "Greys",
    # Authority types (lighter = more authority, darker = restricted)
    "express": "#ffffff",      # white — explicit statutory authority
    "implied": "#d9d9d9",      # light gray — inferred from general powers
    "procedural": "#bdbdbd",   # medium-light gray — conditional
    "restricted": "#969696",   # medium gray — limited by state law
    "prohibited": "#636363",   # dark gray — banned by state law
    # Home rule / Dillon's Rule
    "home_rule": "#e8e8e8",    # light gray — broad local power
    "hybrid": "#bdbdbd",       # medium gray — mixed
    "dillon": "#707070",       # dark gray — constrained local power
    # Preemption (darker = more state preemption)
    "full_preemption": "#636363",    # dark gray
    "incentive_linked": "#969696",   # medium gray
    "sector_restriction": "#bdbdbd", # medium-light gray
    "no_preemption": "#e8e8e8",      # light gray wash
    # Sector (distinct grays + hatching for differentiation)
    "data_center": "#d9d9d9",  # light gray
    "crypto": "#969696",       # medium gray
    "bess": "#bdbdbd",         # medium-light gray
    "solar": "#e8e8e8",        # very light gray
    "wind": "#707070",         # dark-medium gray
    # General
    "border": "#404040",       # dark gray borders
    "background": "#fafafa",
    "no_data": "#f5f5f5",      # very light gray
    "text": "#252525",
    "dot": "#252525",
}

# Hatch patterns — each category has a unique fill pattern for B&W print
HATCH = {
    # Authority types
    "express": "///",
    "implied": "",
    "procedural": "...",
    "restricted": "xx",
    "prohibited": "\\\\\\",
    # Home rule / Dillon's Rule
    "home_rule": "///",
    "hybrid": "...",
    "dillon": "\\\\\\",
    # Preemption
    "full_preemption": "\\\\\\",
    "incentive_linked": "xx",
    "sector_restriction": "...",
    "no_preemption": "",
    # Sector
    "data_center": "///",
    "crypto": "\\\\\\",
    "bess": "||",
    "solar": "...",
    "wind": "xx",
}


def _filter_alaska(geom):
    """Drop far-western Aleutians (past ~172°W) that distort the inset."""
    from shapely.geometry import MultiPolygon
    if geom.geom_type == "MultiPolygon":
        kept = [p for p in geom.geoms if p.centroid.x > -4800000]
        return MultiPolygon(kept) if len(kept) > 1 else kept[0]
    return geom


def _transform_alaska(geom):
    """Scale down and translate Alaska to inset position (below SW CONUS)."""
    geom = _filter_alaska(geom)
    geom = scale(geom, xfact=0.35, yfact=0.35, origin=(0, 0))
    geom = translate(geom, xoff=-515000, yoff=-3014000)
    return geom


def _filter_hawaii(geom):
    """Keep only main Hawaiian islands, drop Northwestern Hawaiian Islands."""
    from shapely.geometry import MultiPolygon
    if geom.geom_type == "MultiPolygon":
        kept = [p for p in geom.geoms if p.centroid.y < 600000]
        return MultiPolygon(kept) if len(kept) > 1 else kept[0]
    return geom


def _transform_hawaii(geom):
    """Translate Hawaii main islands to inset position (below S-central CONUS)."""
    geom = _filter_hawaii(geom)
    geom = translate(geom, xoff=5675000, yoff=-1897000)
    return geom


class BaseUSMap:
    """Base class for creating US state maps with Alaska/Hawaii insets."""

    def __init__(
        self,
        *,
        figsize: tuple[float, float] = (10, 7),
        title: str = "",
        include_dc: bool = True,
    ):
        self.figsize = figsize
        self.title = title
        self.include_dc = include_dc
        self._gdf: gpd.GeoDataFrame | None = None
        self._fig: Figure | None = None
        self._ax: Axes | None = None

    def _load_and_project(self) -> gpd.GeoDataFrame:
        """Load state geometries, project to Albers, transform AK/HI."""
        gdf = load_states_geo()
        if not self.include_dc:
            gdf = gdf[gdf["STUSPS"] != "DC"]

        # Project to Albers
        gdf = gdf.to_crs(ALBERS_CRS)

        # Transform Alaska and Hawaii for inset display
        ak_mask = gdf["STUSPS"] == "AK"
        hi_mask = gdf["STUSPS"] == "HI"

        gdf.loc[ak_mask, "geometry"] = gdf.loc[ak_mask, "geometry"].apply(
            _transform_alaska
        )
        gdf.loc[hi_mask, "geometry"] = gdf.loc[hi_mask, "geometry"].apply(
            _transform_hawaii
        )

        return gdf

    def _setup_figure(self, gdf: gpd.GeoDataFrame | None = None) -> tuple[Figure, Axes]:
        """Create figure and axes with paper styling."""
        plt.rcParams.update(STYLE)
        fig, ax = plt.subplots(1, 1, figsize=self.figsize)
        ax.set_aspect("equal")
        ax.axis("off")
        if self.title:
            ax.set_title(self.title, fontweight="bold", pad=12)
        # Set tight axis limits if we have geometry data
        if gdf is not None:
            bounds = gdf.total_bounds  # xmin, ymin, xmax, ymax
            pad = 50000
            ax.set_xlim(bounds[0] - pad, bounds[2] + pad)
            ax.set_ylim(bounds[1] - pad, bounds[3] + pad)
        return fig, ax

    def _draw_borders(self, ax: Axes, gdf: gpd.GeoDataFrame, **kwargs):
        """Draw state borders."""
        defaults = {
            "edgecolor": PALETTE["border"],
            "linewidth": 0.4,
            "facecolor": "none",
        }
        defaults.update(kwargs)
        gdf.plot(ax=ax, **defaults)

    def _draw_inset_separators(self, ax: Axes, gdf: gpd.GeoDataFrame):
        """Draw light separator lines around Alaska and Hawaii insets."""
        from matplotlib.patches import FancyBboxPatch
        for state in ("AK", "HI"):
            subset = gdf[gdf["STUSPS"] == state]
            if subset.empty:
                continue
            bounds = subset.total_bounds  # xmin, ymin, xmax, ymax
            pad = 40000
            rect = mpatches.FancyBboxPatch(
                (bounds[0] - pad, bounds[1] - pad),
                (bounds[2] - bounds[0]) + 2 * pad,
                (bounds[3] - bounds[1]) + 2 * pad,
                boxstyle="round,pad=0",
                linewidth=0.4,
                edgecolor="#cccccc",
                facecolor="none",
                zorder=0,
            )
            ax.add_patch(rect)

    def _add_state_labels(
        self,
        ax: Axes,
        gdf: gpd.GeoDataFrame,
        column: str | None = None,
        label_col: str = "STUSPS",
        fontsize: float = 5.5,
        skip_small: bool = True,
    ):
        """Add state abbreviation labels at centroids."""
        # States too small for internal labels
        SMALL_STATES = {"DC", "DE", "RI", "CT", "NJ", "NH", "VT", "MA", "MD"}

        for _, row in gdf.iterrows():
            abbrev = row["STUSPS"]
            if skip_small and abbrev in SMALL_STATES:
                continue
            centroid = row["geometry"].centroid
            label = row[label_col] if label_col != "value" else str(row.get(column, ""))
            ax.annotate(
                abbrev,
                xy=(centroid.x, centroid.y),
                ha="center",
                va="center",
                fontsize=fontsize,
                color=PALETTE["text"],
                fontweight="bold",
            )

    def _add_count_labels(
        self,
        ax: Axes,
        gdf: gpd.GeoDataFrame,
        count_col: str = "count",
        fontsize: float = 6,
        min_count: int = 1,
    ):
        """Add count labels at state centroids (only for states with count >= min_count)."""
        SMALL_STATES = {"DC", "DE", "RI", "CT", "NJ", "NH", "VT", "MA", "MD"}
        for _, row in gdf.iterrows():
            count = row.get(count_col, 0)
            if count < min_count:
                continue
            abbrev = row["STUSPS"]
            centroid = row["geometry"].centroid
            if abbrev in SMALL_STATES:
                continue
            ax.annotate(
                f"{row['STUSPS']}\n{int(count)}",
                xy=(centroid.x, centroid.y),
                ha="center",
                va="center",
                fontsize=fontsize,
                color="white" if count >= 5 else PALETTE["text"],
                fontweight="bold",
                linespacing=0.85,
            )

    def choropleth(
        self,
        values: dict[str, float],
        *,
        cmap: str = "YlOrRd",
        vmin: float | None = None,
        vmax: float | None = None,
        legend_label: str = "",
        missing_color: str | None = None,
    ) -> tuple[Figure, Axes]:
        """Draw a choropleth map colored by continuous values.

        Args:
            values: dict mapping state abbreviation -> numeric value
            cmap: matplotlib colormap name
            vmin, vmax: color scale limits
            legend_label: label for the colorbar
            missing_color: color for states with no data
            label_counts: if True, show counts on states
        """
        gdf = self._load_and_project()
        fig, ax = self._setup_figure(gdf)

        gdf["value"] = gdf["STUSPS"].map(values).fillna(0)

        if vmin is None:
            vmin = 0
        if vmax is None:
            vmax = gdf["value"].max()

        # Draw filled states
        gdf.plot(
            ax=ax,
            column="value",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            edgecolor=PALETTE["border"],
            linewidth=0.4,
            missing_kwds={"color": missing_color or PALETTE["no_data"]},
        )

        # Colorbar
        sm = plt.cm.ScalarMappable(
            cmap=cmap, norm=mcolors.Normalize(vmin=vmin, vmax=vmax)
        )
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax, shrink=0.5, aspect=20, pad=0.02)
        if legend_label:
            cbar.set_label(legend_label, fontsize=9)
        cbar.ax.tick_params(labelsize=8)

        self._draw_inset_separators(ax, gdf)

        self._fig, self._ax, self._gdf = fig, ax, gdf
        return fig, ax

    def categorical(
        self,
        categories: dict[str, str],
        color_map: dict[str, str],
        *,
        hatch_map: dict[str, str] | None = None,
        legend_title: str = "",
        label_states: bool = True,
    ) -> tuple[Figure, Axes]:
        """Draw a categorical map with discrete fills and hatch patterns.

        Args:
            categories: dict mapping state abbreviation -> category name
            color_map: dict mapping category name -> color
            hatch_map: dict mapping category name -> hatch pattern string
            legend_title: title for the legend
            label_states: whether to add state abbreviation labels
        """
        gdf = self._load_and_project()
        fig, ax = self._setup_figure(gdf)

        gdf["category"] = gdf["STUSPS"].map(categories).fillna("Unknown")

        # Draw each category with optional hatching
        for cat, color in color_map.items():
            subset = gdf[gdf["category"] == cat]
            if not subset.empty:
                hatch = (hatch_map or {}).get(cat, "")
                subset.plot(
                    ax=ax,
                    color=color,
                    edgecolor=PALETTE["border"],
                    linewidth=0.4,
                    hatch=hatch,
                )

        # Draw any "Unknown" states
        unknown = gdf[~gdf["category"].isin(color_map)]
        if not unknown.empty:
            unknown.plot(
                ax=ax,
                color=PALETTE["no_data"],
                edgecolor=PALETTE["border"],
                linewidth=0.4,
            )

        # Legend with hatch patterns
        patches = [
            mpatches.Patch(
                facecolor=color,
                edgecolor=PALETTE["border"],
                hatch=(hatch_map or {}).get(cat, ""),
                label=cat,
            )
            for cat, color in color_map.items()
        ]
        ax.legend(
            handles=patches,
            loc="lower right",
            title=legend_title,
            title_fontsize=9,
            fontsize=8,
            frameon=True,
            fancybox=False,
            edgecolor="#cccccc",
            framealpha=0.95,
        )

        self._draw_inset_separators(ax, gdf)

        self._fig, self._ax, self._gdf = fig, ax, gdf
        return fig, ax

    def overlay_dots(
        self,
        ax: Axes,
        gdf: gpd.GeoDataFrame,
        values: dict[str, float],
        *,
        scale_factor: float = 15.0,
        color: str = "#333333",
        alpha: float = 0.7,
        edgecolor: str = "white",
        min_value: float = 1,
    ):
        """Overlay proportional circles on an existing map.

        Args:
            ax: axes to draw on
            gdf: GeoDataFrame with state geometries
            values: dict mapping state abbreviation -> numeric value
            scale_factor: multiplier for circle radius
            color: fill color for circles
            alpha: circle transparency
            edgecolor: edge color for circles
            min_value: minimum value to show a dot
        """
        for _, row in gdf.iterrows():
            val = values.get(row["STUSPS"], 0)
            if val < min_value:
                continue
            centroid = row["geometry"].centroid
            ax.scatter(
                centroid.x,
                centroid.y,
                s=val * scale_factor,
                c=color,
                alpha=alpha,
                edgecolors=edgecolor,
                linewidths=0.5,
                zorder=5,
            )

    def save(
        self,
        filename: str,
        *,
        formats: tuple[str, ...] = ("pdf", "svg"),
        directory: Path | None = None,
    ) -> list[Path]:
        """Save the current figure to file(s).

        Args:
            filename: base filename (without extension)
            formats: tuple of formats to save ("pdf", "svg", "png")
            directory: output directory (defaults to latex/figures/)

        Returns:
            list of saved file paths
        """
        if self._fig is None:
            raise RuntimeError("No figure to save. Call choropleth() or categorical() first.")

        outdir = directory or FIGURES_DIR
        outdir.mkdir(parents=True, exist_ok=True)

        paths = []
        for fmt in formats:
            path = outdir / f"{filename}.{fmt}"
            self._fig.savefig(path, format=fmt, bbox_inches="tight", pad_inches=0.1)
            paths.append(path)
            print(f"  Saved: {path}")

        return paths

    def close(self):
        """Close the figure to free memory."""
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
