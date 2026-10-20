"""Report generator.

The report is assembled as an ordered list of *content blocks* (headings,
paragraphs, tables, figures, ...). The same block list is rendered to Markdown,
HTML and DOCX, so the three formats can never disagree. Crucially, **every
numeric value is read from ``outputs/metrics.csv`` and ``outputs/stats.json``** —
nothing is typed by hand. Missing values render as ``N/A``.
"""
from __future__ import annotations

import datetime as _dt
import math
import sys
from pathlib import Path
from typing import Any

try:
    import markdown
except ImportError:  # fallback for limited offline review environments
    markdown = None
import pandas as pd

import config
from src import utils

# --------------------------------------------------------------------------- #
# Small block model
# --------------------------------------------------------------------------- #
# A block is a tuple: (kind, *payload). Renderers below interpret each kind.


def _fmt(value: Any, nd: int = 3) -> str:
    """Format any metric value for display; missing -> 'N/A'."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{nd}f}"
    return str(value)


def _fmt_p(value: Any) -> str:
    """Report very small p-values without formatting nonzero values as zero."""
    if value is None:
        return "N/A"
    value = float(value)
    return f"{value:.3g}" if 0 < value < 0.001 else f"{value:.4f}"


def _pct(value: Any) -> str:
    """Format a 0-1 fraction as a percentage string, or 'N/A'."""
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.1f}%"


# --------------------------------------------------------------------------- #
# Data access helpers (all values originate here, from computed files)
# --------------------------------------------------------------------------- #
def _median(stats_blob: dict, metric: str, source: str) -> float | None:
    try:
        return stats_blob["metrics"][metric]["groups"][source]["median"]
    except KeyError:
        return None


def _best_source(stats_blob: dict, metric: str) -> tuple[str | None, float | None]:
    """Return (source, median) that is best for *metric* given its orientation."""
    rec = stats_blob["metrics"].get(metric)
    if not rec:
        return None, None
    orientation = rec["orientation"]
    medians = {s: rec["groups"][s]["median"] for s in config.SOURCES
               if rec["groups"][s]["median"] is not None}
    if not medians:
        return None, None
    if orientation == "up":
        best = max(medians, key=medians.get)
    else:
        best = min(medians, key=medians.get)
    return best, medians[best]


def _df_median(df: pd.DataFrame, metric: str, source: str, tier: str | None = None) -> float | None:
    sub = df[df["source"] == source]
    if tier:
        sub = sub[sub["difficulty"] == tier]
    # Collapse a source's samples to one value per task (its per-task median)
    # before taking the across-task median, so a k-sample source is weighted
    # per task — the same balanced basis the static-metric tests use
    # (statistics_engine via utils.collapse_samples). For tier=None this equals
    # the median reported in stats.json, keeping the RQ3 tally consistent with it.
    per_task = sub.groupby("task_id")[metric].median().dropna()
    return round(float(per_task.median()), 3) if len(per_task) else None


def _order_sources(stats_blob: dict, metric: str) -> list[tuple[str, float]]:
    """Sources ranked best->worst for *metric* (respecting orientation)."""
    rec = stats_blob["metrics"][metric]
    orientation = rec["orientation"]
    pairs = [(s, rec["groups"][s]["median"]) for s in config.SOURCES
             if rec["groups"][s]["median"] is not None]
    pairs.sort(key=lambda kv: kv[1], reverse=orientation == "up")
    return pairs


def _significant_pairs(stats_blob: dict, metric: str) -> list[str]:
    """Human strings for the significant pairwise differences of *metric*."""
    rec = stats_blob["metrics"][metric]
    out = []
    for pair, pr in rec["pairwise"].items():
        if pr["significant"]:
            out.append(
                f"{pair.replace('_vs_', ' vs ')} "
                f"(p_adj={_fmt_p(pr['p_adj'])}, paired rank-biserial={_fmt(pr['rank_biserial'])}, "
                "paired effect size)"
            )
    return out


# --------------------------------------------------------------------------- #
# Section builders
# --------------------------------------------------------------------------- #
def _title_block() -> list:
    today = _dt.date.today().isoformat()
    return [
        ("h1", f"{config.PROJECT_NAME} — {config.FULL_TITLE}"),
        ("p", f"**Author:** {config.AUTHOR}  \n**Institution:** {config.INSTITUTION}  \n"
              f"**Date:** {today}"),
        ("p", "_This report is generated automatically by `run_analysis.py`. "
              "Every figure, table and statistic below is read directly from "
              "`outputs/metrics.csv` and `outputs/stats.json`; no value is "
              "entered by hand. Where a value could not be computed it is shown "
              "as `N/A`._"),
        ("hr",),
    ]


def _executive_summary(stats_blob: dict) -> list:
    key_metrics = list(config.BOXPLOT_METRICS)
    bullets = []
    for metric in key_metrics:
        source, value = _best_source(stats_blob, metric)
        label = config.NUMERIC_METRICS[metric][0]
        orient = "highest" if config.NUMERIC_METRICS[metric][1] == "up" else "lowest"
        if source is None:
            bullets.append(f"{label}: N/A")
        else:
            bullets.append(
                f"**{label}** — best ({orient} median) was **{source}** "
                f"at {_fmt(value)}."
            )
    rates = stats_blob["functional"]["pass_rate_overall"]
    pass_line = ", ".join(f"{s} {_pct(rates[s])}" for s in config.SOURCES)
    n = stats_blob["n_tasks"]

    chi = stats_blob["functional"]["cochrans_q"]
    if chi["significant"] is True:
        corr_sig = (f"differences in pass rate across sources are statistically "
                    f"significant (Cochran Q p={_fmt_p(chi['p'])}).")
    elif chi["significant"] is False:
        corr_sig = (f"differences in pass rate across sources are not statistically "
                    f"significant (Cochran Q p={_fmt_p(chi['p'])}).")
    else:
        corr_sig = "a Cochran Q test of pass rate was not computable on this data."

    return [
        ("h2", "1. Executive Summary"),
        ("p", f"This study compares Python solutions from three sources — "
              f"**beginner**, **LLM**, and **expert** — across **{n}** benchmark "
              f"tasks, using static-analysis metrics, functional testing and "
              f"non-parametric statistics. Headline findings, all computed from "
              f"the data:"),
        ("bullets", bullets),
        ("p", f"**Overall visible-test pass rate:** {pass_line}. A paired task-level "
              f"Cochran Q test using LLM sample 1 gives: {corr_sig} These results "
              "are not independently unseen-test estimates."),
    ]


def _introduction() -> list:
    return [
        ("h2", "2. Introduction & Background"),
        ("p",
         "Large Language Model (LLM) coding assistants now sit between two long-"
         "standing reference points in software engineering: the novice "
         "programmer who is still acquiring idiom and rigour, and the experienced "
         "expert who writes concise, maintainable, secure code. Most published "
         "comparisons are binary — human versus AI — which collapses the very "
         "real gap between a beginner and an expert into a single 'human' "
         "category."),
        ("p",
         "This project takes a three-way view. It asks not only whether LLM output "
         "differs from human output, but *where on the novice-to-expert spectrum "
         "it sits*. To do that objectively it applies the same automated pipeline "
         "of complexity, maintainability, style and security metrics to every "
         "solution, then tests each one for functional correctness and compares "
         "the groups statistically."),
    ]


def _methodology(tasks_by_tier: dict[str, int]) -> list:
    total = sum(tasks_by_tier.values())
    tier_rows = [[t, tasks_by_tier[t]] for t in config.DIFFICULTIES]
    tier_rows.append(["**Total**", total])
    return [
        ("h2", "3. Dataset & Methodology"),
        ("h3", "3.1 Benchmark dataset"),
        ("p",
         f"The benchmark comprises **{total} self-contained, pure-function "
         f"programming tasks** (no I/O, no external dependencies) spread across "
         f"three difficulty tiers:"),
        ("table", ["Difficulty tier", "Number of tasks"], tier_rows),
        ("p",
         "**Honest framing — please read.** This is a *curated, representative "
         "benchmark*. For each task the **beginner** and **expert** solutions are "
         "single authored reference implementations chosen to embody the "
         "characteristics typically associated with each source: a beginner style "
         "(works on the common cases but with poor naming, little decomposition, "
         "higher complexity, weak edge-case handling, and occasional sloppy or "
         "insecure patterns) and an expert style (idiomatic, decomposed, fully "
         "type-hinted, documented, low-complexity, edge-complete). The **LLM** "
         "solutions are labelled as model-generated in the archived dataset, sampled "
         f"{config.SAMPLES_PER_SOURCE['llm']} times per task under controlled "
         "prompting; the author-reported model name, version, date and prompt are recorded in "
         "`dataset/LLM_PROVENANCE.md`. None of the code was scraped from real "
         "students, real assistants, or real professionals."),
        ("p",
         "Results therefore characterise **this benchmark only** and must not be "
         "generalised to any wider population, to real beginner or expert "
         "programmers, or to other programming languages. It is intended — and "
         "deliberately left unchanged — that the beginner solutions fail some "
         "edge-case tests on the harder tasks. That monotonic decline is the "
         "experimental signal: it demonstrates that the automated pipeline can "
         "*detect* such quality and correctness differences. It is **not** an "
         "empirical finding that real beginner programmers fail at these rates."),
        ("h3", "3.2 Tools and metrics"),
        ("p", "Static metrics are extracted by invoking each tool's documented "
              "JSON/command-line interface (never an unverified Python API):"),
        ("bullets", [
            "**radon** — cyclomatic complexity (McCabe), maintainability index, "
            "raw size (LOC/LLOC/SLOC/comments) and Halstead volume.",
            "**pylint** — style/standards score (out of 10) and issue count.",
            "**bandit** — security findings by severity (low / medium / high).",
            "**pytest** — functional correctness: each solution is run in a "
            "separate process against the task's core and edge tests.",
        ]),
        ("h3", "3.3 Statistical methods"),
        ("p",
         "Because samples are small and not assumed normal, analysis is "
         "non-parametric. For each numeric metric we report Shapiro-Wilk per group "
         "(normality diagnostic), a Friedman omnibus test across the three "
         "sources, paired Wilcoxon tests with within-metric Bonferroni correction "
         f"(factor {config.BONFERRONI_FACTOR}), and rank-biserial as a "
         "distribution-free effect size. Functional correctness (binary) is "
         "summarised by pass rate; matched inference uses Cochran Q on "
         "the preselected LLM sample 1 per task plus exact paired McNemar tests. Functional correctness also uses the unbiased `pass@k` "
         "estimator of Chen et al. (2021): the LLM arm is sampled "
         f"{config.SAMPLES_PER_SOURCE['llm']} times per task so its `pass@k` (k>1) "
         "is a descriptive visible-test multi-sample estimate, while the single-sample beginner and "
         "expert arms report `pass@1`."),
        ("p",
         "For the static-metric tests, each source contributes **one observation "
         "per task** — its per-task median across samples — so the multi-sampled "
         "LLM arm is weighted equally with the single-sample human arms rather than "
         f"{config.SAMPLES_PER_SOURCE['llm']}-fold. The per-sample data feed only "
         "the `pass@k` estimator and the per-sample pass rate; the full per-sample "
         "table is retained in the appendix."),
    ]


def _results(stats_blob: dict, figures: list[Path]) -> list:
    metrics = ["mean_cc", "max_cc", "mi", "halstead_volume", "loc", "sloc",
               "comments", "pylint_score", "pylint_issues", "bandit_total"]
    headers = ["Metric"] + [f"median ({s})" for s in config.SOURCES]
    rows = []
    for metric in metrics:
        label = config.NUMERIC_METRICS[metric][0]
        rows.append([label] + [_fmt(_median(stats_blob, metric, s)) for s in config.SOURCES])

    blocks: list = [
        ("h2", "4. Results"),
        ("p", "_Scope: the results below characterise **this benchmark only** and "
              "do not generalise to wider populations of programmers or to other "
              "programming languages._"),
        ("p", "Median value of each metric per source (computed from "
              "`outputs/metrics.csv`):"),
        ("table", headers, rows),
        ("h3", "4.1 Figures"),
    ]

    captions = {
        "box_mean_cc.png": "Distribution of mean cyclomatic complexity per source "
                           "(lower is better).",
        "box_mi.png": "Distribution of maintainability index per source (higher is "
                      "better).",
        "box_halstead_volume.png": "Distribution of Halstead volume per source "
                                   "(lower is better).",
        "box_sloc.png": "Distribution of source lines of code per source (lower is "
                        "leaner).",
        "box_pylint_score.png": "Distribution of pylint score per source (higher is "
                                "better).",
        "box_bandit_total.png": "Distribution of total bandit security findings per "
                                "source (lower is better).",
        "passrate_by_difficulty.png": "Functional pass rate by source and difficulty "
                                      "tier.",
        "radar_overall.png": "Overall normalised quality profile (every axis oriented "
                             "so that further out = better).",
    }
    for fig in figures:
        caption = captions.get(fig.name, fig.name)
        blocks.append(("image", f"../figures/{fig.name}", caption))
    return blocks


def _statistical_analysis(stats_blob: dict) -> list:
    kw_headers = ["Metric", "median (beginner)", "median (llm)", "median (expert)",
                  "Friedman chi2", "Friedman p", "significant"]
    kw_rows = []
    for rec in stats_blob["metrics"].values():
        g = rec["groups"]
        kw_rows.append([
            rec["label"], _fmt(g["beginner"]["median"]), _fmt(g["llm"]["median"]),
            _fmt(g["expert"]["median"]), _fmt(rec["friedman"]["statistic"]),
            _fmt_p(rec["friedman"]["p"]), _fmt(rec["friedman"]["significant"]),
        ])

    pw_headers = ["Metric", "Pair", "W", "p (adj)", "sig", "Rank-biserial", "paired effect"]
    pw_rows = []
    for rec in stats_blob["metrics"].values():
        for pair, pr in rec["pairwise"].items():
            pw_rows.append([
                rec["label"], pair.replace("_vs_", " vs "), _fmt(pr["W"]),
                _fmt_p(pr["p_adj"]), _fmt(pr["significant"]), _fmt(pr["rank_biserial"]),
                "paired",
            ])

    func = stats_blob["functional"]
    chi = func["cochrans_q"]
    chi_text = (f"Cochran Q test of task-matched binary correctness across sources: "
                f"Q = {_fmt(chi['statistic'])}, dof = {_fmt(chi['dof'])}, "
                f"p = {_fmt_p(chi['p'])}, significant = {_fmt(chi['significant'])}.")
    if chi["note"]:
        chi_text += f" Note: {chi['note']}"

    pak = stats_blob.get("pass_at_k", {})
    pak_headers = ["Source", "Samples/task"] + [f"pass@{k}" for k in config.PASS_AT_K]
    pak_rows = []
    for source in config.SOURCES:
        rec = pak.get(source, {})
        row = [source, rec.get("n_samples", 1)]
        for k in config.PASS_AT_K:
            row.append(_fmt(rec.get(f"k{k}")))
        pak_rows.append(row)

    return [
        ("h2", "5. Statistical Analysis"),
        ("h3", "5.1 Omnibus tests (Friedman)"),
        ("p", "Matched-task group medians and the Friedman omnibus test for every metric. "
              "A significant result means at least one source differs."),
        ("table", kw_headers, kw_rows),
        ("h3", "5.2 Pairwise comparisons (paired Wilcoxon, Bonferroni) with effect size"),
        ("p", "Pairwise tests with Bonferroni-adjusted p-values and rank-biserial "
              "effect sizes. 'sig' = adjusted p < 0.05."),
        ("table", pw_headers, pw_rows),
        ("h3", "5.3 Functional correctness"),
        ("p", chi_text),
        ("h3", "5.4 Functional pass@k (Chen et al. 2021)"),
        ("p", "Unbiased pass@k averaged over tasks. pass@k is only defined for "
              "k <= the number of samples, so single-sample sources show N/A beyond "
              "pass@1; the LLM arm is sampled multiple times per task, giving a "
              "descriptive multi-sample estimate rather than pass@1 (independence unverified)."),
        ("table", pak_headers, pak_rows),
    ]


def _rq_findings(df: pd.DataFrame, stats_blob: dict) -> list:
    blocks: list = [("h2", "6. Findings by Research Question")]

    # ---- RQ1: code quality ------------------------------------------------ #
    blocks.append(("h3", "RQ1 — How does code quality compare (complexity, "
                         "maintainability, size, style)?"))
    rq1_metrics = ["mean_cc", "mi", "sloc", "pylint_score"]
    rq1_bullets = []
    for metric in rq1_metrics:
        order = _order_sources(stats_blob, metric)
        label = config.NUMERIC_METRICS[metric][0]
        if not order:
            rq1_bullets.append(f"{label}: N/A")
            continue
        ranking = " > ".join(f"{s} ({_fmt(v)})" for s, v in order)
        sig = _significant_pairs(stats_blob, metric)
        sig_text = ("Significant pairwise differences: " + "; ".join(sig) + "."
                    if sig else "No pairwise difference reached significance after "
                    "Bonferroni correction.")
        rq1_bullets.append(f"**{label}** (best→worst by median): {ranking}. {sig_text}")
    blocks.append(("bullets", rq1_bullets))

    # ---- RQ2: correctness + security ------------------------------------- #
    blocks.append(("h3", "RQ2 — How do correctness and security compare?"))
    func = stats_blob["functional"]
    rates = func["pass_rate_overall"]
    rq2_bullets = [
        "Overall pass rate — " + ", ".join(f"{s}: {_pct(rates[s])}" for s in config.SOURCES) + ".",
    ]
    for difficulty in config.DIFFICULTIES:
        cells = func["pass_rate_by_difficulty"][difficulty]
        rq2_bullets.append(
            f"{difficulty.capitalize()} tier — "
            + ", ".join(f"{s}: {cells[s]['pass']}/{cells[s]['total']} "
                        f"({_pct(cells[s]['rate'])})" for s in config.SOURCES) + "."
        )
    # Security
    bandit_order = _order_sources(stats_blob, "bandit_total")
    if bandit_order:
        sec = ", ".join(f"{s} ({_fmt(v)})" for s, v in bandit_order)
        sig = _significant_pairs(stats_blob, "bandit_total")
        sec_sig = ("Significant: " + "; ".join(sig) + "." if sig
                   else "No pairwise security difference reached significance.")
        rq2_bullets.append(f"Security — median total bandit findings (fewest→most): "
                           f"{sec}. {sec_sig}")
    chi = func["cochrans_q"]
    if chi["significant"] is True:
        rq2_bullets.append(f"The pass-rate difference across sources is statistically "
                           f"significant (Cochran Q p={_fmt_p(chi['p'])}).")
    elif chi["significant"] is False:
        rq2_bullets.append(f"The pass-rate difference across sources is not "
                           f"statistically significant (Cochran Q p={_fmt_p(chi['p'])}).")
    blocks.append(("bullets", rq2_bullets))

    # ---- RQ3: does LLM resemble beginner or expert? ---------------------- #
    blocks.append(("h3", "RQ3 — Does the LLM resemble the beginner or the expert?"))
    rq3_metrics = ["mean_cc", "max_cc", "mi", "halstead_volume", "loc", "sloc",
                   "comments", "pylint_score", "pylint_issues", "bandit_total"]

    def tally(tier: str | None) -> tuple[int, int, int]:
        nearer_beg = nearer_exp = ties = 0
        for metric in rq3_metrics:
            m_llm = _df_median(df, metric, "llm", tier)
            m_beg = _df_median(df, metric, "beginner", tier)
            m_exp = _df_median(df, metric, "expert", tier)
            if None in (m_llm, m_beg, m_exp):
                continue
            d_beg, d_exp = abs(m_llm - m_beg), abs(m_llm - m_exp)
            if d_beg < d_exp:
                nearer_beg += 1
            elif d_exp < d_beg:
                nearer_exp += 1
            else:
                ties += 1
        return nearer_beg, nearer_exp, ties

    nb, ne, nt = tally(None)
    verdict = ("the **expert**" if ne > nb else "the **beginner**" if nb > ne
               else "**neither distinctly** (a tie)")
    rq3_bullets = [
        f"Across {len(rq3_metrics)} metrics overall, the LLM's median was closer to "
        f"the beginner on **{nb}**, closer to the expert on **{ne}**, and tied on "
        f"**{nt}**. Verdict: the LLM most resembles {verdict}.",
    ]
    for tier in config.DIFFICULTIES:
        tb, te, tt = tally(tier)
        tv = ("expert" if te > tb else "beginner" if tb > te else "neither (tie)")
        rq3_bullets.append(
            f"{tier.capitalize()} tier — closer to beginner on {tb}, to expert on "
            f"{te}, tied on {tt} → resembles {tv}."
        )
    blocks.append(("bullets", rq3_bullets))

    # ---- RQ4: limits of automated metrics -------------------------------- #
    blocks.append(("h3", "RQ4 — What are the limits of automated metrics?"))
    failing = df[~df["functional_pass"].astype(bool)]
    rq4_bullets = []
    if len(failing):
        # The most striking case: the failing solution that looks best on MI.
        worst = failing.sort_values("mi", ascending=False).iloc[0]
        rq4_bullets.append(
            f"Concrete disagreement found in the data: task **{worst['task_id']}** "
            f"({worst['source']}) attains a maintainability index of "
            f"**{_fmt(float(worst['mi']))}** and a pylint score of "
            f"**{_fmt(float(worst['pylint_score']))}/10**, yet it still **fails "
            f"functional tests** ({int(worst['tests_passed'])}/"
            f"{int(worst['tests_total'])} passing). Static quality scores looked "
            f"acceptable while the code was, in fact, wrong."
        )
        n_fail = int(len(failing))
        rq4_bullets.append(
            f"In total {n_fail} (source, task) solution(s) failed at least one test; "
            f"static metrics alone would not have flagged the functional defects."
        )
    else:
        rq4_bullets.append(
            "No solution in this run combined healthy static metrics with a test "
            "failure: every solution passed its tests, so no direct "
            "metric-versus-correctness contradiction is present in the data."
        )
    rq4_bullets += [
        "Static metrics measure *form*, not *behaviour*: maintainability index, "
        "complexity and style score say nothing about whether output is correct.",
        "Security scanners such as bandit detect known insecure patterns, not "
        "logic errors or missing edge-case handling.",
        "These caveats are why this study pairs every static metric with executed "
        "functional tests rather than relying on metrics alone.",
    ]
    blocks.append(("bullets", rq4_bullets))
    return blocks


def _limitations() -> list:
    return [
        ("h2", "7. Limitations"),
        ("bullets", [
            "**Curated benchmark.** The beginner and expert solutions were authored "
            "to typify each source and the LLM solutions are archived model-labelled files without authenticated generation logs; "
            "none are sampled from real populations. Findings describe this "
            "benchmark only and do not generalise. The monotonic decline in the "
            "beginner pass rate across tiers shows that the pipeline can *detect* "
            "such differences; it is not a claim that real beginner programmers "
            "fail at these rates.",
            "**Sampling.** The beginner and expert arms use a single authored "
            "reference per task; the LLM arm is sampled "
            f"{config.SAMPLES_PER_SOURCE['llm']} times per task, so `pass@k` (k>1) "
            "is defined for the LLM on the visible-generation tests; within-source variance is observable in its "
            "metrics, while the human arms remain single-sample. Statistical power "
            "is still bounded by the benchmark size; effect sizes are reported "
            "alongside p-values for transparency.",
            "**Model provenance.** The archive identifies Claude as the sole model family, "
            "but independent model-response receipts and original generation logs "
            "are absent. Its use of the visible evaluation tests during generation "
            "prevents treating the original 100% pass rate as unseen accuracy. "
            "A multi-vendor comparison that also includes a "
            "GPT-4-class model is left as future work.",
            "**Python only.** All tasks are Python; results may not transfer to "
            "other languages or paradigms.",
            "**Static-metric limits (see RQ4).** Maintainability, complexity, style "
            "and security scores capture form and known patterns, not functional "
            "correctness; this is why executed tests are included.",
        ]),
    ]


def _conclusion(stats_blob: dict) -> list:
    rates = stats_blob["functional"]["pass_rate_overall"]
    best_mi, _ = _best_source(stats_blob, "mi")
    best_cc, _ = _best_source(stats_blob, "mean_cc")
    best_style, _ = _best_source(stats_blob, "pylint_score")
    return [
        ("h2", "8. Conclusion"),
        ("p",
         f"On this benchmark, the automated pipeline cleanly separates the three "
         f"sources. The **{best_mi}** source led on maintainability, **{best_cc}** "
         f"on (lowest) complexity, and **{best_style}** on style score, while "
         f"overall functional pass rates were "
         + ", ".join(f"{s} {_pct(rates[s])}" for s in config.SOURCES) +
         ". The three-way framing makes visible where LLM output falls relative to "
         "beginner and expert code (RQ3), and the surfaced metric/correctness "
         "disagreements (RQ4) reinforce that static analysis must be paired with "
         "execution. All conclusions are drawn solely from the computed outputs and "
         "characterise this benchmark only; they do not generalise to wider "
         "populations of programmers or to other programming languages."),
    ]


def _references() -> list:
    return [
        ("h2", "9. References"),
        ("links", [(r["text"], r["url"]) for r in config.REFERENCES]),
    ]


def _appendix(df: pd.DataFrame) -> list:
    bin_dir = Path(sys.executable).parent
    versions = {
        "Python": sys.version.split()[0],
        "radon": utils.tool_version([str(bin_dir / "radon")]),
        "pylint": utils.tool_version([str(bin_dir / "pylint")]),
        "bandit": utils.tool_version([str(bin_dir / "bandit")]),
    }
    ver_rows = [[k, v] for k, v in versions.items()]
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Full per-(task, source, sample) table.
    show_cols = ["task_id", "difficulty", "source", "sample", "mean_cc", "max_cc",
                 "mi", "halstead_volume", "sloc", "comments", "pylint_score",
                 "pylint_issues", "bandit_total", "functional_pass",
                 "tests_passed", "tests_total"]
    show_cols = [c for c in show_cols if c in df.columns]
    headers = show_cols
    rows = [[_fmt(v) if isinstance(v, float) else str(v) for v in
             (row[c] for c in show_cols)] for _, row in df.iterrows()]

    return [
        ("h2", "Appendix"),
        ("h3", "A. Tool versions and run metadata"),
        ("table", ["Component", "Version"], ver_rows),
        ("p", f"Run timestamp: {timestamp}. Random seed: {config.SEED}."),
        ("h3", "B. Full per-task metrics"),
        ("table", headers, rows),
        ("hr",),
        ("p", "_End of report. Generated from `outputs/metrics.csv` and "
              "`outputs/stats.json`._"),
    ]


# --------------------------------------------------------------------------- #
# Renderers
# --------------------------------------------------------------------------- #
def _render_markdown(blocks: list) -> str:
    lines: list[str] = []
    for block in blocks:
        kind = block[0]
        if kind == "h1":
            lines += [f"# {block[1]}", ""]
        elif kind == "h2":
            lines += [f"## {block[1]}", ""]
        elif kind == "h3":
            lines += [f"### {block[1]}", ""]
        elif kind == "p":
            lines += [block[1], ""]
        elif kind == "bullets":
            lines += [f"- {item}" for item in block[1]] + [""]
        elif kind == "table":
            headers, rows = block[1], block[2]
            lines.append("| " + " | ".join(str(h) for h in headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            lines.append("")
        elif kind == "image":
            path, caption = block[1], block[2]
            lines += [f"![{caption}]({path})", "", f"*Figure: {caption}*", ""]
        elif kind == "links":
            for i, (text, url) in enumerate(block[1], 1):
                lines.append(f"{i}. {text} <{url}>")
            lines.append("")
        elif kind == "hr":
            lines += ["---", ""]
    return "\n".join(lines)


_CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 900px;
       margin: 2rem auto; padding: 0 1.5rem; color: #000; background: #fff;
       line-height: 1.55; }
h1 { font-size: 1.8rem; border-bottom: 3px solid #000; padding-bottom: .4rem; }
h2 { font-size: 1.35rem; border-bottom: 1px solid #000; margin-top: 2rem;
     padding-bottom: .2rem; }
h3 { font-size: 1.1rem; margin-top: 1.4rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .9rem; }
th, td { border: 1px solid #000; padding: .35rem .55rem; text-align: left; }
th { background: #eee; }
img { max-width: 100%; height: auto; display: block; margin: 1rem auto;
      border: 1px solid #000; }
a { color: #000; }
em { color: #333; }
code { background: #f0f0f0; padding: .1rem .3rem; font-family: 'Courier New', monospace; }
"""


def _render_html(markdown_text: str) -> str:
    if markdown is not None:
        body = markdown.markdown(markdown_text, extensions=["tables", "fenced_code"])
    else:
        import mistune
        # mistune is only a fallback for an offline environment lacking markdown;
        # the pinned production dependency remains Python-Markdown.
        body = mistune.create_markdown(plugins=['table'])(markdown_text)
    return (
        "<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
        f"<title>{config.PROJECT_NAME} Report</title>\n<style>{_CSS}</style>\n"
        f"</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def _render_docx(blocks: list, out_path: Path) -> bool:
    """Best-effort DOCX. Returns True on success, False (logged) on failure."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
    except Exception as exc:  # pragma: no cover
        utils.get_logger().warning("python-docx unavailable, skipping DOCX: %r", exc)
        return False

    try:
        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(12)
        style.paragraph_format.line_spacing = 1.5

        def _plain(text: str) -> str:
            return (text.replace("**", "").replace("`", "")
                        .replace("_", "").replace("  \n", "; ").replace("\n", " "))

        for block in blocks:
            kind = block[0]
            if kind in ("h1", "h2", "h3"):
                doc.add_heading(_plain(block[1]), level=int(kind[1]))
            elif kind == "p":
                doc.add_paragraph(_plain(block[1]))
            elif kind == "bullets":
                for item in block[1]:
                    doc.add_paragraph(_plain(item), style="List Bullet")
            elif kind == "table":
                headers, rows = block[1], block[2]
                table = doc.add_table(rows=1, cols=len(headers))
                table.style = "Table Grid"
                for j, head in enumerate(headers):
                    table.rows[0].cells[j].text = _plain(str(head))
                for row in rows:
                    cells = table.add_row().cells
                    for j, value in enumerate(row):
                        cells[j].text = _plain(str(value))
            elif kind == "image":
                rel = block[1].replace("../", "")
                img_path = config.ROOT / rel
                if img_path.exists():
                    doc.add_picture(str(img_path), width=Inches(5.5))
                doc.add_paragraph(_plain(block[2])).italic = True
            elif kind == "links":
                for i, (text, url) in enumerate(block[1], 1):
                    doc.add_paragraph(f"{i}. {_plain(text)} {url}")
            elif kind == "hr":
                doc.add_paragraph("_" * 40)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(out_path))
        return True
    except Exception as exc:  # pragma: no cover
        utils.get_logger().warning("DOCX generation failed: %r", exc)
        return False


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def build_report(figures: list[Path] | None = None) -> dict[str, Any]:
    """Assemble and write report.md, report.html and (best-effort) report.docx.

    Reads exclusively from outputs/metrics.csv and outputs/stats.json so every
    number is traceable. Returns a dict of written paths.
    """
    log = utils.get_logger()
    df = pd.read_csv(config.METRICS_CSV)
    stats_blob = utils.read_json(config.STATS_JSON)

    if figures is None:
        figures = sorted(config.FIGURES_DIR.glob("*.png"))
    # Order figures: boxplots (config order), then passrate, then radar.
    order = {f"box_{m}.png": i for i, m in enumerate(config.BOXPLOT_METRICS)}
    order["passrate_by_difficulty.png"] = 100
    order["radar_overall.png"] = 101
    figures = sorted(figures, key=lambda p: order.get(p.name, 50))

    tasks_by_tier = {d: int(df[df["difficulty"] == d]["task_id"].nunique())
                     for d in config.DIFFICULTIES}

    blocks: list = []
    blocks += _title_block()
    blocks += _executive_summary(stats_blob)
    blocks += _introduction()
    blocks += _methodology(tasks_by_tier)
    blocks += _results(stats_blob, figures)
    blocks += _statistical_analysis(stats_blob)
    blocks += _rq_findings(df, stats_blob)
    blocks += _limitations()
    blocks += _conclusion(stats_blob)
    blocks += _references()
    blocks += _appendix(df)

    config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md_text = _render_markdown(blocks)
    md_path = config.REPORT_DIR / "report.md"
    md_path.write_text(md_text, encoding="utf-8")

    html_text = _render_html(md_text)
    html_path = config.REPORT_DIR / "report.html"
    html_path.write_text(html_text, encoding="utf-8")

    docx_path = config.REPORT_DIR / "report.docx"
    docx_ok = _render_docx(blocks, docx_path)

    log.info("Wrote %s", md_path)
    log.info("Wrote %s", html_path)
    log.info("Wrote %s", docx_path if docx_ok else "(DOCX skipped)")

    result = {"md": md_path, "html": html_path}
    if docx_ok:
        result["docx"] = docx_path
    return result
