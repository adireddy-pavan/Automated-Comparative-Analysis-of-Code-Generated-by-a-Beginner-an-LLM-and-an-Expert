# Change Log

This file records revisions made to the artefact, together with the test runs
used to verify them.

## Status of the original development period

The submitted archive contains no version-control metadata and no change record
covering the original development period, so this file carries no entries for
that work. Nothing here has been backdated or reconstructed.

No historical Git log or supervisory timeline was included. No earlier
iteration or supervisor feedback has been retrospectively invented.

## Revisions

Each entry names the issue, the decision taken, the change made, the test
command rerun, and the observed result, so that it can be checked against the
repository history and the regenerated outputs.

| Date | Issue | Decision | Change | Test rerun | Result |
|---|---|---|---|---|---|
| 2026-10-15 | Independent-group inference on same tasks | Use paired design | Friedman, Wilcoxon, rank-biserial, Cochran Q, exact McNemar | Archived `outputs/metrics.csv` -> `src.statistics_engine.run_statistics` | Matched statistics generated; end-to-end rerun not verified |
| 2026-10-15 | Generation-visible test cases | Add separately labelled post-generation supplementary cases | `supplementary/cases.json` and `tools/run_supplementary_tests.py` | `python tools/run_supplementary_tests.py` | Completed 210/210 executions; pass-all solutions: beginner 15/30, LLM 150/150, expert 30/30; cases are post-hoc, not blind |
| 2026-10-15 | Report/provenance overclaims | Qualify statistical and reproducibility claims | README, provenance, dissertation revision | Manual consistency audit | Original generation model/date not independently authenticated |


## Verification commands

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/
.venv/bin/python run_analysis.py
```

Running the pipeline regenerates `outputs/`, `figures/` and `report/`; the raw
output of every external tool call is written to `evidence/`.

## Current review-environment verification (2026-10-15)

- Regenerated `outputs/stats.json` and `outputs/stats.md` from the unaltered metrics CSV.
- Added and executed 80 post-generation cases over 210 archived solutions;
  all runner processes returned valid results; see `supplementary/results.json`.
- Framework: 28 tests passed with the metric extractor integration test
  deselected. The integration test needs Radon/Pylint/Bandit binaries, which
  are not installed in the review environment; it has **not** passed here.
- The original Radon/Pylint/Bandit/pytest pipeline was **not** rerun end-to-end
  because dependencies are unavailable. No existing raw static evidence was
  overwritten.
- No claim of passing full CI or publishing a changed online GitHub repository.

## Further corrections performed on 2026-10-15 (current revision, not original development)

| Date | Issue | Change | Verification | Limitation |
|---|---|---|---|---|
| 2026-10-15 | Constructed-human baseline evidence overstated | Added all-60 AST structural audit, honest reviewer form and dissertation construct-validity warning | `python tools/audit_baselines.py`; 60/60 parsed, hashes stored; 30/30 framework tests not needing static tools passed | Automated descriptors do not authenticate skill labels |
| 2026-10-15 | Tool-generated report and documentation overclaim model provenance | Qualified statements in README, provenance, generated reports, dashboard, abstract and results | Cross-file terms inspected; 64-page DOCX rendered | Original provider transactions unavailable |
| 2026-10-15 | Runner might mis-score a nonzero pytest exit with a misleading passing summary | `functional_pass` now requires pytest exit code 0; nonstandard exit records reason | Framework tests and compile checks passed | No fresh all-210 archived pytest completion claimed |
| 2026-10-15 | Stale Table of Contents, figure/table pages and incomplete screencast | Refreshed displayed page references; retained student-completion marker | Rendered 64 pages for visual review | Signature, genuine screencast, original supervisory commits still absent |
| 2026-10-15 | Full static rerun not independently executable in current environment | Added a full environment manifest and explicit preflight evidence | `python run_analysis.py --skip-figures --skip-report` exited 3, identifying missing Radon/Pylint/Bandit | Full end-to-end pipeline remains unverified |

Imported-archive comparison commits, if present, are newly created change-audit commits **not** historic student development commits.

## Further evidence-based review (2026-10-15 UTC / 2026-10-16 IST)

| Issue / evidence gap | Genuine corrective change | Executed verification | Remaining limitation |
|---|---|---|---|
| Archive traceability was asserted without machine-checked source/evidence coverage | Added `tools/audit_repro_evidence.py` and two regression checks; checks task/source/sample uniqueness, source SHA-256 and all 1,680 expected task-level raw evidence files | `python tools/audit_repro_evidence.py`: PASS, 30 tasks/210 rows/0 missing expected evidence; `pytest -q tests/ -k 'not test_metric_extraction_on_sample'`: 33 passed | Verifies archived data structure, not fresh Radon/Pylint/Bandit execution or statistical construct validity |
| Blind human-baseline review and external tests not ready to commission | Added unlabelled 60-stimulus `verification/independent_review_preparation/REVIEWER_PACKET/`, private coding key, empty reviewer form, and spec-only `verification/external_test_author_packet.zip` | Packet-generation tools executed; all 60 anonymous stimuli prepared; 30 task specs included | No actual reviewers, human-authored novice/expert solutions, externally written tests, or prospective model samples collected |
| `verify.sh` could report completion despite failed pip install/tests | Replaced permissive script with fail-fast gated install, framework tests, quality gates, end-to-end pipeline and explicit PASS/FAIL status record | `bash -n verify.sh`: PASS; dry preflight `python run_analysis.py --skip-figures --skip-report`: EXIT 3 (missing Radon, Pylint, Bandit) | Clean full pipeline still requires tool installation on a connected/appropriately isolated computer |
| Earlier original-test repeat attempt was incomplete | Preserved the original partial log and recorded the later attempt without calling it a successful rerun | Two attempts reached 60/210 before execution window stopped | No 210/210 original-suite rerun evidence is claimed |
| Dissertation still needed audit-method provenance and reviewer-readiness linkage | Qualified methodology, Chapter 4 and Appendix B/C; generated separate verification/action and prospective protocol documents | Document rendered and visually checked (64 dissertation pages and 2 pages each for verification and protocol) | Student-signed declaration, actual screencast, authentic provider logs and original Git history still missing |

Current generated audit commits reflect new review corrections only. They do not evidence the original student development timeline. No retrospective human-participant results or hidden test scores were manufactured.

## 2026-10-16 — Fresh visible-test replication and provenance audit (assistant-assisted review)

- **Issue:** the archived functional pass rates were not independently rerun over all 210 submitted implementations.
  **Change:** executed `tools/verify_archived_tests.py` on the archived task tests in fresh subprocesses; saved per-sample exit codes, SHA-256 code fingerprints and mismatch comparison in `verification/fresh_visible_test_rerun.csv` and `_summary.json`.
  **Retest:** 210 completed, 193 passed and 17 expected beginner-style failures; 0 runner errors and 0 mismatches to the original dataset. Not blind validation.
- **Issue:** archived code source identity and the claimed model provider were conflated.
  **Change:** added `tools/provenance_inventory.py` and regression tests; recorded complete byte-level source manifests. Explicitly marked original model identity, date and sample independence as **unverified**.
- **Issue:** a new authenticated model experiment lacked a safe receipt-collection pathway.
  **Change:** added opt-in `tools/collect_new_model_evidence.py` that writes provider response receipts for **new** calls into a separate folder; dry-run tested, no new API requests made.
- **Issue:** unavailable package installation prevented a complete fresh static analysis.
  **Change:** added GitHub Actions workflow `.github/workflows/independent-full-verification.yml` to install packages and run framework tests, Radon/Pylint/Bandit and all 210 tasks, then publish run logs. **Workflow not triggered or remotely verified in this review.**
- **Local verification:** 38 applicable framework tests passed. The external analysis-tool integration remains unverified; preflight correctly exited 3 on unavailable Radon, Pylint and Bandit.
- **Integrity:** no original model-response receipts, external participant ratings or historical student commits were fabricated. The review commits and test executions represent new current-dated corrections only.

### 2026-10-16 — AI-assisted verification acceptance hardening (new review work, not historical student development)

- **Issue:** The post-run checker previously asserted file presence and functional parity but did not expose static-metric drift. **Change:** `tools/windows_review_summary.py` now tabulates field-level numeric drift with concrete samples and flags when the dissertation must be reconciled. **Retest:** `test_windows_comparison_detects_numeric_static_drift_without_faking_failure` passed for both identical and intentionally modified CSVs.
- **Issue:** An arbitrary `WINDOWS_STATUS.json` with a PASS string could be counted as evidence. **Change:** `tools/evidence_completion_status.py` requires an actual set of successful steps plus a matching post-run comparison output. **Retest:** `test_technical_pass_cannot_be_faked_by_status_only` passed.
- **Issue:** Archived statistics needed a separate independent check. **Change:** `tools/archive_scientific_crosscheck.py` recalculates five Friedman statistics directly from source CSV, checks archived outputs, and runs before/after the fresh pipeline when possible. **Retest:** `tests/test_professor_acceptance.py` contains positive and negative checks; `verification/archived_scientific_crosscheck.json` confirms only archived-data agreement.
- **Issue:** Missing/invalid external research evidence could be misinterpreted as completed. **Change:** Reviewer/test manifest validators reject malformed future dates, unzoned test freeze dates and obvious attestation placeholders; no third-party evidence is constructed. **Retest:** 50 applicable framework tests pass, one Radon/Pylint/Bandit integration test remains unavailable in this environment (logs under `verification/professor_audit/`).

This entry documents current AI-assisted technical review only. Git author metadata does not establish student authorship or original development-period work. No supervisor-era history was manufactured.
