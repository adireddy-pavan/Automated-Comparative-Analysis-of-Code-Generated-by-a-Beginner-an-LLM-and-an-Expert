"""Discover and validate benchmark tasks.

A *task* is a self-contained directory under ``dataset/tasks/`` holding a
``meta.json``, solution files for each source and a ``tests/test_solution.py``.
A source may contribute one sample or several:

* a single-sample source lives at ``solutions/<source>.py``;
* a ``k``-sample source lives at ``solutions/<source>/sample_<i>.py``.

The number of samples per source is declared once in
``config.SAMPLES_PER_SOURCE``. This module turns those directories into validated
:class:`Task` objects and refuses to proceed if the structure is wrong or any
sample will not import.
"""
from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import config
from src import utils

REQUIRED_META_KEYS = ("id", "title", "difficulty", "entry_point", "description")


@dataclass
class Task:
    """A single benchmark problem with its three candidate solutions."""

    task_id: str
    title: str
    difficulty: str
    entry_point: str
    description: str
    directory: Path
    meta: dict[str, Any] = field(default_factory=dict)

    def solution_paths(self, source: str) -> list[Path]:
        """Absolute paths to every sample for *source*, in sample order.

        A single-sample source resolves to ``solutions/<source>.py``; a
        multi-sample source to ``solutions/<source>/sample_1.py`` ... ``sample_k.py``
        where ``k = config.SAMPLES_PER_SOURCE[source]``.
        """
        base = self.directory / "solutions"
        count = config.SAMPLES_PER_SOURCE.get(source, 1)
        if count == 1:
            return [base / config.SOURCE_FILES[source]]
        return [base / source / f"sample_{i}.py" for i in range(1, count + 1)]

    def solution_path(self, source: str) -> Path:
        """Absolute path to *source*'s representative (first) sample."""
        return self.solution_paths(source)[0]

    def sample_label(self, source: str, sample: int) -> str:
        """Human/evidence label for a sample, e.g. ``llm_s3`` or ``expert``."""
        if config.SAMPLES_PER_SOURCE.get(source, 1) == 1:
            return source
        return f"{source}_s{sample}"

    @property
    def test_path(self) -> Path:
        """Absolute path to the task's pytest file."""
        return self.directory / "tests" / "test_solution.py"


def _load_meta(task_dir: Path) -> dict[str, Any]:
    return utils.read_json(task_dir / "meta.json")


def discover_tasks() -> list[Task]:
    """Scan the tasks directory and return Task objects, deterministically sorted.

    Returns:
        Tasks ordered by (difficulty tier, task id). Directories without a
        ``meta.json`` are skipped silently (they are not tasks).
    """
    tasks: list[Task] = []
    if not config.TASKS_DIR.exists():
        return tasks
    for task_dir in sorted(config.TASKS_DIR.iterdir()):
        if not task_dir.is_dir():
            continue
        meta_file = task_dir / "meta.json"
        if not meta_file.exists():
            continue
        meta = _load_meta(task_dir)
        tasks.append(
            Task(
                task_id=str(meta.get("id", task_dir.name)),
                title=str(meta.get("title", task_dir.name)),
                difficulty=str(meta.get("difficulty", "unknown")),
                entry_point=str(meta.get("entry_point", "")),
                description=str(meta.get("description", "")),
                directory=task_dir,
                meta=meta,
            )
        )

    def sort_key(task: Task) -> tuple[int, str]:
        known = task.difficulty in config.DIFFICULTIES
        tier = config.DIFFICULTIES.index(task.difficulty) if known else 99
        return (tier, task.task_id)

    return sorted(tasks, key=sort_key)


def _imports_and_defines(path: Path, entry_point: str) -> tuple[bool, str]:
    """Return (ok, reason). Imports *path* in isolation and checks entry_point."""
    if not path.exists():
        return False, f"missing file {path.name}"
    # A globally-unique module name derived from the path under tasks/, so that
    # same-named sample files in different tasks never collide in importlib.
    try:
        rel = path.relative_to(config.TASKS_DIR)
    except ValueError:
        rel = path
    module_name = "_probe_" + re.sub(r"\W+", "_", str(rel.with_suffix("")))
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return False, "could not create import spec"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - we want any import error reported
        return False, f"import error: {exc!r}"
    if not hasattr(module, entry_point):
        return False, f"does not define entry_point '{entry_point}'"
    if not callable(getattr(module, entry_point)):
        return False, f"'{entry_point}' is not callable"
    return True, "ok"


def validate_task(task: Task) -> list[str]:
    """Return a list of human-readable problems with *task* (empty == valid)."""
    problems: list[str] = []

    for key in REQUIRED_META_KEYS:
        if key not in task.meta:
            problems.append(f"meta.json missing key '{key}'")

    if task.difficulty not in config.DIFFICULTIES:
        problems.append(
            f"difficulty '{task.difficulty}' not one of {config.DIFFICULTIES}"
        )

    if not task.test_path.exists():
        problems.append("missing tests/test_solution.py")

    for source in config.SOURCES:
        paths = task.solution_paths(source)
        expected = config.SAMPLES_PER_SOURCE.get(source, 1)
        if len(paths) != expected:  # defensive; should never happen
            problems.append(f"{source}: expected {expected} sample(s), found {len(paths)}")
        for sample, path in enumerate(paths, 1):
            ok, reason = _imports_and_defines(path, task.entry_point)
            if not ok:
                problems.append(f"{task.sample_label(source, sample)}: {reason}")

    return problems


def load_dataset(strict: bool = True, tier: str | None = None) -> list[Task]:
    """Discover, validate and return all tasks (optionally one *tier* only).

    Args:
        strict: If True, raise ValueError when any task fails validation.
        tier: If given, keep only tasks of that difficulty.

    Returns:
        The validated list of Task objects.

    Raises:
        ValueError: When *strict* and one or more tasks are invalid, or when no
            tasks are found at all.
    """
    log = utils.get_logger()
    tasks = discover_tasks()
    if tier:
        tasks = [t for t in tasks if t.difficulty == tier]

    if not tasks:
        msg = f"No tasks discovered under {config.TASKS_DIR}"
        if strict:
            raise ValueError(msg)
        log.warning(msg)
        return []

    all_problems: dict[str, list[str]] = {}
    for task in tasks:
        problems = validate_task(task)
        if problems:
            all_problems[task.task_id] = problems

    if all_problems:
        for task_id, problems in all_problems.items():
            for problem in problems:
                log.error("INVALID %s: %s", task_id, problem)
        if strict:
            raise ValueError(
                f"{len(all_problems)} task(s) failed validation; see log above."
            )

    counts = {d: sum(1 for t in tasks if t.difficulty == d) for d in config.DIFFICULTIES}
    log.info(
        "Validated %d tasks  (introductory=%d, intermediate=%d, advanced=%d)",
        len(tasks), counts["introductory"], counts["intermediate"], counts["advanced"],
    )
    return tasks


def tier_counts(tasks: list[Task]) -> dict[str, int]:
    """Return ``{difficulty: count}`` across *tasks*."""
    return {d: sum(1 for t in tasks if t.difficulty == d) for d in config.DIFFICULTIES}
