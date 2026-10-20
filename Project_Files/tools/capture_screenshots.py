#!/usr/bin/env python3
"""Capture GUI/output and code screenshots of the analysis dashboard.

Renders the self-contained ``report/dashboard.html`` with headless Chromium and
writes the images into two clearly separated folders:

    screenshots/code/   - the three-way (beginner/llm/expert) source comparison
                          for representative tasks: "proper code" screenshots.
    screenshots/gui/    - the dashboard's output views (overview, metrics,
                          statistics, figures, code-browser, findings).

Each shot targets a dashboard tab (and, for code shots, a specific task) via a URL
hash such as ``#statistics`` or ``#code:two_sum`` that the page reads on load.
No network is used.

Usage:
    python tools/capture_screenshots.py                 # capture everything
    python tools/capture_screenshots.py --only code     # just the code shots
    python tools/capture_screenshots.py --browser /usr/bin/chromium
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD = ROOT / "report" / "dashboard.html"
SHOTS = ROOT / "screenshots"
PROFILE = Path("/tmp/tharun-chrome-profile")

# Each entry: (category, filename, url-hash, window width, window height)
GUI_SHOTS = [
    ("gui", "01_overview.png",      "overview",   1500, 1700),
    ("gui", "02_metrics.png",       "metrics",    1500, 2300),
    ("gui", "03_statistics.png",    "statistics", 1500, 2750),
    ("gui", "04_figures.png",       "figures",    1500, 1750),
    ("gui", "05_code_browser.png",  "code",       1500, 2200),
    ("gui", "06_findings.png",      "findings",   1500, 1900),
]
# One code screenshot per task (discovered dynamically so it never goes stale),
# tall window + auto-trim handles length.
_ALL_TASKS = sorted(
    p.name for p in (ROOT / "dataset" / "tasks").iterdir()
    if (p / "meta.json").exists()
)
CODE_SHOTS = [("code", f"{t}.png", f"code:{t}", 1500, 3200) for t in _ALL_TASKS]

_BROWSER_CANDIDATES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome",
]


def find_browser(explicit: str | None) -> str:
    if explicit:
        return explicit
    for name in _BROWSER_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("No Chromium/Chrome found. Pass --browser /path/to/chromium.")


def trim_bottom(path: Path, margin: int = 24, bg: tuple = (255, 255, 255)) -> None:
    """Crop trailing whitespace below the content (keeps full width)."""
    try:
        from PIL import Image, ImageChops
    except Exception:  # noqa: BLE001
        return
    img = Image.open(path).convert("RGB")
    bbox = ImageChops.difference(img, Image.new("RGB", img.size, bg)).getbbox()
    if bbox:
        width, height = img.size
        new_h = min(height, bbox[3] + margin)
        if new_h < height:
            img.crop((0, 0, width, new_h)).save(path)


def capture(browser: str, out: Path, url_hash: str,
            width: int, height: int, scale: float) -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)
    url = DASHBOARD.as_uri() + (f"#{url_hash}" if url_hash else "")
    cmd = [
        browser, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--default-background-color=FFFFFFFF",
        f"--force-device-scale-factor={scale}",
        "--virtual-time-budget=7000", "--run-all-compositor-stages-before-draw",
        f"--user-data-dir={PROFILE}",
        f"--window-size={width},{height}",
        f"--screenshot={out}", url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    ok = out.exists() and out.stat().st_size > 2000
    if ok:
        trim_bottom(out)
    else:
        sys.stderr.write(f"  ! {out} failed (rc={proc.returncode})\n")
        sys.stderr.write((proc.stderr or "")[-400:] + "\n")
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", default=None)
    parser.add_argument("--only", choices=["gui", "code"], default=None,
                        help="capture only one category")
    parser.add_argument("--scale", type=float, default=1.5,
                        help="device scale factor (crispness); default 1.5")
    args = parser.parse_args(argv)

    browser = find_browser(args.browser)

    # Rebuild the dashboard so screenshots reflect the latest template/data.
    try:
        sys.path.insert(0, str(ROOT))
        from src import webapp
        webapp.build_dashboard()
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"(could not rebuild dashboard: {exc!r}; using existing)\n")

    if not DASHBOARD.exists():
        raise SystemExit(f"{DASHBOARD} missing — run `python run_analysis.py` first.")

    spec = GUI_SHOTS + CODE_SHOTS
    if args.only:
        spec = [s for s in spec if s[0] == args.only]

    print(f"Using browser: {browser}")
    ok_count = 0
    for category, name, url_hash, width, height in spec:
        out = SHOTS / category / name
        if capture(browser, out, url_hash, width, height, args.scale):
            print(f"  ok  {category}/{name:24} ({out.stat().st_size // 1024} KB)")
            ok_count += 1
    print(f"\nCaptured {ok_count}/{len(spec)} screenshots:")
    print(f"    {SHOTS}/code/   (source-code comparisons)")
    print(f"    {SHOTS}/gui/    (dashboard output views)")
    return 0 if ok_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
