# Screenshot & Evidence Guide — Tharun Project

This guide lists, **in order**, the exact command to run and what to capture for
each step of the workflow described in the proposal. Run each command from the
project root (`tharun-project/`) with the virtual environment available. Every
command is copy-paste ready for Linux/macOS; Windows equivalents are noted.

> Tip: activate the venv first with `source .venv/bin/activate`, then you can drop
> the `.venv/bin/` prefixes. The commands below keep the prefix so they work even
> without activation.

## How to capture the screen (Linux)

```bash
mkdir -p screenshots
# X11 — select a region with the mouse:
scrot -s screenshots/01.png
# Wayland:
grim -g "$(slurp)" screenshots/01.png
# Open an image or the HTML report in the default app:
xdg-open figures/radar_overall.png
xdg-open report/report.html
```
(macOS: `screencapture -i screenshots/01.png`. Windows: press `Win+Shift+S`.)

Run a numbered command, then capture into the matching `screenshots/NN.png`.

---

### 01 — Project structure
Shows the repository layout (proposal: Methodology / deliverables).
```bash
find . -path ./.venv -prune -o -type f -print | grep -v __pycache__ | sort | head -n 60
```
Capture: the directory/file listing (or use `tree -L 3 -I '.venv|__pycache__'`).

### 02 — Dataset validation & tier counts
Shows the benchmark is discovered and validated (proposal: Dataset).
```bash
.venv/bin/python run_analysis.py --skip-figures --skip-report --verbose 2>&1 | sed -n '1,30p'
```
Capture: the "Validated 30 tasks (introductory=10, intermediate=10, advanced=10)"
line and the per-task correctness lines (the LLM arm is sampled 5 times per task,
shown as `llm_s1` … `llm_s5`).

### 03 — The three solution styles for one task
Shows beginner vs expert vs llm for the same problem (proposal: three sources).
The LLM arm has 5 samples per task; sample 1 is shown as the representative.
```bash
for s in beginner expert llm/sample_1; do echo "================ $s ================"; cat dataset/tasks/two_sum/solutions/$s.py; done
```
Capture: the three solutions side by side (note the length/comment/style
differences).

### 04 — Functional correctness for one task (all three sources)
Shows pass/fail as data, including a beginner edge failure (proposal: correctness).
Run from the project root; each solution is copied into a fresh temp dir as
`solution.py` (the LLM representative is `llm/sample_1`).
```bash
for s in beginner expert llm/sample_1; do echo "==== $s ===="; tmp=$(mktemp -d); cp dataset/tasks/max_subarray/solutions/$s.py "$tmp/solution.py"; cp dataset/tasks/max_subarray/tests/test_solution.py "$tmp/"; PYTHONPATH="$tmp" .venv/bin/python -m pytest -q "$tmp"; done
```
Capture: expert/llm green, beginner failing the all-negative / empty edge tests.

### 05 — radon metrics on a sample (beginner vs expert)
Shows complexity, maintainability, Halstead (proposal: metrics; McCabe's
cyclomatic complexity).
```bash
echo "### beginner ###"; .venv/bin/radon cc dataset/tasks/max_subarray/solutions/beginner.py -s; .venv/bin/radon mi dataset/tasks/max_subarray/solutions/beginner.py -s
echo "### expert ###";   .venv/bin/radon cc dataset/tasks/max_subarray/solutions/expert.py -s;   .venv/bin/radon mi dataset/tasks/max_subarray/solutions/expert.py -s
```
Capture: the complexity ranks and MI for both (expert better than beginner).

### 06 — pylint on a sample beginner (style score)
Shows a beginner losing style points (proposal: standards/style).
```bash
.venv/bin/pylint dataset/tasks/count_vowels/solutions/beginner.py --disable=C0114,C0115,C0116 --score=y
```
Capture: the issues list and the "rated at X/10" line (this beginner scores ~5/10).

### 07 — bandit security scan on a sample beginner
Shows a real security finding in beginner code (proposal: security).
```bash
.venv/bin/bandit -r dataset/tasks/two_sum/solutions/beginner.py
```
Capture: the `B101 assert_used` (or for `word_frequency`, `B110 try_except_pass`)
finding. Compare with the expert, which is clean:
```bash
.venv/bin/bandit -r dataset/tasks/two_sum/solutions/expert.py
```

### 08 — Full pipeline, end to end
The single command that runs everything (proposal: the tool).
```bash
.venv/bin/python run_analysis.py
```
Capture: the stage banners (1/6 … 6/6) and the final **RESULTS SUMMARY** block.

### 09 — Results table (computed metrics)
Shows the tidy per-(task × source) metrics table (proposal: Results).
```bash
.venv/bin/python -c "import pandas as pd; pd.set_option('display.width',200); pd.set_option('display.max_columns',30); print(pd.read_csv('outputs/metrics.csv')[['task_id','difficulty','source','sample','mean_cc','mi','sloc','pylint_score','bandit_total','functional_pass','tests_passed','tests_total']].to_string(index=False))"
```
Capture: the table (or open `outputs/metrics.csv` in a spreadsheet).

### 10 — Statistical results
Shows Kruskal-Wallis, pairwise Mann-Whitney + Cliff's delta, pass rates
(proposal: statistical analysis).
```bash
sed -n '1,60p' outputs/stats.md
```
Capture: the per-metric medians + KW table, and the functional pass-rate table.

### 11 — Figures
Shows the visualisations (proposal: Results / charts). Open each PNG:
```bash
xdg-open figures/box_mean_cc.png
xdg-open figures/box_mi.png
xdg-open figures/box_halstead_volume.png
xdg-open figures/box_sloc.png
xdg-open figures/box_pylint_score.png
xdg-open figures/box_bandit_total.png
xdg-open figures/passrate_by_difficulty.png
xdg-open figures/radar_overall.png
```
Capture: each chart (they are grayscale + hatched, so they print cleanly in B/W).

### 12 — The generated report
Shows the final auto-written report (proposal: deliverable).
```bash
xdg-open report/report.html
```
Capture: the title block, the Results median table, the Statistical Analysis
tables, the RQ1–RQ4 findings, and the References list. (`report/report.docx` is
the Word version; `report/report.md` the Markdown source.)

### 13 — Framework unit tests pass
Shows the tool's own tests are green (proposal: rigour / reproducibility).
```bash
.venv/bin/python -m pytest tests/ -v
```
Capture: all tests passing.

### 14 — Interactive web dashboard (GUI)
Shows the project as a live web app (advanced deliverable).
```bash
xdg-open report/dashboard.html          # offline, self-contained
# or serve it live (stdlib only):  python -m src.webapp serve   → http://localhost:8000
```
Capture: the **Overview** tab (KPI cards + radar), then click through **Metrics
Explorer**, **Statistics**, **Figures**, **Code Browser** (three styles side by
side with each solution's metrics), and **Findings**.

### 15 — Auto-captured screenshots (two folders)
The repo ships ready-made captures, separated by kind:

- **`screenshots/code/`** — beginner/llm/expert source side by side per task
  (`is_palindrome.png`, `two_sum.png`, `dijkstra.png`, …) → "proper code" shots.
- **`screenshots/gui/`** — dashboard output views (`01_overview.png` …
  `06_findings.png`).

Regenerate with headless Chromium (see `screenshots/README.md`):
```bash
python tools/capture_screenshots.py             # both    (make screenshots)
python tools/capture_screenshots.py --only code # code shots only
python tools/capture_screenshots.py --only gui  # GUI shots only
```
The `code/` images drop into the report's code/Appendix sections; the `gui/`
images into Results.

---

## Where the raw evidence lives

Every external tool call is saved verbatim under `evidence/` (e.g.
`evidence/two_sum__beginner_bandit.json`, `evidence/run.log`). These back up the
numbers in the report and are useful as appendix evidence.
