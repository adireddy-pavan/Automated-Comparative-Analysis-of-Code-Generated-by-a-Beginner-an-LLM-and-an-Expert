#!/usr/bin/env python3
"""Tharun Project — single entry point for the whole analysis pipeline.

Runs, in order:

    1. validate dataset
    2. functional correctness (subprocess pytest per solution (not security-isolated))
    3. static metrics (radon / pylint / bandit)
    4. statistics (Friedman, paired Wilcoxon, Cochran Q and exact McNemar)
    5. figures (box plots, pass-rate bars, radar)
    6. report (Markdown + HTML + DOCX)

No network access, no API keys, no external servers are required. Example:

    python run_analysis.py                # full pipeline
    python run_analysis.py --tier advanced --skip-report --verbose
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure the repo root is importable when run from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from src import (  # noqa: E402
    correctness,
    dataset_loader,
    metrics,
    report,
    statistics_engine,
    utils,
    visualize,
    webapp,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Automated comparative analysis of beginner / LLM / expert code.",
    )
    parser.add_argument("--skip-figures", action="store_true",
                        help="Do not generate figures.")
    parser.add_argument("--skip-report", action="store_true",
                        help="Do not generate the report.")
    parser.add_argument("--tier", choices=config.DIFFICULTIES, default=None,
                        help="Restrict the run to a single difficulty tier.")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose (DEBUG-level) console logging.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the full pipeline (or the subset selected by CLI flags)."""
    args = parse_args(argv)
    utils.ensure_output_dirs()
    log = utils.setup_logging(verbose=args.verbose)
    utils.seed_everything(config.SEED)

    started = time.perf_counter()
    log.info("%s", "#" * 70)
    log.info("#  %s", config.PROJECT_NAME)
    log.info("#  %s", config.FULL_TITLE)
    log.info("#  seed=%d  tier=%s", config.SEED, args.tier or "all")
    log.info("%s", "#" * 70)

    # 0. Preflight ------------------------------------------------------------
    log.info("\nPreflight — external analysis tools:")
    versions = utils.check_tools(log)
    missing = [tool for tool, version in versions.items() if version == "N/A"]
    if missing:
        log.error("Required tools unavailable: %s. Refusing to generate incomplete metrics.",
                  ", ".join(missing))
        return 3

    # 1. Dataset --------------------------------------------------------------
    utils.banner("Stage 1/6 — Validate dataset", log)
    try:
        tasks = dataset_loader.load_dataset(strict=True, tier=args.tier)
    except ValueError as exc:
        log.error("Dataset validation failed: %s", exc)
        return 2
    counts = dataset_loader.tier_counts(tasks)
    log.info("Dataset OK: %d tasks  %s", len(tasks), counts)

    # 2. Correctness ----------------------------------------------------------
    utils.banner("Stage 2/6 — Functional correctness (subprocess pytest; not sandboxed)", log)
    correctness_rows = correctness.run_all(tasks)

    # 3. Metrics --------------------------------------------------------------
    utils.banner("Stage 3/6 — Static metrics (radon / pylint / bandit)", log)
    df = metrics.collect_metrics(tasks, correctness_rows)

    # 4. Statistics -----------------------------------------------------------
    utils.banner("Stage 4/6 — Statistics", log)
    stats_blob = statistics_engine.run_statistics(df)

    # 5. Figures --------------------------------------------------------------
    figures: list[Path] = []
    if args.skip_figures:
        log.info("\n[skip] Stage 5/6 — Figures (--skip-figures)")
    else:
        utils.banner("Stage 5/6 — Figures", log)
        figures = visualize.make_all_figures(df, stats_blob)

    # 6. Report ---------------------------------------------------------------
    report_paths: dict = {}
    if args.skip_report:
        log.info("\n[skip] Stage 6/6 — Report (--skip-report)")
    else:
        utils.banner("Stage 6/6 — Report", log)
        report_paths = report.build_report(figures=figures or None)
        # Interactive web dashboard (self-contained; never breaks the core run).
        try:
            report_paths["dashboard"] = webapp.build_dashboard()
        except Exception as exc:  # noqa: BLE001
            log.warning("Dashboard build skipped: %r", exc)

    elapsed = time.perf_counter() - started
    _print_summary(log, tasks, df, stats_blob, figures, report_paths, elapsed)
    return 0


def _print_summary(log, tasks, df, stats_blob, figures, report_paths, elapsed) -> None:
    """Emit a clear, screenshot-friendly RESULTS SUMMARY."""
    utils.banner("RESULTS SUMMARY", log)
    rates = stats_blob["functional"]["pass_rate_overall"]
    log.info("Tasks analysed      : %d", len(tasks))
    log.info("Rows in metrics.csv : %d", len(df))
    log.info("")
    log.info("Overall pass rate (functional):")
    for source in config.SOURCES:
        counts = stats_blob["functional"]["pass_counts_overall"][source]
        rate = rates[source]
        pct = "N/A" if rate is None else f"{rate * 100:5.1f}%"
        log.info("    %-9s %s   (%d/%d rows)",
                 source, pct, counts["pass"], counts["total"])
    log.info("")
    log.info("Median key metrics (per source):")
    for metric in ("mean_cc", "mi", "halstead_volume", "sloc", "pylint_score", "bandit_total"):
        label = config.NUMERIC_METRICS[metric][0]
        vals = []
        groups = stats_blob["metrics"].get(metric, {}).get("groups", {})
        for source in config.SOURCES:
            value = groups.get(source, {}).get("median")
            vals.append(f"{source}={'N/A' if value is None else value}")
        log.info("    %-28s %s", label + ":", "  ".join(vals))
    log.info("")
    log.info("Artifacts written:")
    artifacts = [
        config.METRICS_CSV, config.METRICS_JSON, config.STATS_JSON, config.STATS_MD,
    ]
    artifacts += list(figures)
    artifacts += list(report_paths.values())
    artifacts.append(config.RUN_LOG)
    for path in artifacts:
        marker = "ok " if Path(path).exists() else "MISS"
        log.info("    [%s] %s", marker, Path(path).relative_to(config.ROOT)
                 if str(path).startswith(str(config.ROOT)) else path)
    log.info("")
    log.info("Total wall-clock: %.1fs", elapsed)
    log.info("Done.")


if __name__ == "__main__":
    raise SystemExit(main())
