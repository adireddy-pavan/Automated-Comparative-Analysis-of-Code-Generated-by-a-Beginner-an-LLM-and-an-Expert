"""Central configuration for the Tharun Project pipeline.

This module is the single source of truth for paths, the random seed, the set of
code "sources" being compared, the metric definitions, and small bits of
metadata used by the report. Nothing here performs analysis; importing it has no
side effects beyond defining constants.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
#: Global random seed applied to ``random`` and ``numpy`` (see utils.seed_everything).
SEED: int = 42

# --------------------------------------------------------------------------- #
# Paths (all relative to the repository root, i.e. this file's directory)
# --------------------------------------------------------------------------- #
ROOT: Path = Path(__file__).resolve().parent
DATASET_DIR: Path = ROOT / "dataset"
TASKS_DIR: Path = DATASET_DIR / "tasks"
OUTPUTS_DIR: Path = ROOT / "outputs"
FIGURES_DIR: Path = ROOT / "figures"
REPORT_DIR: Path = ROOT / "report"
EVIDENCE_DIR: Path = ROOT / "evidence"

#: Created on demand by the pipeline so a fresh clone "just works".
OUTPUT_DIRECTORIES = (OUTPUTS_DIR, FIGURES_DIR, REPORT_DIR, EVIDENCE_DIR)

# Named output artifacts ----------------------------------------------------- #
METRICS_CSV: Path = OUTPUTS_DIR / "metrics.csv"
METRICS_JSON: Path = OUTPUTS_DIR / "metrics.json"
STATS_JSON: Path = OUTPUTS_DIR / "stats.json"
STATS_MD: Path = OUTPUTS_DIR / "stats.md"
RUN_LOG: Path = EVIDENCE_DIR / "run.log"

# --------------------------------------------------------------------------- #
# Experimental factors
# --------------------------------------------------------------------------- #
#: The three code "sources" (independent variable). Order is display order.
SOURCES: tuple[str, ...] = ("beginner", "llm", "expert")

#: File name each *single-sample* source's solution lives under ``solutions/``.
SOURCE_FILES = {s: f"{s}.py" for s in SOURCES}

# --------------------------------------------------------------------------- #
# Sampling (multi-sample / pass@k support)
# --------------------------------------------------------------------------- #
# Number of independent solution samples stored per source. The beginner and
# expert arms are single authored references (one sample each). The LLM arm is
# sampled ``k`` times so the functional ``pass@k`` estimator of Chen et al.
# (2021) is real (k > 1) and within-source variance is observable.
#
# Layout convention (see dataset_loader.Task.solution_paths):
#   * a source with exactly 1 sample lives at  ``solutions/<source>.py``
#   * a source with k > 1 samples lives at     ``solutions/<source>/sample_<i>.py``
#
# Changing a value here is picked up automatically by the loader, validator,
# correctness runner, metrics collector and statistics engine — nothing else
# needs editing.
SAMPLES_PER_SOURCE: dict[str, int] = {
    "beginner": 1,
    "llm": 5,
    "expert": 1,
}

#: The k values reported for the functional pass@k estimator (only k <= the
#: per-source sample count are computable; the rest render as N/A).
PASS_AT_K = (1, 5)

#: Difficulty tiers, ordered easiest -> hardest.
DIFFICULTIES: tuple[str, ...] = ("introductory", "intermediate", "advanced")

# --------------------------------------------------------------------------- #
# Metric definitions
# --------------------------------------------------------------------------- #
# Each numeric metric carries a human label and an "orientation": whether a
# HIGHER raw value is better ("up") or worse ("down"). Orientation drives the
# radar chart normalisation and the "best source" logic in the report so that
# those never hard-code an assumption about a particular metric.
#
#   key                -> (label, orientation)
NUMERIC_METRICS: dict[str, tuple[str, str]] = {
    "mean_cc": ("Mean Cyclomatic Complexity", "down"),
    "max_cc": ("Max Cyclomatic Complexity", "down"),
    "mi": ("Maintainability Index", "up"),
    "halstead_volume": ("Halstead Volume", "down"),
    "loc": ("Lines of Code (LOC)", "down"),
    "lloc": ("Logical LOC", "down"),
    "sloc": ("Source LOC", "down"),
    "comments": ("Comment Lines", "up"),
    "pylint_score": ("Pylint Score (/10)", "up"),
    "pylint_issues": ("Pylint Issue Count", "down"),
    "bandit_low": ("Bandit Low-severity", "down"),
    "bandit_medium": ("Bandit Medium-severity", "down"),
    "bandit_high": ("Bandit High-severity", "down"),
    "bandit_total": ("Bandit Total Findings", "down"),
    "tests_passed": ("Tests Passed", "up"),
}
# NOTE: ``run_seconds`` is recorded per (task, source) in metrics.csv for
# transparency but is deliberately NOT in NUMERIC_METRICS: it is wall-clock
# timing and therefore the only non-deterministic measurement. Excluding it keeps
# every value in stats.json byte-for-byte reproducible across runs.

#: Metrics that get a dedicated box plot.
BOXPLOT_METRICS: tuple[str, ...] = (
    "mean_cc",
    "mi",
    "halstead_volume",
    "sloc",
    "pylint_score",
    "bandit_total",
)

#: Key metrics summarised on the radar chart (subset, one axis each).
RADAR_METRICS: tuple[str, ...] = (
    "mean_cc",
    "mi",
    "halstead_volume",
    "sloc",
    "pylint_score",
    "bandit_total",
    "pass_rate",  # derived, always oriented "up"
)

# Column order for the tidy metrics table (functional columns appended later).
METRIC_TABLE_COLUMNS: tuple[str, ...] = (
    "task_id",
    "title",
    "difficulty",
    "source",
    "sample",
    "mean_cc",
    "max_cc",
    "mi",
    "halstead_volume",
    "loc",
    "lloc",
    "sloc",
    "comments",
    "pylint_score",
    "pylint_issues",
    "bandit_low",
    "bandit_medium",
    "bandit_high",
    "bandit_total",
    "functional_pass",
    "tests_passed",
    "tests_total",
    "run_seconds",
)

# --------------------------------------------------------------------------- #
# Statistics
# --------------------------------------------------------------------------- #
ALPHA: float = 0.05  # significance threshold
BONFERRONI_FACTOR: int = 3  # three pairwise comparisons per metric
#: Pairwise comparisons performed for every metric.
PAIRS: tuple[tuple[str, str], ...] = (
    ("beginner", "expert"),
    ("beginner", "llm"),
    ("expert", "llm"),
)

# Cliff's delta magnitude thresholds (Romano et al. 2006 conventions).
CLIFF_THRESHOLDS = (
    (0.147, "negligible"),
    (0.330, "small"),
    (0.474, "medium"),
)  # otherwise "large"

# --------------------------------------------------------------------------- #
# Report metadata
# --------------------------------------------------------------------------- #
PROJECT_NAME = "Tharun Project"
FULL_TITLE = (
    "Automated Comparative Analysis of Code Generated by "
    "a Beginner, an LLM, and an Expert"
)
AUTHOR = "Tharun"
INSTITUTION = "University of Roehampton"

#: The seven references, fixed and verbatim (all 2020-2026 sources, matching the
#: final proposal). The report renders exactly these, in this order.
REFERENCES: tuple[dict[str, str], ...] = (
    {
        "text": (
            "Chen, M. et al. (2021) Evaluating Large Language Models Trained on "
            "Code. arXiv:2107.03374."
        ),
        "url": "https://arxiv.org/abs/2107.03374",
    },
    {
        "text": (
            "Chuang, Y. T. and Chang, H. Y. (2024) Analyzing novice and competent "
            "programmers' problem-solving behaviors using an automated evaluation "
            "system. Science of Computer Programming, 237, 103138."
        ),
        "url": "https://doi.org/10.1016/j.scico.2024.103138",
    },
    {
        "text": (
            "Cotroneo, D., Improta, C. and Liguori, P. (2025) Human-Written vs. "
            "AI-Generated Code: A Large-Scale Study of Defects, Vulnerabilities, "
            "and Complexity. arXiv:2508.21634."
        ),
        "url": "https://arxiv.org/abs/2508.21634",
    },
    {
        "text": (
            "Fan, A. X. et al. (2024) Evaluating the Quality of Code Comments "
            "Generated by LLMs for Novice Programmers. arXiv:2409.14368."
        ),
        "url": "https://arxiv.org/abs/2409.14368",
    },
    {
        "text": (
            "Fawareh, H. J., Al-Shdaifat, H. M. and Samara, G. (2025) Comparing "
            "Open Source with Software Code Generated by AI Tools from Software "
            "Maintainability Quality Factor Perspective. WSEAS Transactions on "
            "Computer Research, 13, 653-659."
        ),
        "url": "https://wseas.com/journals/cr/2025/b185118-377.pdf",
    },
    {
        "text": (
            "Hou, W. and Ji, Z. (2025) Comparing Large Language Models and Human "
            "Programmers for Generating Programming Code. Advanced Science, 12, "
            "2412279."
        ),
        "url": "https://doi.org/10.1002/advs.202412279",
    },
    {
        "text": (
            "Licorish, S. A. et al. (2025) Comparing Human and LLM Generated "
            "Code: The Jury is Still Out! arXiv:2501.16857."
        ),
        "url": "https://arxiv.org/abs/2501.16857",
    },
)

# Pylint message categories disabled for the *style* run: missing module,
# class, and function docstrings. We disable these so that the docstring signal
# is captured by other metrics (comments) rather than dominating the issue count
# uniformly; this mirrors the spec.
PYLINT_DISABLE = "C0114,C0115,C0116"
