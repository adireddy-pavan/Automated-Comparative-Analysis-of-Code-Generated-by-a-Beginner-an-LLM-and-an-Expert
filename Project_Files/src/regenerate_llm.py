"""OPTIONAL: regenerate the LLM sample solutions from a live language model.

This module is **not** part of the reproducible pipeline and is **never imported
by ``run_analysis.py``**. It does nothing unless the ``LLM_API_KEY`` environment
variable is set, so the core analysis always runs fully offline with no API keys.

It is provided so a future user can, if they wish, replace the curated LLM-style
solutions with output from an actual model and re-run the same analysis. Using it
requires your own API key and network access, and makes the run **non-
deterministic** — that is why it is opt-in and off by default.

Usage (only if you explicitly want it):

    export LLM_API_KEY=sk-...                 # your Anthropic API key
    python -m src.regenerate_llm --task two_sum --dry-run   # preview the prompt
    python -m src.regenerate_llm --task two_sum            # actually call the API

Without ``LLM_API_KEY`` set, every entry point here is a safe no-op that explains
what would happen.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

# Standalone import guard so this file works whether run as a module or a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import dataset_loader, utils  # noqa: E402

# Anthropic Messages API (documented public endpoint). Only contacted when a key
# is present AND the user explicitly runs this module.
_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"
_DEFAULT_MODEL = "claude-sonnet-4-6"

_PROMPT_TEMPLATE = """\
You are writing a Python solution as a typical AI coding assistant would: correct
and readable, with clear comments and light defensive checks. Implement exactly
one function named `{entry_point}` solving this task:

{description}

Return ONLY the Python source for a module defining `{entry_point}` (no markdown
fences, no prose). Standard library only.
"""


def is_enabled() -> bool:
    """True only when an API key is configured (the feature is opt-in)."""
    return bool(os.environ.get("LLM_API_KEY"))


def build_prompt(task) -> str:
    """Return the generation prompt for *task* (no network access)."""
    return _PROMPT_TEMPLATE.format(
        entry_point=task.entry_point, description=task.description
    )


def _call_api(prompt: str, model: str) -> str:
    """POST the prompt to the Anthropic Messages API and return the text reply.

    Only ever called when ``LLM_API_KEY`` is set and the user opted in. Uses the
    standard library so no extra dependency is introduced.
    """
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    # _API_URL is a fixed https:// constant; reject anything else defensively so
    # the urlopen below can only ever speak https to the configured endpoint.
    if not _API_URL.startswith("https://"):
        raise ValueError("API URL must be https://")
    request = urllib.request.Request(
        _API_URL,
        data=payload,
        headers={
            "x-api-key": os.environ["LLM_API_KEY"],
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    # Scheme is asserted https above and the URL is a fixed constant
    # (see the [tool.bandit] skips rationale in pyproject.toml).
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    # Messages API returns {"content": [{"type": "text", "text": "..."}], ...}
    parts = [block.get("text", "") for block in body.get("content", [])]
    return "".join(parts).strip()


def regenerate_task(task_id: str, model: str = _DEFAULT_MODEL,
                    dry_run: bool = False) -> str:
    """Regenerate (or preview) the representative LLM sample for one task.

    Writes to the task's representative LLM sample path
    (``solutions/llm/sample_1.py`` for the multi-sample layout). Optional and
    off by default; the committed samples are recorded in
    ``dataset/LLM_PROVENANCE.md``.

    Args:
        task_id: The task whose LLM sample to regenerate.
        model: Model identifier to request.
        dry_run: If True, only return the prompt; never contact the network.

    Returns:
        A human-readable status string.
    """
    log = utils.get_logger()
    tasks = {t.task_id: t for t in dataset_loader.discover_tasks()}
    if task_id not in tasks:
        return f"Unknown task '{task_id}'. Available: {sorted(tasks)}"
    task = tasks[task_id]
    prompt = build_prompt(task)

    if dry_run:
        return f"[dry-run] Prompt for {task_id}:\n\n{prompt}"
    if not is_enabled():
        return ("LLM_API_KEY is not set, so nothing was changed. This optional "
                "feature is off by default; the core pipeline does not need it.")

    code = _call_api(prompt, model)
    target = task.solution_path("llm")
    target.write_text(code + "\n", encoding="utf-8")
    log.info("Regenerated %s (%d chars)", target, len(code))
    return f"Wrote {target}. NOTE: results are now non-deterministic for this task."


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the optional LLM regeneration tool."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Task id to regenerate.")
    parser.add_argument("--model", default=_DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true",
                        help="Only print the prompt; never call the network.")
    args = parser.parse_args(argv)
    utils.setup_logging()
    print(regenerate_task(args.task, model=args.model, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
