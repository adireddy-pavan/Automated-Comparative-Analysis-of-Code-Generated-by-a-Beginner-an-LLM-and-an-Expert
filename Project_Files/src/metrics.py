"""Static-metric extraction via the radon / pylint / bandit command-line tools.

Every tool is invoked through its *documented JSON (or text) CLI* and the raw
output is both parsed and saved verbatim under ``evidence/``. We never import the
tools' Python internals, so the code cannot drift against an unverified API.

Tool output shapes were confirmed against the installed versions:

* ``radon cc -j``  -> ``{file: [{"complexity": int, "type": str, ...}, ...]}``
* ``radon mi -j``  -> ``{file: {"mi": float, "rank": str}}``
* ``radon raw -j`` -> ``{file: {"loc","lloc","sloc","comments", ...}}``
* ``radon hal -j`` -> ``{file: {"total": {"volume","effort", ...}, ...}}``
* ``pylint --output-format=json`` -> ``[{"symbol","message-id", ...}, ...]`` plus a
  text run whose summary line reads ``Your code has been rated at X.XX/10``.
* ``bandit -f json`` -> ``{"metrics": {"_totals": {"SEVERITY.LOW": int, ...}}, ...}``
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

import config
from src import utils

_log = utils.get_logger

# Resolve platform-appropriate CLI names from the active Python environment.
# Windows venv entry points have .exe suffixes; POSIX venv commands do not.
RADON = utils.analysis_tool_path("radon")
PYLINT = utils.analysis_tool_path("pylint")
BANDIT = utils.analysis_tool_path("bandit")

_SCORE_RE = re.compile(r"rated at (-?\d+\.\d+)/10")


# --------------------------------------------------------------------------- #
# radon
# --------------------------------------------------------------------------- #
def _collect_complexities(blocks: Any) -> list[float]:
    """Recursively pull complexity from function/method blocks (skip class agg)."""
    out: list[float] = []
    if not isinstance(blocks, list):
        return out
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get("type") in ("function", "method") and "complexity" in block:
            out.append(float(block["complexity"]))
        out.extend(_collect_complexities(block.get("closures")))
        out.extend(_collect_complexities(block.get("methods")))
    return out


def run_radon_cc(path: Path) -> dict[str, Any]:
    """Return ``{"mean_cc", "max_cc", "_raw"}`` from ``radon cc -j``."""
    proc = utils.run_command([RADON, "cc", str(path), "-j"])
    raw = proc.stdout or proc.stderr or ""
    mean_cc: float | None = None
    max_cc: float | None = None
    try:
        data = utils.read_json_str(raw)
        values = _collect_complexities(next(iter(data.values()), []))
        if values:
            mean_cc = round(sum(values) / len(values), 3)
            max_cc = float(max(values))
        else:  # a file with no functions -> trivially complexity 0
            mean_cc, max_cc = 0.0, 0.0
    except Exception as exc:  # pragma: no cover - defensive
        _log().debug("radon cc parse failed for %s: %s", path, exc)
    return {"mean_cc": mean_cc, "max_cc": max_cc, "_raw": raw}


def run_radon_mi(path: Path) -> dict[str, Any]:
    """Return ``{"mi", "_raw"}`` from ``radon mi -j`` (0-100 scale)."""
    proc = utils.run_command([RADON, "mi", str(path), "-j"])
    raw = proc.stdout or proc.stderr or ""
    mi: float | None = None
    try:
        data = utils.read_json_str(raw)
        entry = next(iter(data.values()), {})
        mi = utils.safe_float(entry.get("mi"))
        if mi is not None:
            mi = round(mi, 3)
    except Exception as exc:  # pragma: no cover
        _log().debug("radon mi parse failed for %s: %s", path, exc)
    return {"mi": mi, "_raw": raw}


def run_radon_raw(path: Path) -> dict[str, Any]:
    """Return ``{"loc","lloc","sloc","comments", "_raw"}`` from ``radon raw -j``."""
    proc = utils.run_command([RADON, "raw", str(path), "-j"])
    raw = proc.stdout or proc.stderr or ""
    result: dict[str, Any] = {k: None for k in ("loc", "lloc", "sloc", "comments")}
    try:
        data = utils.read_json_str(raw)
        entry = next(iter(data.values()), {})
        for key in ("loc", "lloc", "sloc", "comments"):
            value = entry.get(key)
            result[key] = int(value) if value is not None else None
    except Exception as exc:  # pragma: no cover
        _log().debug("radon raw parse failed for %s: %s", path, exc)
    result["_raw"] = raw
    return result


def run_radon_hal(path: Path) -> dict[str, Any]:
    """Return ``{"halstead_volume","halstead_effort","_raw"}`` from ``radon hal -j``."""
    proc = utils.run_command([RADON, "hal", str(path), "-j"])
    raw = proc.stdout or proc.stderr or ""
    volume: float | None = None
    effort: float | None = None
    try:
        data = utils.read_json_str(raw)
        entry = next(iter(data.values()), {})
        total = entry.get("total", {}) if isinstance(entry, dict) else {}
        volume = utils.safe_float(total.get("volume"))
        effort = utils.safe_float(total.get("effort"))
        if volume is not None:
            volume = round(volume, 3)
        if effort is not None:
            effort = round(effort, 3)
    except Exception as exc:  # pragma: no cover
        _log().debug("radon hal parse failed for %s: %s", path, exc)
    return {"halstead_volume": volume, "halstead_effort": effort, "_raw": raw}


# --------------------------------------------------------------------------- #
# pylint
# --------------------------------------------------------------------------- #
def run_pylint(path: Path) -> dict[str, Any]:
    """Return ``{"pylint_score","pylint_issues","_raw_json","_raw_text"}``.

    pylint exits non-zero whenever it reports a message; that is expected and
    handled. We run it twice: once as JSON (for the issue list) and once as text
    (to scrape the ``rated at X/10`` score line, which JSON output omits).
    """
    common = [
        f"--disable={config.PYLINT_DISABLE}",
        "--persistent=n",  # no cross-run cache -> deterministic
        "--score=y",
    ]
    json_proc = utils.run_command([PYLINT, str(path), "--output-format=json", *common])
    raw_json = json_proc.stdout or ""
    issues: int | None = None
    try:
        messages = utils.read_json_str(raw_json)
        issues = len(messages) if isinstance(messages, list) else None
    except Exception as exc:  # pragma: no cover
        _log().debug("pylint json parse failed for %s: %s", path, exc)

    text_proc = utils.run_command([PYLINT, str(path), *common])
    raw_text = text_proc.stdout or ""
    score: float | None = None
    match = _SCORE_RE.search(raw_text)
    if match:
        score = round(float(match.group(1)), 3)

    return {
        "pylint_score": score,
        "pylint_issues": issues,
        "_raw_json": raw_json,
        "_raw_text": raw_text,
    }


# --------------------------------------------------------------------------- #
# bandit
# --------------------------------------------------------------------------- #
def run_bandit(path: Path) -> dict[str, Any]:
    """Return per-severity bandit counts from ``bandit -r <file> -f json``.

    bandit exits non-zero when it finds issues; handled. Counts are read from the
    authoritative ``metrics._totals`` block.
    """
    proc = utils.run_command([BANDIT, "-r", str(path), "-f", "json"])
    raw = proc.stdout or proc.stderr or ""
    low = med = high = None
    try:
        data = utils.read_json_str(raw)
        totals = data.get("metrics", {}).get("_totals", {})
        low = int(totals.get("SEVERITY.LOW", 0))
        med = int(totals.get("SEVERITY.MEDIUM", 0))
        high = int(totals.get("SEVERITY.HIGH", 0))
    except Exception as exc:  # pragma: no cover
        _log().debug("bandit parse failed for %s: %s", path, exc)
    total = None if low is None else (low + med + high)
    return {
        "bandit_low": low,
        "bandit_medium": med,
        "bandit_high": high,
        "bandit_total": total,
        "_raw": raw,
    }


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def extract_static_metrics(path: Path, evidence_prefix: str | None = None) -> dict[str, Any]:
    """Run every static tool on *path* and return one flat metrics dict.

    Raw tool output is written to ``evidence/<prefix>_<tool>...`` when
    *evidence_prefix* is given. This function is what the framework unit test
    exercises on a sample file.

    Args:
        path: Python file to analyse.
        evidence_prefix: If set, raw outputs are saved under this prefix.

    Returns:
        Dict with keys: mean_cc, max_cc, mi, halstead_volume, halstead_effort,
        loc, lloc, sloc, comments, pylint_score, pylint_issues, bandit_low,
        bandit_medium, bandit_high, bandit_total.
    """
    path = Path(path)
    cc = run_radon_cc(path)
    mi = run_radon_mi(path)
    raw = run_radon_raw(path)
    hal = run_radon_hal(path)
    pyl = run_pylint(path)
    ban = run_bandit(path)

    if evidence_prefix:
        utils.save_evidence(f"{evidence_prefix}_radon_cc.json", cc["_raw"])
        utils.save_evidence(f"{evidence_prefix}_radon_mi.json", mi["_raw"])
        utils.save_evidence(f"{evidence_prefix}_radon_raw.json", raw["_raw"])
        utils.save_evidence(f"{evidence_prefix}_radon_hal.json", hal["_raw"])
        utils.save_evidence(f"{evidence_prefix}_pylint.json", pyl["_raw_json"])
        utils.save_evidence(f"{evidence_prefix}_pylint.txt", pyl["_raw_text"])
        utils.save_evidence(f"{evidence_prefix}_bandit.json", ban["_raw"])

    return {
        "mean_cc": cc["mean_cc"],
        "max_cc": cc["max_cc"],
        "mi": mi["mi"],
        "halstead_volume": hal["halstead_volume"],
        "halstead_effort": hal["halstead_effort"],
        "loc": raw["loc"],
        "lloc": raw["lloc"],
        "sloc": raw["sloc"],
        "comments": raw["comments"],
        "pylint_score": pyl["pylint_score"],
        "pylint_issues": pyl["pylint_issues"],
        "bandit_low": ban["bandit_low"],
        "bandit_medium": ban["bandit_medium"],
        "bandit_high": ban["bandit_high"],
        "bandit_total": ban["bandit_total"],
    }


def collect_metrics(tasks: list, correctness_rows: list[dict]) -> pd.DataFrame:
    """Build the tidy metrics table for every (task, source) and persist it.

    Args:
        tasks: Loaded Task objects (see dataset_loader).
        correctness_rows: Functional results keyed per (task_id, source).

    Returns:
        The merged DataFrame (also written to outputs/metrics.csv and .json).
    """
    log = _log()
    corr_index = {(r["task_id"], r["source"], r["sample"]): r for r in correctness_rows}
    rows: list[dict[str, Any]] = []

    for task in tasks:
        for source in config.SOURCES:
            for sample, file_path in enumerate(task.solution_paths(source), 1):
                label = task.sample_label(source, sample)
                prefix = f"{task.task_id}__{label}"
                log.info("  metrics: %-26s [%s]", task.task_id, label)
                static = extract_static_metrics(file_path, evidence_prefix=prefix)
                corr = corr_index.get((task.task_id, source, sample), {})
                row = {
                    "task_id": task.task_id,
                    "title": task.title,
                    "difficulty": task.difficulty,
                    "source": source,
                    "sample": sample,
                    **static,
                    "functional_pass": corr.get("functional_pass"),
                    "tests_passed": corr.get("tests_passed"),
                    "tests_total": corr.get("tests_total"),
                    "run_seconds": corr.get("run_seconds"),
                }
                rows.append(row)

    df = pd.DataFrame(rows)
    # Stable, deterministic ordering.
    df["difficulty"] = pd.Categorical(
        df["difficulty"], categories=config.DIFFICULTIES, ordered=True)
    df["source"] = pd.Categorical(
        df["source"], categories=config.SOURCES, ordered=True)
    df = df.sort_values(
        ["difficulty", "task_id", "source", "sample"]).reset_index(drop=True)
    df["difficulty"] = df["difficulty"].astype(str)
    df["source"] = df["source"].astype(str)

    utils.ensure_output_dirs()
    df.to_csv(config.METRICS_CSV, index=False)
    # Replace any NaN (e.g. a tool that failed) with None so the JSON is valid.
    clean = df.astype(object).where(pd.notna(df), None)
    utils.write_json(config.METRICS_JSON, clean.to_dict(orient="records"))
    log.info("Wrote %s (%d rows) and %s", config.METRICS_CSV, len(df), config.METRICS_JSON)
    return df
