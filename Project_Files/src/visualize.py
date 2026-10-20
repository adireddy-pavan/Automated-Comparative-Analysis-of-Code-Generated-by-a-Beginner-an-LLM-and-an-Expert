"""Black-and-white-friendly figures.

All charts use the non-interactive ``Agg`` backend, a grayscale fill palette, and
*distinct hatches, line styles and markers per source* so they remain legible
when printed in monochrome. Figures regenerate deterministically (no randomness,
fixed DPI, fixed fonts).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # must precede pyplot import
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config  # noqa: E402
from src import utils  # noqa: E402

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": ":",
})

# Per-source monochrome styling: light->dark grey, unique hatch/marker/linestyle.
SOURCE_STYLE: dict[str, dict[str, str]] = {
    "beginner": {"color": "0.85", "hatch": "////", "marker": "o", "linestyle": "-"},
    "llm": {"color": "0.55", "hatch": "....", "marker": "s", "linestyle": "--"},
    "expert": {"color": "0.30", "hatch": "xxxx", "marker": "^", "linestyle": "-."},
}


def _save(fig: plt.Figure, name: str) -> Path:
    """Save *fig* into the figures directory and close it."""
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIGURES_DIR / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _grouped_values(df: pd.DataFrame, metric: str) -> list[list[float]]:
    """Return [values_per_source] dropping NaNs, in config.SOURCES order."""
    out = []
    for source in config.SOURCES:
        series = df.loc[df["source"] == source, metric]
        out.append([float(v) for v in series.tolist() if pd.notna(v)])
    return out


def box_plot(df: pd.DataFrame, metric: str) -> Path | None:
    """One box plot for *metric* with a box per source."""
    if metric not in df.columns:
        return None
    data = _grouped_values(df, metric)
    if all(len(d) == 0 for d in data):
        return None
    label = config.NUMERIC_METRICS[metric][0]

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot(
        data,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 2},
        widths=0.6,
    )
    for patch, source in zip(bp["boxes"], config.SOURCES):
        style = SOURCE_STYLE[source]
        patch.set_facecolor(style["color"])
        patch.set_hatch(style["hatch"])
        patch.set_edgecolor("black")
    for element in ("whiskers", "caps"):
        for line in bp[element]:
            line.set_color("black")
    for flier in bp["fliers"]:
        flier.set(marker="o", markerfacecolor="0.4", markeredgecolor="black", markersize=4)

    ax.set_xticklabels(list(config.SOURCES))
    ax.set_ylabel(label)
    ax.set_xlabel("Source")
    ax.set_title(f"{label} by source")
    return _save(fig, f"box_{metric}.png")


def passrate_by_difficulty(stats_blob: dict[str, Any]) -> Path:
    """Grouped bar chart of pass rate: source x difficulty."""
    by_diff = stats_blob["functional"]["pass_rate_by_difficulty"]
    difficulties = list(config.DIFFICULTIES)
    x = np.arange(len(difficulties))
    width = 0.25

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, source in enumerate(config.SOURCES):
        style = SOURCE_STYLE[source]
        rates = [(by_diff[d][source]["rate"] or 0.0) for d in difficulties]
        ax.bar(
            x + (i - 1) * width, rates, width,
            label=source, color=style["color"], hatch=style["hatch"],
            edgecolor="black",
        )
    ax.set_xticks(x)
    ax.set_xticklabels(difficulties)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Pass rate (fraction of tasks fully passing)")
    ax.set_xlabel("Difficulty tier")
    ax.set_title("Functional pass rate by source and difficulty")
    ax.legend(title="Source")
    return _save(fig, "passrate_by_difficulty.png")


def _radar_value(values: list[float], orientation: str, target: float) -> float:
    """Min-max normalise *target* among *values*, oriented so higher = better."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return 0.5  # all sources equal on this axis
    frac = (target - lo) / (hi - lo)
    return frac if orientation == "up" else 1.0 - frac


def radar_overall(df: pd.DataFrame, stats_blob: dict[str, Any]) -> Path:
    """Radar chart: each axis a key metric normalised so higher = better."""
    metrics = list(config.RADAR_METRICS)
    # Raw per-source value for each radar metric (median, or pass-rate).
    raw: dict[str, dict[str, float]] = {}
    for metric in metrics:
        if metric == "pass_rate":
            raw[metric] = {
                s: float(stats_blob["functional"]["pass_rate_overall"][s] or 0.0)
                for s in config.SOURCES
            }
        else:
            raw[metric] = {
                s: float(df.loc[df["source"] == s, metric].median())
                for s in config.SOURCES
            }

    orientation = {m: ("up" if m == "pass_rate" else config.NUMERIC_METRICS[m][1])
                   for m in metrics}
    labels = [("Pass rate" if m == "pass_rate" else config.NUMERIC_METRICS[m][0])
              for m in metrics]

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for source in config.SOURCES:
        style = SOURCE_STYLE[source]
        norm = [
            _radar_value(list(raw[m].values()), orientation[m], raw[m][source])
            for m in metrics
        ]
        norm += norm[:1]
        ax.plot(angles, norm, color=style["color"], linewidth=2,
                linestyle=style["linestyle"], marker=style["marker"],
                markersize=6, label=source)
        ax.fill(angles, norm, color=style["color"], alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=7)
    ax.set_title("Overall quality profile (normalised, higher = better)", pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10), title="Source")
    return _save(fig, "radar_overall.png")


def make_all_figures(df: pd.DataFrame, stats_blob: dict[str, Any]) -> list[Path]:
    """Generate every figure and return the written paths.

    The box plots and the radar chart show *static* metrics, so they use the same
    balanced one-observation-per-(task, source) view as the statistical tests:
    each source's samples are collapsed to their per-task median first. This keeps
    every figure's medians/spread consistent with stats.json and stops the
    k-sample LLM arm from being drawn k times as densely as the single-sample arms.
    """
    log = utils.get_logger()
    metric_cols = [m for m in config.NUMERIC_METRICS if m in df.columns]
    collapsed = utils.collapse_samples(df, metric_cols)
    paths: list[Path] = []
    for metric in config.BOXPLOT_METRICS:
        path = box_plot(collapsed, metric)
        if path:
            paths.append(path)
            log.info("  figure: %s", path.name)
    paths.append(passrate_by_difficulty(stats_blob))
    log.info("  figure: passrate_by_difficulty.png")
    paths.append(radar_overall(collapsed, stats_blob))
    log.info("  figure: radar_overall.png")
    return paths
