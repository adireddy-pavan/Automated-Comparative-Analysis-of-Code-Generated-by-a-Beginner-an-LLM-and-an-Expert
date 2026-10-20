"""Framework unit tests for the Tharun Project pipeline.

These test the *framework itself* (not the bundled solutions, whose pass/fail is
research data). They must all pass. Run with: ``pytest tests/``.
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pandas as pd
import pytest

# Make the repository root importable regardless of where pytest is invoked.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from src import (  # noqa: E402
    correctness,
    dataset_loader,
    metrics,
    report,
    statistics_engine,
    utils,
    webapp,
)


# --------------------------------------------------------------------------- #
# Cliff's delta
# --------------------------------------------------------------------------- #
def test_cliffs_delta_extremes():
    # Every x strictly below every y -> delta = -1 (large).
    delta, magnitude = statistics_engine.cliffs_delta([1, 2, 3], [4, 5, 6])
    assert delta == -1.0
    assert magnitude == "large"
    # Mirror image -> +1 (large).
    delta, magnitude = statistics_engine.cliffs_delta([4, 5, 6], [1, 2, 3])
    assert delta == 1.0
    assert magnitude == "large"


def test_cliffs_delta_identical_is_negligible():
    delta, magnitude = statistics_engine.cliffs_delta([1, 2, 3], [1, 2, 3])
    assert delta == 0.0
    assert magnitude == "negligible"


def test_cliffs_delta_known_medium():
    # Hand-computed: (#gt - #lt)/(nx*ny) = (3 - 10)/16 = -0.4375 -> medium.
    delta, magnitude = statistics_engine.cliffs_delta([1, 2, 3, 4], [2, 3, 4, 5])
    assert delta == pytest.approx(-0.438, abs=1e-3)
    assert magnitude == "medium"


# --------------------------------------------------------------------------- #
# pass@k estimator
# --------------------------------------------------------------------------- #
def test_pass_at_1_returns_c():
    # For the single-sample case n=k=1, pass@1 must equal c (0 or 1).
    assert correctness.pass_at_k(1, 0, 1) == 0.0
    assert correctness.pass_at_k(1, 1, 1) == 1.0


def test_pass_at_k_multisample():
    assert correctness.pass_at_k(5, 0, 1) == 0.0
    assert correctness.pass_at_k(5, 5, 1) == 1.0
    assert correctness.pass_at_k(2, 1, 1) == pytest.approx(0.5)
    # n - c < k path returns 1.0.
    assert correctness.pass_at_k(3, 2, 2) == 1.0


def test_pass_at_k_validates_arguments():
    with pytest.raises(ValueError):
        correctness.pass_at_k(1, 1, 2)  # k > n
    with pytest.raises(ValueError):
        correctness.pass_at_k(2, 3, 1)  # c > n


# --------------------------------------------------------------------------- #
# dataset_loader validation
# --------------------------------------------------------------------------- #
def test_dataset_loader_discovers_and_validates():
    tasks = dataset_loader.discover_tasks()
    assert len(tasks) >= 1
    palindrome = [t for t in tasks if t.task_id == "is_palindrome"]
    assert palindrome, "the reference task 'is_palindrome' must exist"
    assert dataset_loader.validate_task(palindrome[0]) == []


def test_dataset_loader_flags_bad_entry_point():
    task = [t for t in dataset_loader.discover_tasks() if t.task_id == "is_palindrome"][0]
    broken = dataclasses.replace(task, entry_point="this_function_does_not_exist")
    problems = dataset_loader.validate_task(broken)
    assert any("entry_point" in problem for problem in problems)


# --------------------------------------------------------------------------- #
# Metric-extraction wrapper on a real sample file
# --------------------------------------------------------------------------- #
def test_metric_extraction_on_sample():
    task = [t for t in dataset_loader.discover_tasks() if t.task_id == "is_palindrome"][0]
    result = metrics.extract_static_metrics(task.solution_path("expert"))
    expected_keys = {
        "mean_cc", "max_cc", "mi", "halstead_volume", "loc", "lloc", "sloc",
        "comments", "pylint_score", "pylint_issues", "bandit_low",
        "bandit_medium", "bandit_high", "bandit_total",
    }
    assert expected_keys.issubset(result.keys())
    assert result["mean_cc"] is not None and result["mean_cc"] >= 1
    assert result["mi"] is not None and 0.0 <= result["mi"] <= 100.0
    assert result["loc"] is not None and result["loc"] > 0
    assert result["bandit_total"] == 0  # the expert solution is clean


# --------------------------------------------------------------------------- #
# statistics_engine structure
# --------------------------------------------------------------------------- #
def _toy_df() -> pd.DataFrame:
    """A small, well-separated frame: expert < llm < beginner on mean_cc."""
    rows = []
    profile = {"beginner": (8, 0), "llm": (5, 1), "expert": (2, 1)}
    for i in range(4):
        difficulty = config.DIFFICULTIES[i % len(config.DIFFICULTIES)]
        for source, (cc, passes) in profile.items():
            rows.append({
                "task_id": f"task{i}",
                "title": f"Task {i}",
                "difficulty": difficulty,
                "source": source,
                "mean_cc": cc + i,
                "functional_pass": bool(passes),
            })
    return pd.DataFrame(rows)


def test_statistics_engine_metric_keys():
    record = statistics_engine.analyse_metric(_toy_df(), "mean_cc")
    assert set(record.keys()) == {"label", "orientation", "groups", "friedman", "pairwise"}
    assert set(record["groups"].keys()) == set(config.SOURCES)
    for source in config.SOURCES:
        for key in ("n", "median", "mean", "std", "min", "max"):
            assert key in record["groups"][source]
    assert set(record["friedman"].keys()) == {"statistic", "p", "significant", "kendalls_w", "n_paired_tasks"}
    assert "beginner_vs_expert" in record["pairwise"]
    for key in ("W", "p_raw", "p_adj", "significant", "rank_biserial", "paired_median_difference", "n_discordant", "direction"):
        assert key in record["pairwise"]["beginner_vs_expert"]


def test_statistics_engine_functional_keys():
    functional = statistics_engine.analyse_functional(_toy_df())
    for key in ("pass_rate_overall", "pass_counts_overall",
                "pass_rate_by_difficulty", "cochrans_q"):
        assert key in functional
    assert set(functional["pass_rate_overall"].keys()) == set(config.SOURCES)


@pytest.mark.filterwarnings(
    "ignore:invalid value encountered in scalar divide:RuntimeWarning")
def test_statistics_handles_constant_metric():
    # Every value identical -> degenerate tests must yield None, not crash.
    # (scipy emits a harmless divide warning on identical input; we expect None.)
    df = _toy_df()
    df["mean_cc"] = 5
    record = statistics_engine.analyse_metric(df, "mean_cc")
    assert record["friedman"]["statistic"] is None  # kruskal undefined on identical input
    for source in config.SOURCES:
        assert record["groups"][source]["normal"] is None  # no variance


def test_statistics_handles_small_n():
    # n = 2 per group -> Shapiro (needs n>=3) is skipped, not an error.
    rows = []
    for i in range(2):
        for source, cc in (("beginner", 9), ("llm", 5), ("expert", 2)):
            rows.append({"task_id": f"t{i}", "difficulty": "introductory",
                         "source": source, "mean_cc": cc + i, "functional_pass": True})
    record = statistics_engine.analyse_metric(pd.DataFrame(rows), "mean_cc")
    assert record["groups"]["beginner"]["shapiro_W"] is None


# --------------------------------------------------------------------------- #
# Determinism guard
# --------------------------------------------------------------------------- #
def test_run_seconds_excluded_from_inferential_stats():
    # Wall-clock timing must not be in the statistically tested metric set, so
    # stats.json stays fully deterministic across runs.
    assert "run_seconds" not in config.NUMERIC_METRICS


# --------------------------------------------------------------------------- #
# Report helpers
# --------------------------------------------------------------------------- #
def test_report_fmt_and_pct():
    assert report._fmt(None) == "N/A"
    assert report._fmt(float("nan")) == "N/A"
    assert report._fmt(1.23456) == "1.235"
    assert report._fmt(True) == "yes"
    assert report._pct(0.5) == "50.0%"
    assert report._pct(None) == "N/A"


# --------------------------------------------------------------------------- #
# Web dashboard helpers
# --------------------------------------------------------------------------- #
def test_highlight_escapes_and_classifies():
    html = webapp.highlight("def f():\n    return '<x> & y'")
    # Keyword styling present, and HTML-significant characters are escaped.
    assert 'class="k"' in html
    assert "&lt;x&gt;" in html and "&amp;" in html
    assert "<x>" not in html  # never emits raw angle brackets from the source


def test_json_for_script_is_script_safe():
    payload = webapp._json_for_script([{"task": "</script><b>", "n": 1}])
    assert "</script>" not in payload
    assert "<" not in payload and ">" not in payload
    # Still valid JSON once parsed.
    import json
    assert json.loads(payload)[0]["n"] == 1


def test_dashboard_branding_is_neutral():
    # The dashboard template must not carry the personal/project name.
    from src import webapp_template
    assert "Tharun" not in webapp_template.TEMPLATE


# --------------------------------------------------------------------------- #
# Multi-sample layout, pass@k aggregation, dynamic RQ3 metric count
# --------------------------------------------------------------------------- #
def test_solution_paths_match_sample_counts():
    task = [t for t in dataset_loader.discover_tasks() if t.task_id == "is_palindrome"][0]
    for source in config.SOURCES:
        paths = task.solution_paths(source)
        assert len(paths) == config.SAMPLES_PER_SOURCE[source]
    # The representative path is the first sample, and the LLM arm is multi-sample.
    assert task.solution_path("llm") == task.solution_paths("llm")[0]
    assert config.SAMPLES_PER_SOURCE["llm"] >= 2  # pass@k must be real (k > 1)


def test_sample_label_distinguishes_multisample():
    task = [t for t in dataset_loader.discover_tasks() if t.task_id == "is_palindrome"][0]
    assert task.sample_label("expert", 1) == "expert"        # single-sample
    assert task.sample_label("llm", 3) == "llm_s3"           # multi-sample


def test_pass_at_k_summary_multisample():
    rows = []
    for task_id in ("alpha", "beta"):
        for i in range(1, config.SAMPLES_PER_SOURCE["llm"] + 1):
            rows.append({"task_id": task_id, "source": "llm", "sample": i,
                         "functional_pass": i <= 3})  # 3 of k pass
        rows.append({"task_id": task_id, "source": "beginner", "sample": 1,
                     "functional_pass": True})
        rows.append({"task_id": task_id, "source": "expert", "sample": 1,
                     "functional_pass": True})
    out = statistics_engine.pass_at_k_summary(pd.DataFrame(rows))
    n = config.SAMPLES_PER_SOURCE["llm"]
    # pass@1 = c/n = 3/n; pass@(n) = 1 because at least one of k passes.
    assert out["llm"]["n_samples"] == n
    assert out["llm"]["k1"] == pytest.approx(3 / n, abs=1e-3)
    assert out["llm"][f"k{config.PASS_AT_K[-1]}"] == pytest.approx(1.0)
    # Single-sample sources are undefined beyond pass@1 -> None.
    assert out["beginner"][f"k{config.PASS_AT_K[-1]}"] is None
    assert out["beginner"]["k1"] == pytest.approx(1.0)


def test_rq3_verdict_reports_metric_count():
    from src import webapp
    keys = ["mean_cc", "max_cc", "mi", "halstead_volume", "loc", "sloc",
            "comments", "pylint_score", "pylint_issues", "bandit_total"]
    blob = {"metrics": {k: {"groups": {s: {"median": 1.0} for s in config.SOURCES}}
                        for k in keys}}
    rq3 = webapp._rq3_verdict(blob)
    assert rq3["metric_count"] == len(keys)


def _multisample_metric_df() -> pd.DataFrame:
    """Frame mirroring the real layout: llm has k samples/task, humans have 1."""
    rows = []
    k = config.SAMPLES_PER_SOURCE["llm"]
    for i in range(3):
        difficulty = config.DIFFICULTIES[i % len(config.DIFFICULTIES)]
        rows.append({"task_id": f"t{i}", "difficulty": difficulty,
                     "source": "beginner", "sample": 1, "mean_cc": 8 + i})
        rows.append({"task_id": f"t{i}", "difficulty": difficulty,
                     "source": "expert", "sample": 1, "mean_cc": 2 + i})
        # Five llm samples whose median is deterministic (middle value = 5 + i).
        for s, cc in enumerate((3, 4, 5, 6, 7), 1):
            rows.append({"task_id": f"t{i}", "difficulty": difficulty,
                         "source": "llm", "sample": s, "mean_cc": cc + i})
    return pd.DataFrame(rows)


def test_collapse_samples_balances_sources():
    # The k-sample LLM arm must collapse to one observation per (task, source),
    # so every source is weighted equally (here 3 vs 3 vs 3, not 3 vs 15 vs 3).
    df = _multisample_metric_df()
    collapsed = utils.collapse_samples(df, ["mean_cc"])
    assert len(collapsed) == 3 * len(config.SOURCES)
    for source in config.SOURCES:
        assert int((collapsed["source"] == source).sum()) == df["task_id"].nunique()
    # difficulty is carried through, one value per task.
    assert set(collapsed.columns) >= {"task_id", "source", "mean_cc", "difficulty"}


def test_collapse_samples_uses_per_task_median():
    # The LLM samples (3,4,5,6,7)+i collapse to their median 5+i per task; the
    # single-sample human arms are unchanged.
    df = _multisample_metric_df()
    collapsed = utils.collapse_samples(df, ["mean_cc"])
    for i in range(3):
        task_rows = collapsed[collapsed["task_id"] == f"t{i}"].set_index("source")
        assert task_rows.loc["llm", "mean_cc"] == pytest.approx(5 + i)
        assert task_rows.loc["beginner", "mean_cc"] == pytest.approx(8 + i)
        assert task_rows.loc["expert", "mean_cc"] == pytest.approx(2 + i)


def test_collapsed_metric_tests_have_equal_group_n():
    # Feeding the collapsed frame to analyse_metric yields equal n per source —
    # the property the imbalance fix guarantees for the static-metric tests.
    df = _multisample_metric_df()
    collapsed = utils.collapse_samples(df, ["mean_cc"])
    record = statistics_engine.analyse_metric(collapsed, "mean_cc")
    ns = {record["groups"][s]["n"] for s in config.SOURCES}
    assert ns == {df["task_id"].nunique()}


def test_references_are_in_range_2020_2026():
    # B1: the reference list must match the final proposal (all sources 2020-2026;
    # the dated Dieste 2017 and McCabe 1976 entries were removed).
    joined = " ".join(r["text"] for r in config.REFERENCES)
    assert "Dieste" not in joined and "1976" not in joined
    assert "Chuang" in joined and "Fawareh" in joined
    assert len(config.REFERENCES) == 7


def test_paired_friedman_detects_taskwise_pattern():
    df = _toy_df()
    rec = statistics_engine.analyse_metric(df, "mean_cc")
    assert rec["friedman"]["n_paired_tasks"] == 4
    assert rec["friedman"]["statistic"] is not None
    assert rec["friedman"]["kendalls_w"] is not None

def test_paired_inference_rejects_missing_source():
    df = _toy_df()
    df = df[df.source != "llm"]
    with pytest.raises(ValueError, match="Missing experimental source"):
        statistics_engine.analyse_metric(df, "mean_cc")

def test_paired_binary_uses_one_llm_sample_per_task():
    df = _toy_df()
    rows = []
    for _, record in df.iterrows():
        row = record.to_dict()
        row["sample"] = 1
        rows.append(row)
        if row["source"] == "llm":
            row2 = dict(row)
            row2["sample"] = 2
            row2["functional_pass"] = False
            rows.append(row2)
    result = statistics_engine.analyse_functional(pd.DataFrame(rows))
    assert result["cochrans_q"]["n_paired_tasks"] == 4
    assert result["pass_counts_overall"]["llm"]["total"] == 8
