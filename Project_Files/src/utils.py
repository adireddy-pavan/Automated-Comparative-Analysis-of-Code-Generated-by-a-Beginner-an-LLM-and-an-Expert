"""Shared helpers: deterministic seeding, logging, JSON I/O, subprocess running.

Every other module leans on these so behaviour (especially logging and the way
external tools are invoked) is consistent across the pipeline.
"""
from __future__ import annotations

import json
import logging
import math
import random
# subprocess only ever runs fixed, local analysis tools (radon/pylint/bandit);
# see the [tool.bandit] skips rationale in pyproject.toml.
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

import config

_LOGGER_NAME = "tharun"


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def seed_everything(seed: int = config.SEED) -> None:
    """Seed Python's ``random`` and NumPy so the whole run is reproducible.

    Args:
        seed: Integer seed; defaults to :data:`config.SEED` (42).
    """
    random.seed(seed)
    np.random.seed(seed)


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def setup_logging(verbose: bool = False, log_file: Path | None = None) -> logging.Logger:
    """Configure and return the project logger.

    Logs at INFO (or DEBUG when *verbose*) to the console, and always writes a
    full DEBUG-level log to *log_file* (default :data:`config.RUN_LOG`) so no
    console output is ever lost.

    Args:
        verbose: If True, console level is DEBUG instead of INFO.
        log_file: Destination for the full file log; defaults to config.RUN_LOG.

    Returns:
        The configured :class:`logging.Logger`.
    """
    log_file = log_file or config.RUN_LOG
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # idempotent across repeated calls / tests
    logger.propagate = False

    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s")
    )
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the project logger (configured lazily if needed)."""
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        return setup_logging()
    return logger


def banner(title: str, logger: logging.Logger | None = None) -> None:
    """Log a clear, screenshot-friendly stage banner."""
    logger = logger or get_logger()
    line = "=" * 70
    logger.info("\n%s\n  %s\n%s", line, title.upper(), line)


# --------------------------------------------------------------------------- #
# JSON I/O
# --------------------------------------------------------------------------- #
def read_json(path: Path) -> Any:
    """Read and parse a JSON file."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read_json_str(text: str) -> Any:
    """Parse a JSON string (raises ValueError on malformed input)."""
    return json.loads(text)


def write_json(path: Path, data: Any) -> None:
    """Write *data* to *path* as pretty, deterministic JSON (UTF-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, default=_json_default)
        handle.write("\n")


def _json_default(obj: Any) -> Any:
    """Fallback encoder for NumPy / Path types so dumping never crashes."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serialisable")


# --------------------------------------------------------------------------- #
# Subprocess
# --------------------------------------------------------------------------- #
def run_command(
    cmd: Sequence[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 120,
    restrict_resources: bool = False,
) -> subprocess.CompletedProcess:
    """Run *cmd* capturing stdout/stderr as text, never raising on exit code.

    Many of the tools we call (pylint, bandit) intentionally exit non-zero when
    they find issues. We therefore never use ``check=True``; callers inspect
    ``returncode`` and the captured output themselves.

    Args:
        cmd: The command and arguments as a list.
        cwd: Working directory for the child process.
        env: Environment overrides (merged by the caller if needed).
        timeout: Seconds before the call is abandoned.
        restrict_resources: Apply best-effort POSIX CPU/RAM/file limits to a
            child process. This is NOT a filesystem or network sandbox.

    Returns:
        The :class:`subprocess.CompletedProcess`. On timeout or OS error a
        synthetic completed-process with returncode 124/127 is returned so
        callers have a uniform interface.
    """
    def restrict_child() -> None:
        import resource  # POSIX only; child process after fork
        resource.setrlimit(resource.RLIMIT_CPU, (45, 48))
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
        resource.setrlimit(resource.RLIMIT_FSIZE, (16*1024**2, 16*1024**2))

    try:
        # cmd is always a list built from fixed tool names and repo-internal
        # paths (radon/pylint/bandit/pytest); never shell, never request/user
        # input. check=False is intentional (tools exit non-zero on findings).
        return subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            preexec_fn=restrict_child if restrict_resources and __import__('os').name=='posix'
                       else None,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            cmd, 124, stdout=exc.stdout or "", stderr=f"TIMEOUT after {timeout}s"
        )
    except (OSError, ValueError) as exc:  # e.g. tool missing
        return subprocess.CompletedProcess(cmd, 127, stdout="", stderr=str(exc))


def save_evidence(name: str, content: str) -> Path:
    """Persist raw tool output under ``evidence/`` and return the path.

    Args:
        name: File name (e.g. ``"radon_cc_task1_beginner.json"``).
        content: Raw text to store verbatim.
    """
    config.EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = config.EVIDENCE_DIR / name
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content if content is not None else "")
    return path


def ensure_output_dirs() -> None:
    """Create every output directory the pipeline writes into."""
    for directory in config.OUTPUT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Sample collapsing (balanced per-(task, source) view for static-metric stats)
# --------------------------------------------------------------------------- #
def collapse_samples(df: pd.DataFrame, metric_cols: Sequence[str]) -> pd.DataFrame:
    """Reduce each ``(task_id, source)`` to one row via the per-metric median.

    The static-metric statistical tests, the per-source medians shown in the
    report and figures, and the radar chart must all treat **one observation per
    (task, source)**. Otherwise a source sampled ``k`` times (the LLM arm)
    contributes ``k`` non-independent observations per task, inflating its weight
    ``k``-fold. Taking the per-task median collapses those ``k`` samples to one
    representative value, so every source is compared one-per-task (e.g. the
    30-task benchmark becomes 30 vs 30 vs 30). Single-sample sources are unchanged
    (the median of one value is that value).

    The full, per-sample frame is deliberately retained by callers for the things
    that *do* consume every sample: the functional ``pass@k`` estimator, the
    per-sample pass-rate, and the per-sample appendix / explorer tables.

    Args:
        df: Tidy metrics frame containing ``task_id``, ``source`` and the metric
            columns. A ``difficulty`` column, if present, is carried through.
        metric_cols: Numeric metric columns to aggregate by median. Columns not
            present in *df* are silently skipped.

    Returns:
        A new frame with exactly one row per ``(task_id, source)`` pair.
    """
    cols = [c for c in metric_cols if c in df.columns]
    collapsed = (df.groupby(["task_id", "source"], as_index=False, sort=True)[cols]
                 .median())
    if "difficulty" in df.columns:
        meta = df[["task_id", "difficulty"]].drop_duplicates("task_id")
        collapsed = collapsed.merge(meta, on="task_id", how="left")
    return collapsed


def safe_float(value: Any, default: float | None = None) -> float | None:
    """Coerce *value* to float, returning *default* if it cannot be parsed."""
    try:
        if value is None:
            return default
        result = float(value)
        if math.isnan(result):
            return default
        return result
    except (TypeError, ValueError):
        return default


def tool_version(executable: Sequence[str]) -> str:
    """Return a tool's ``--version`` string (first line), or 'N/A' on failure."""
    proc = run_command(list(executable) + ["--version"], timeout=30)
    if proc.returncode != 0:
        return "N/A"
    out = (proc.stdout or proc.stderr or "").strip()
    return out.splitlines()[0] if out else "N/A"


def analysis_tool_path(name: str, *, on_windows: bool | None = None) -> str:
    """Return the CLI executable in this interpreter's environment.

    Windows virtual environments use Scripts/<name>.exe, whereas POSIX
    environments use bin/<name> without an extension. Keeping the paths
    interpreter-local prevents accidental use of a global tool version.
    """
    if on_windows is None:
        on_windows = sys.platform.startswith("win")
    suffix = ".exe" if on_windows else ""
    return str(Path(sys.executable).parent / (name + suffix))


def check_tools(logger: logging.Logger | None = None) -> dict[str, str]:
    """Preflight: report the version of each external analysis tool.

    Resolves radon/pylint/bandit from the active interpreter's directory (the
    venv) and logs each version. The pipeline entry point refuses to run if any
    required tool is missing; missing metrics must never be silently reported.

    Returns:
        Mapping of tool name to its version string ("N/A" if unavailable).
    """
    logger = logger or get_logger()
    versions: dict[str, str] = {}
    for tool in ("radon", "pylint", "bandit"):
        version = tool_version([analysis_tool_path(tool)])
        versions[tool] = version
        if version == "N/A":
            logger.warning("  preflight: %-7s NOT FOUND — metrics from it will be N/A", tool)
        else:
            logger.info("  preflight: %-7s %s", tool, version)
    return versions
