# Screenshots

Ready-made evidence for the report, in three folders by kind. All are captured
offline with headless Chromium and trimmed to content.

## `code/` — source-code screenshots (30, one per task)
The three sources (**beginner / llm / expert**) side by side for each task, each
annotated with the static metrics it earned (LOC, complexity, MI, pylint, bandit,
pass/fail). The beginner and expert solutions are single authored references; the
LLM column shows a representative sample of the 5 genuine model samples per task.

- Introductory: `count_vowels`, `count_words`, `factorial`, `find_max`,
  `fizzbuzz`, `gcd`, `is_palindrome`, `reverse_string`, `sum_list`,
  `sum_of_digits`
- Intermediate: `binary_search`, `chunk_list`, `fibonacci`, `is_subsequence`,
  `roman_to_int`, `run_length_encode`, `second_largest`, `title_case`, `two_sum`,
  `valid_parentheses`
- Advanced: `caesar_cipher`, `coin_change`, `dijkstra`, `length_of_lis`,
  `longest_common_prefix`, `max_profit`, `max_subarray`, `merge_intervals`,
  `quicksort`, `word_frequency`

## `gui/` — dashboard / output screenshots (6)
- `01_overview.png` — KPI cards + radar chart
- `02_metrics.png` — sortable/filterable metrics table (all 210 rows)
- `03_statistics.png` — Kruskal–Wallis + pairwise tables
- `04_figures.png` — all charts
- `05_code_browser.png` — the code-browser tab
- `06_findings.png` — research-question findings + references

## `cli/` — terminal / command-line evidence (14)
Real command output rendered as terminal cards — maps to the proposal workflow:
- `01_project_structure.png` — repository layout
- `02_tool_versions.png` — Python/radon/pylint/bandit versions (reproducibility)
- `03_dataset_validation.png` — 30 tasks validated across 3 tiers
- `04_pipeline_summary.png` — full pipeline run + RESULTS SUMMARY
- `05_framework_tests.png` — pytest (all framework tests pass)
- `06_pylint_framework.png` — pylint **10.00/10**
- `07_bandit_framework.png` — bandit **clean**
- `08_radon_beginner_vs_expert.png` — complexity & MI compared
- `09_pylint_beginner_sample.png` — a beginner solution scoring lower
- `10_bandit_beginner_sample.png` — a real insecure pattern flagged in beginner code
- `11_metrics_table.png` — computed metrics table
- `12_statistics.png` — statistical results
- `13_security_signal.png` — bandit findings per source
- `14_quality_gates.png` — all gates green together

## Regenerate

```bash
make screenshots                              # everything (gui + code + cli)
python tools/capture_screenshots.py           # dashboard: gui + 30 code shots
python tools/capture_screenshots.py --only code
python tools/capture_terminal.py              # the 14 cli evidence shots
```
Needs Chromium installed; runs fully offline.
