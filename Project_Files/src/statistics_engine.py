"""Statistical comparison of the three sources across every numeric metric.

Design choices:

* The same tasks are evaluated by all three sources. The per-task aligned
  metric medians are therefore tested with Friedman (paired omnibus), followed
  by paired Wilcoxon signed-rank tests, Bonferroni adjusted within each metric.
  Rank-biserial correlation describes paired effect size. Shapiro-Wilk remains
  descriptive only; it does not select the inferential test.
* The static-metric tests treat **one observation per (task, source)**: a source
  sampled k times (the LLM arm) is first collapsed to its per-task median
  (``utils.collapse_samples``) so every source is compared on equal footing
  (e.g. 30 vs 30 vs 30) without the k-fold weighting / non-independence that
  pooling all samples would introduce. The full per-sample frame is kept only for
  the functional ``pass@k`` estimator and the per-sample pass-rate, which are the
  measures that legitimately consume every sample.
* Every test is wrapped so degenerate input (identical values, n < 3) yields a
  sensible, JSON-serialisable record instead of crashing the pipeline.
* Descriptive pass rates and pass@k use all samples; matched binary inference
  uses one preselected sample (LLM sample 1) per task, with Cochran's Q and
  exact McNemar comparisons. Results are limited to the archived sample set;
  no inference is made that five LLM samples are independent tasks.
"""
from __future__ import annotations

import math
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats
from tabulate import tabulate

import config
from src import utils
from src.correctness import pass_at_k


# --------------------------------------------------------------------------- #
# Functional pass@k (Chen et al. 2021)
# --------------------------------------------------------------------------- #
def pass_at_k_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Per-source pass@k averaged over tasks, for every k in ``config.PASS_AT_K``.

    For each (source, task) with n samples of which c pass, the unbiased
    estimator ``pass@k = 1 - C(n-c, k)/C(n, k)`` is computed (skipping k > n) and
    averaged across tasks. Single-sample sources report pass@1 only (pass@5 is
    N/A because k > n). This is what makes the estimator *real* for the LLM arm,
    where n = ``config.SAMPLES_PER_SOURCE['llm']`` > 1.
    """
    out: dict[str, Any] = {}
    for source in config.SOURCES:
        sub = df[df["source"] == source]
        n_samples = config.SAMPLES_PER_SOURCE.get(source, 1)
        record: dict[str, Any] = {"n_samples": n_samples,
                                  "tasks": int(sub["task_id"].nunique())}
        for k in config.PASS_AT_K:
            estimates = []
            for _, vals in sub.groupby("task_id")["functional_pass"]:
                n = len(vals)
                c = int(vals.astype(bool).sum())
                if k <= n:
                    estimates.append(pass_at_k(n, c, k))
            record[f"k{k}"] = (round(sum(estimates) / len(estimates), 4)
                               if estimates else None)
        out[source] = record
    return out


# --------------------------------------------------------------------------- #
# Effect size
# --------------------------------------------------------------------------- #
def cliffs_delta(x: list[float], y: list[float]) -> tuple[float, str]:
    """Return (delta, magnitude) for Cliff's delta of *x* vs *y*.

    delta = (#(x>y) - #(x<y)) / (nx * ny), in [-1, 1]. Positive means *x* tends
    to exceed *y*. Magnitude bands follow Romano et al. (2006).
    """
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, "negligible"
    greater = sum(1 for a in x for b in y if a > b)
    lesser = sum(1 for a in x for b in y if a < b)
    delta = (greater - lesser) / (nx * ny)
    magnitude = "large"
    for threshold, name in config.CLIFF_THRESHOLDS:
        if abs(delta) < threshold:
            magnitude = name
            break
    return round(delta, 3), magnitude


def _safe(fn: Callable, *args) -> tuple[Any, Any] | tuple[None, None]:
    """Call a scipy test, returning (stat, p) or (None, None) on failure/NaN.

    Degenerate input (identical values, n too small) can make scipy either raise
    or return NaN; both collapse to (None, None) so downstream JSON stays valid.
    """
    try:
        result = fn(*args)
        stat, pvalue = float(result[0]), float(result[1])
        if math.isnan(stat) or math.isnan(pvalue):
            return None, None
        return stat, pvalue
    except Exception:  # noqa: BLE001 - degenerate input is expected sometimes
        return None, None


def _group_arrays(df: pd.DataFrame, metric: str) -> dict[str, list[float]]:
    """Return {source: [non-null metric values across tasks]} for *metric*."""
    arrays: dict[str, list[float]] = {}
    for source in config.SOURCES:
        series = df.loc[df["source"] == source, metric]
        values = [float(v) for v in series.tolist() if pd.notna(v)]
        arrays[source] = values
    return arrays


def _describe(values: list[float]) -> dict[str, Any]:
    """Summary stats + Shapiro-Wilk for one group."""
    record: dict[str, Any] = {
        "n": len(values),
        "median": round(float(np.median(values)), 3) if values else None,
        "mean": round(float(np.mean(values)), 3) if values else None,
        "std": round(float(np.std(values, ddof=1)), 3) if len(values) > 1 else 0.0,
        "min": round(float(np.min(values)), 3) if values else None,
        "max": round(float(np.max(values)), 3) if values else None,
        "shapiro_W": None,
        "shapiro_p": None,
        "normal": None,
    }
    if len(values) >= 3 and len(set(values)) > 1:
        w, p = _safe(stats.shapiro, values)
        if w is not None:
            record["shapiro_W"] = round(w, 3)
            record["shapiro_p"] = round(p, 3)
            record["normal"] = bool(p > config.ALPHA)
    return record


def _direction(delta: float, a: str, b: str) -> str:
    """Human arrow for a pairwise comparison from Cliff's delta sign."""
    if delta > 0:
        return f"{a} > {b}"
    if delta < 0:
        return f"{a} < {b}"
    return f"{a} ~ {b}"


def _paired_rank_biserial(differences: np.ndarray) -> float:
    """Rank-biserial correlation of non-zero paired differences; direction a-b."""
    nonzero = differences[differences != 0]
    if not len(nonzero):
        return 0.0
    ranks = stats.rankdata(np.abs(nonzero))
    denom = float(ranks.sum())
    return round(float((ranks[nonzero > 0].sum() - ranks[nonzero < 0].sum()) / denom), 3)


def analyse_metric(df: pd.DataFrame, metric: str) -> dict[str, Any]:
    """Matched-task inference with identical task IDs in every source."""
    label, orientation = config.NUMERIC_METRICS[metric]
    if df.duplicated(["task_id", "source"]).any():
        raise ValueError("Collapse samples to one observation per task/source first")
    pivot = df.pivot(index="task_id", columns="source", values=metric)
    missing = [src for src in config.SOURCES if src not in pivot.columns]
    if missing:
        raise ValueError(f"Missing experimental source(s): {missing}")
    common = pivot[list(config.SOURCES)].dropna()
    arrays = {src: common[src].astype(float).to_numpy() for src in config.SOURCES}
    groups = {src: _describe(arr.tolist()) for src, arr in arrays.items()}
    n = len(common)
    friedman: dict[str, Any] = {
        "statistic": None, "p": None, "significant": None,
        "kendalls_w": None, "n_paired_tasks": n,
    }
    # scipy raises when ALL values are identical, and returns NaN for ties only.
    if n >= 3:
        stat, prob = _safe(stats.friedmanchisquare, *(arrays[src] for src in config.SOURCES))
        if stat is not None:
            w = float(stat) / (n * (len(config.SOURCES) - 1))
            friedman.update({"statistic": round(stat, 4),
                            "p": float(f"{prob:.10g}"), "significant": bool(prob < config.ALPHA),
                            "kendalls_w": round(w, 4)})
    pairwise = {}
    for a, b in config.PAIRS:
        diffs = arrays[a] - arrays[b]
        nonzero = diffs[diffs != 0]
        if n == 0:
            wstat, praw = None, None
        elif len(nonzero) == 0:
            wstat, praw = 0.0, 1.0
        else:
            wstat, praw = _safe(lambda v: stats.wilcoxon(
                v, zero_method="wilcox", alternative="two-sided", method="auto"), diffs)
        padj = min(1.0, praw * len(config.PAIRS)) if praw is not None else None
        rbc = _paired_rank_biserial(diffs)
        pairwise[f"{a}_vs_{b}"] = {
            "W": round(wstat, 3) if wstat is not None else None,
            "p_raw": float(f"{praw:.10g}") if praw is not None else None,
            "p_adj": float(f"{padj:.10g}") if padj is not None else None,
            "significant": bool(padj < config.ALPHA) if padj is not None else None,
            "rank_biserial": rbc,
            "paired_median_difference": round(float(np.median(diffs)), 4) if n else None,
            "n_discordant": int(len(nonzero)),
            "direction": f"{a} > {b}" if rbc > 0 else f"{a} < {b}" if rbc < 0 else "ties",
        }
    return {"label": label, "orientation": orientation, "groups": groups,
            "friedman": friedman, "pairwise": pairwise}


def _matched_binary_inference(df: pd.DataFrame) -> dict[str, Any]:
    """Cochran Q and exact paired McNemar, one fixed sample per source/task.

    LLM sample 1 was selected by its pre-existing numerical identifier, *not*
    its outcome. This inferential subset must not be confused with descriptive
    150-sample LLM pass rates.
    """
    first = df[(df["sample"] == 1)].copy() if "sample" in df else df.copy()
    if first.duplicated(["task_id", "source"]).any():
        raise ValueError("Multiple functional outcomes for one task/source")
    pivot = first.pivot(index="task_id", columns="source", values="functional_pass")
    for src in config.SOURCES:
        if src not in pivot:
            raise ValueError(f"Missing functional source: {src}")
    complete = pivot[list(config.SOURCES)].dropna().astype(int)
    arr = complete.to_numpy(dtype=int)
    n, k = arr.shape
    q = {"statistic": None, "p": None, "dof": k-1,
         "significant": None, "n_paired_tasks": n,
         "note": "LLM sample 1 only; source matched by task; all-sample rates remain descriptive."}
    if n > 0:
        cols = arr.sum(axis=0)
        rows = arr.sum(axis=1)
        total = int(cols.sum())
        den = k * total - int((rows**2).sum())
        if den:
            value = (k - 1) * (k * int((cols**2).sum()) - total**2) / den
            pv = float(stats.chi2.sf(value, k-1))
            q.update({"statistic": round(float(value), 4), "p": round(pv, 8),
                      "significant": bool(pv < config.ALPHA)})
    pairs = {}
    for a, b in config.PAIRS:
        if n:
            x, y = complete[a], complete[b]
            a_only = int(((x == 1) & (y == 0)).sum())
            b_only = int(((x == 0) & (y == 1)).sum())
            discordant = a_only + b_only
            p_raw = float(stats.binomtest(min(a_only,b_only), discordant, 0.5).pvalue) if discordant else 1.0
        else:
            a_only = b_only = discordant = 0
            p_raw = None
        adj = min(1.0, p_raw * len(config.PAIRS)) if p_raw is not None else None
        pairs[f"{a}_vs_{b}"] = {"a_only": a_only, "b_only": b_only,
            "discordant": discordant, "p_exact": round(p_raw, 8) if p_raw is not None else None,
            "p_adj": round(adj, 8) if adj is not None else None,
            "significant": bool(adj < config.ALPHA) if adj is not None else None,
            "paired_rate_difference": round((a_only - b_only) / n, 4) if n else None}
    return {"cochrans_q": q, "mcnemar_pairs": pairs}


def analyse_functional(df: pd.DataFrame) -> dict[str, Any]:
    """Descriptive pass rates plus matched binary source comparisons."""
    overall_rate: dict[str, float] = {}
    overall_counts: dict[str, dict[str, int]] = {}
    for source in config.SOURCES:
        sub = df[df["source"] == source]
        passes = int(sub["functional_pass"].sum())
        total = int(len(sub))
        overall_counts[source] = {"pass": passes, "total": total}
        overall_rate[source] = round(passes / total, 3) if total else None

    by_difficulty: dict[str, dict[str, Any]] = {}
    for difficulty in config.DIFFICULTIES:
        per_source: dict[str, Any] = {}
        for source in config.SOURCES:
            sub = df[(df["source"] == source) & (df["difficulty"] == difficulty)]
            total = int(len(sub))
            passes = int(sub["functional_pass"].sum())
            per_source[source] = {
                "pass": passes,
                "total": total,
                "rate": round(passes / total, 3) if total else None,
            }
        by_difficulty[difficulty] = per_source

    # Do not pool the LLM's five samples into a chi-square contingency table.
    matched = _matched_binary_inference(df)

    return {
        "pass_rate_overall": overall_rate,
        "pass_counts_overall": overall_counts,
        "pass_rate_by_difficulty": by_difficulty,
        **matched,
    }


def run_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Compute the full statistics structure and write stats.json + stats.md."""
    log = utils.get_logger()
    metrics_present = [m for m in config.NUMERIC_METRICS if m in df.columns]
    # Static-metric tests run on one observation per (task, source): collapse each
    # source's samples to their per-task median so the k-sample LLM arm is not
    # over-weighted relative to the single-sample arms (see utils.collapse_samples).
    # The full, per-sample frame is kept for descriptive pass rates and pass@k.
    metric_df = utils.collapse_samples(df, metrics_present)
    metric_results = {m: analyse_metric(metric_df, m) for m in metrics_present}
    functional = analyse_functional(df)

    stats_blob = {
        "n_tasks": int(df["task_id"].nunique()),
        "n_rows": int(len(df)),
        "n_metric_obs_per_source": {
            s: int((metric_df["source"] == s).sum()) for s in config.SOURCES
        },
        "sources": list(config.SOURCES),
        "samples_per_source": dict(config.SAMPLES_PER_SOURCE),
        "alpha": config.ALPHA,
        "bonferroni_factor": config.BONFERRONI_FACTOR,
        "metrics": metric_results,
        "functional": functional,
        "pass_at_k": pass_at_k_summary(df),
    }

    utils.ensure_output_dirs()
    utils.write_json(config.STATS_JSON, stats_blob)
    _write_stats_md(stats_blob)
    log.info("Wrote %s and %s", config.STATS_JSON, config.STATS_MD)
    return stats_blob


def _fmt(value: Any) -> str:
    """Format a stat value for a Markdown table, using 'N/A' for missing."""
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _write_stats_md(blob: dict[str, Any]) -> None:
    """Render human-readable Markdown tables from the stats structure."""
    samples = blob.get("samples_per_source", {})
    sample_note = ", ".join(f"{s}={samples.get(s, 1)}" for s in config.SOURCES)
    obs = blob.get("n_metric_obs_per_source", {})
    obs_note = ", ".join(f"{s}={obs.get(s, '?')}" for s in config.SOURCES)
    lines = [
        "# Corrected matched-task statistical analysis", "",
        f"Tasks: {blob['n_tasks']}; source samples/task: {sample_note}; paired observations/source: {obs_note}.",
        "", "**Design:** Each of the 30 tasks provides a matched triplet of beginner,",
        "expert and per-task median LLM measurements. Friedman is the omnibus",
        "test; two-sided paired Wilcoxon tests use Bonferroni adjustment",
        "within each metric. Rank-biserial effect sizes preserve pairing.",
        "P-values are exploratory across the many tested metrics (no global family correction).",
        "", "## Matched-task omnibus tests", "",
    ]
    header = ["Metric", "beginner median", "LLM median", "expert median", "n", "Friedman chi2", "p", "Kendall W"]
    rows = []
    for rec in blob["metrics"].values():
        g, fr = rec["groups"], rec["friedman"]
        rows.append([rec["label"], *(_fmt(g[x]["median"]) for x in config.SOURCES),
                     fr["n_paired_tasks"], _fmt(fr["statistic"]),
                     str(fr["p"]), _fmt(fr["kendalls_w"])])
    lines += [tabulate(rows, headers=header, tablefmt="github"), "", "## Paired post-hoc tests", ""]
    pairrows = []
    for rec in blob["metrics"].values():
        for key, pair in rec["pairwise"].items():
            pairrows.append([rec["label"], key.replace("_vs_", " vs "),
                             _fmt(pair["W"]), str(pair["p_adj"]),
                             _fmt(pair["rank_biserial"]),
                             _fmt(pair["paired_median_difference"]), pair["n_discordant"]])
    lines += [tabulate(pairrows, headers=["Metric", "Pair", "Wilcoxon W", "p adjusted",
                                             "Rank-biserial", "Median paired diff", "n nonzero"],
                       tablefmt="github"), "", "## Functional analysis", ""]
    func = blob["functional"]
    rows = [[src, func["pass_counts_overall"][src]["pass"],
             func["pass_counts_overall"][src]["total"],
             _fmt(func["pass_rate_overall"][src])] for src in config.SOURCES]
    lines += [tabulate(rows, headers=["Source", "Passed", "Total samples", "Descriptive pass rate"],
                       tablefmt="github"), ""]
    q = func["cochrans_q"]
    lines += ["**Paired binary test:** prespecified LLM sample 1 per task (30 matched triplets).",
              f"Cochran Q={q['statistic']}; p={q['p']}; n={q['n_paired_tasks']}.", "",
              "**Exact paired McNemar with Bonferroni for three comparisons:**", ""]
    for pair, x in func["mcnemar_pairs"].items():
        lines.append(f"- {pair}: discordant {x['discordant']}; adjusted p={x['p_adj']}; "
                     f"rate difference={x['paired_rate_difference']}")
    lines += ["", "## pass@k", "", "The original visible-tests estimates are descriptive",
              "and must not be interpreted as unseen-test reliability.", ""]
    for src, vals in blob["pass_at_k"].items():
        lines.append(f"- {src}: pass@1={vals.get('k1')}, pass@5={vals.get('k5')}")
    lines.append("")

    with open(config.STATS_MD, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
