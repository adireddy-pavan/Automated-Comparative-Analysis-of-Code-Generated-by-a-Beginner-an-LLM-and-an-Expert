"""Functional-correctness measurement.

For every (task, source) we copy the candidate solution into an isolated temp
directory as ``solution.py`` alongside the task's test file, then run pytest and
parse the pass/fail counts. A failing solution is *data*, never a pipeline error:
each run is wrapped so one bad solution can never abort the analysis.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
from math import comb
from pathlib import Path
from typing import Any

import config
from src import utils

# Matches the pytest one-line summary, e.g. "2 failed, 3 passed in 0.05s".
_COUNT_RE = {
    "passed": re.compile(r"(\d+) passed"),
    "failed": re.compile(r"(\d+) failed"),
    "error": re.compile(r"(\d+) error"),
    "skipped": re.compile(r"(\d+) skipped"),
    "xfailed": re.compile(r"(\d+) xfailed"),
}


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator from Chen et al. (2021).

    ``pass@k = 1 - C(n - c, k) / C(n, k)`` where *n* is the number of samples and
    *c* the number that pass. For the bundled single-sample dataset ``n = k = 1``
    so ``pass@1 == c`` (0 or 1). Exposed for future multi-sample use.

    Args:
        n: Total samples generated (n >= 1, n >= k).
        c: Number of correct samples (0 <= c <= n).
        k: The k in pass@k (1 <= k <= n).

    Returns:
        The probability in [0, 1] that at least one of k drawn samples passes.
    """
    if k > n or n <= 0:
        raise ValueError("require 1 <= k <= n and n > 0")
    if c < 0 or c > n:
        raise ValueError("require 0 <= c <= n")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def _parse_counts(stdout: str) -> dict[str, int]:
    """Extract pytest result counts from its summary output."""
    counts = {key: 0 for key in _COUNT_RE}
    for key, pattern in _COUNT_RE.items():
        match = pattern.search(stdout)
        if match:
            counts[key] = int(match.group(1))
    return counts


def run_one(task, source: str, sample: int = 1) -> dict[str, Any]:
    """Run one *sample* of *source*'s solution for *task* under pytest.

    Returns a dict with: task_id, title, difficulty, source, sample,
    functional_pass (bool), tests_passed, tests_total, run_seconds, reason.
    """
    log = utils.get_logger()
    label = task.sample_label(source, sample)
    result: dict[str, Any] = {
        "task_id": task.task_id,
        "title": task.title,
        "difficulty": task.difficulty,
        "source": source,
        "sample": sample,
        "functional_pass": False,
        "tests_passed": 0,
        "tests_total": 0,
        "run_seconds": None,
        "reason": "",
    }

    tmp = Path(tempfile.mkdtemp(prefix=f"tharun_{task.task_id}_{label}_"))
    try:
        shutil.copyfile(task.solution_paths(source)[sample - 1], tmp / "solution.py")
        shutil.copyfile(task.test_path, tmp / "test_solution.py")

        env = dict(os.environ)
        env["PYTHONPATH"] = str(tmp) + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        cmd = [
            sys.executable, "-m", "pytest", "-q",
            "--tb=no", "-p", "no:cacheprovider", ".",
        ]
        start = time.perf_counter()
        proc = utils.run_command(cmd, cwd=tmp, env=env, timeout=90,
                                 restrict_resources=True)
        elapsed = time.perf_counter() - start

        stdout = (proc.stdout or "") + "\n" + (proc.stderr or "")
        counts = _parse_counts(stdout)
        passed = counts["passed"]
        failed = counts["failed"] + counts["error"]
        total = passed + failed + counts["skipped"]

        result["tests_passed"] = passed
        result["tests_total"] = total
        result["run_seconds"] = round(elapsed, 4)
        # functional_pass: every collected test passed and at least one ran.
        result["functional_pass"] = bool(
            proc.returncode == 0 and total > 0 and failed == 0
            and counts["skipped"] == 0
        )
        if proc.returncode not in (0, 1):
            result["reason"] = f"pytest runner status {proc.returncode} (not a scored test failure)"
        elif proc.returncode == 1 and failed == 0:
            result["reason"] = "pytest exited nonzero without a parsed failing test"
        if total == 0:
            result["reason"] = "no tests collected (possible import/collection error)"
        utils.save_evidence(f"{task.task_id}__{label}_pytest.txt", stdout)
        log.info(
            "  correctness: %-26s [%-10s] %2d/%-2d %s (%.3fs)",
            task.task_id, label, passed, total,
            "PASS" if result["functional_pass"] else "FAIL", elapsed,
        )
    except Exception as exc:  # noqa: BLE001 - never let one task kill the run
        result["reason"] = f"runner error: {exc!r}"
        log.error("  correctness: %s [%s] runner error: %r", task.task_id, label, exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return result


def run_all(tasks: list) -> list[dict[str, Any]]:
    """Run correctness for every (task, source, sample) and return all rows."""
    rows: list[dict[str, Any]] = []
    for task in tasks:
        for source in config.SOURCES:
            for sample in range(1, config.SAMPLES_PER_SOURCE.get(source, 1) + 1):
                rows.append(run_one(task, source, sample))
    return rows


def pass_at_k_by_source(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate the Chen et al. pass@k estimator per source from result rows.

    For every (source, task) we have n = samples and c = number passing. We
    compute ``pass@k`` per task for each k in ``config.PASS_AT_K`` (skipping
    k > n) and average across tasks. Returns, per source::

        {source: {"n_samples": n, "tasks": t, "k1": mean, "k5": mean | None}}
    """
    # Group (n, c) per (source, task_id).
    grouped: dict[str, dict[str, list[int]]] = {}
    for row in rows:
        src = grouped.setdefault(row["source"], {})
        n_c = src.setdefault(row["task_id"], [0, 0])
        n_c[0] += 1
        n_c[1] += 1 if row["functional_pass"] else 0

    out: dict[str, Any] = {}
    for source, per_task in grouped.items():
        n_samples = config.SAMPLES_PER_SOURCE.get(source, 1)
        record: dict[str, Any] = {"n_samples": n_samples, "tasks": len(per_task)}
        for k in config.PASS_AT_K:
            estimates = [pass_at_k(n, c, k) for n, c in per_task.values() if k <= n]
            record[f"k{k}"] = (round(sum(estimates) / len(estimates), 4)
                               if estimates else None)
        out[source] = record
    return out
