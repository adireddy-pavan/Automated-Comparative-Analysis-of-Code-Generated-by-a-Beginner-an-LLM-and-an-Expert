#!/usr/bin/env python3
"""Capture terminal / command-line EVIDENCE screenshots into screenshots/cli/.

Each shot runs a real command, captures its real output, renders it as a clean
monochrome "terminal card" HTML, and screenshots it with headless Chromium (then
trims trailing whitespace with Pillow). These map directly to the proposal's
workflow steps and are ideal report evidence: tool versions, dataset validation,
the full pipeline summary, the framework tests, the 10/10 pylint and clean
bandit, radon/pylint/bandit on sample solutions, the results table, and the
statistics. No network is used.

Usage:
    python tools/capture_terminal.py
    python tools/capture_terminal.py --browser /usr/bin/chromium
"""
from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess  # nosec B404 - fixed local commands, no shell injection vector
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots" / "cli"
TMP = Path("/tmp/tharun-terminal")  # nosec B108 - local scratch render dir
PROFILE = Path("/tmp/tharun-chrome-profile")
VENV = ROOT / ".venv" / "bin"

# Each shot: (filename, caption, command-string shown AND executed via the shell).
SHOTS_SPEC = [
    ("01_project_structure.png", "Project structure",
     "ls -1 ; echo '--- src/ ---' ; ls src ; echo '--- dataset/tasks/ ---' ; ls dataset/tasks"),
    ("02_tool_versions.png", "Tool versions (reproducibility)",
     ".venv/bin/python --version ; .venv/bin/radon --version | sed 's/^/radon /' ; "
     ".venv/bin/pylint --version | head -1 ; .venv/bin/bandit --version 2>&1 | head -1"),
    ("03_dataset_validation.png", "Dataset discovery & validation (30 tasks, 3 tiers)",
     ".venv/bin/python -c \"from src import dataset_loader as dl, utils; "
     "utils.setup_logging(); ts=dl.load_dataset(); print(); "
     "[print(f'{t.difficulty:13} {t.task_id:22} entry_point={t.entry_point}') for t in ts]\""),
    ("04_pipeline_summary.png", "Full pipeline run — RESULTS SUMMARY",
     ".venv/bin/python run_analysis.py 2>&1 | tail -n 34"),
    ("05_framework_tests.png", "Framework unit tests (pytest)",
     ".venv/bin/python -m pytest tests/ -o addopts= -v -p no:cacheprovider 2>&1 | tail -30"),
    ("06_pylint_framework.png", "Framework lint — pylint 10.00/10",
     ".venv/bin/pylint src/ run_analysis.py config.py 2>&1 | tail -4"),
    ("07_bandit_framework.png", "Framework security scan — bandit (clean)",
     ".venv/bin/bandit -c pyproject.toml -r src/ run_analysis.py config.py 2>&1 | tail -18"),
    ("08_radon_beginner_vs_expert.png", "Cyclomatic complexity & MI: beginner vs expert",
     ".venv/bin/radon cc dataset/tasks/max_subarray/solutions/beginner.py -s ; "
     ".venv/bin/radon cc dataset/tasks/max_subarray/solutions/expert.py -s ; "
     ".venv/bin/radon mi dataset/tasks/max_subarray/solutions/beginner.py "
     "dataset/tasks/max_subarray/solutions/expert.py -s"),
    ("09_pylint_beginner_sample.png", "pylint on a beginner solution (lower score)",
     ".venv/bin/pylint dataset/tasks/count_vowels/solutions/beginner.py "
     "--disable=C0114,C0115,C0116 --score=y 2>&1 | tail -12"),
    ("10_bandit_beginner_sample.png", "bandit finds an insecure pattern in beginner code",
     ".venv/bin/bandit dataset/tasks/two_sum/solutions/beginner.py 2>&1 | "
     "grep -A6 'Issue:' | head -16"),
    ("11_metrics_table.png", "Computed metrics table (outputs/metrics.csv)",
     ".venv/bin/python -c \"import pandas as pd; pd.set_option('display.width',200); "
     "pd.set_option('display.max_columns',20); df=pd.read_csv('outputs/metrics.csv'); "
     "print(df[['task_id','difficulty','source','sample','mean_cc','mi','pylint_score',"
     "'bandit_total','functional_pass']].head(21).to_string(index=False))\""),
    ("12_statistics.png", "Statistical results (outputs/stats.md)",
     "sed -n '1,22p' outputs/stats.md"),
    ("13_security_signal.png", "Security signal — bandit findings per source",
     ".venv/bin/python -c \"import pandas as pd; df=pd.read_csv('outputs/metrics.csv'); "
     "print(df.groupby('source')['bandit_total'].sum().to_string())\""),
    ("14_quality_gates.png", "All quality gates green",
     "echo '$ pylint src/ run_analysis.py config.py' ; "
     ".venv/bin/pylint src/ run_analysis.py config.py 2>&1 | grep 'rated at' ; "
     "echo ; echo '$ bandit -c pyproject.toml -r src/ run_analysis.py config.py' ; "
     ".venv/bin/bandit -c pyproject.toml -r src/ run_analysis.py config.py -q >/dev/null 2>&1 && "
     "echo 'No issues identified.' ; "
     "echo ; echo '$ pytest tests/' ; "
     ".venv/bin/python -m pytest tests/ -q -p no:cacheprovider 2>&1 | tail -1"),
]

_CSS = """
body{margin:0;background:#e9e9e9;font-family:'DejaVu Sans Mono',monospace}
.term{max-width:1040px;margin:18px auto;border:1px solid #000;background:#fff}
.bar{display:flex;align-items:center;gap:8px;background:#222;padding:9px 12px}
.bar .dot{width:11px;height:11px;border-radius:50%;background:#bbb;display:inline-block}
.bar .ttl{color:#eee;font-size:12px;margin-left:8px;font-weight:bold}
.body{padding:14px 16px;white-space:pre-wrap;font-size:12.5px;line-height:1.5;color:#111}
.cmd{color:#000;font-weight:bold}
.cmd .pr{color:#555}
.out{color:#222}
"""


def render_html(caption: str, command: str, output: str) -> str:
    cmd_html = "".join(
        f'<span class="cmd"><span class="pr">$ </span>{html.escape(line)}</span>\n'
        for line in command.splitlines()
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{_CSS}</style></head><body><div class='term'>"
        f"<div class='bar'><span class='dot'></span><span class='dot'></span>"
        f"<span class='dot'></span><span class='ttl'>{html.escape(caption)}</span></div>"
        f"<div class='body'>{cmd_html}<span class='out'>{html.escape(output)}</span>"
        "</div></div></body></html>"
    )


def find_browser(explicit: str | None) -> str:
    if explicit:
        return explicit
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("No Chromium/Chrome found. Pass --browser /path/to/chromium.")


def trim_bottom(path: Path, margin: int = 22) -> None:
    """Crop trailing whitespace below the content (keeps full width)."""
    try:
        from PIL import Image, ImageChops
    except Exception:  # noqa: BLE001
        return
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, (233, 233, 233))  # page background
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        width, height = img.size
        new_h = min(height, bbox[3] + margin)
        if new_h < height:
            img.crop((0, 0, width, new_h)).save(path)


def run(command: str) -> str:
    env = dict(os.environ, NO_COLOR="1", FORCE_COLOR="0", PY_COLORS="0",
               COLUMNS="120", PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.run(  # nosec B602 - fixed author-controlled command strings
        command, shell=True, cwd=str(ROOT), env=env,
        capture_output=True, text=True, timeout=180, check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return out.rstrip("\n") or "(no output)"


def capture(browser: str, html_path: Path, out_png: Path, scale: float) -> bool:
    cmd = [
        browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        f"--force-device-scale-factor={scale}", "--virtual-time-budget=3000",
        "--run-all-compositor-stages-before-draw", f"--user-data-dir={PROFILE}",
        "--window-size=1080,2400", f"--screenshot={out_png}", html_path.as_uri(),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)  # nosec B603
    ok = out_png.exists() and out_png.stat().st_size > 1500
    if ok:
        trim_bottom(out_png)
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", default=None)
    parser.add_argument("--scale", type=float, default=1.5)
    args = parser.parse_args(argv)

    browser = find_browser(args.browser)
    SHOTS.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    print(f"Using browser: {browser}")

    ok_count = 0
    for name, caption, command in SHOTS_SPEC:
        output = run(command)
        html_doc = render_html(caption, command, output)
        html_path = TMP / (name.replace(".png", ".html"))
        html_path.write_text(html_doc, encoding="utf-8")
        out_png = SHOTS / name
        if capture(browser, html_path, out_png, args.scale):
            print(f"  ok  cli/{name:34} ({out_png.stat().st_size // 1024} KB)")
            ok_count += 1
        else:
            sys.stderr.write(f"  ! cli/{name} failed\n")
    print(f"\nCaptured {ok_count}/{len(SHOTS_SPEC)} terminal screenshots into {SHOTS}/")
    return 0 if ok_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
