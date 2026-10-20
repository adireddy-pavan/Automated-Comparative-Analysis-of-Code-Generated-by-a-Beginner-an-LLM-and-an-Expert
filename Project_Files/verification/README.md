# Scientific verification evidence and its limits

- `baseline_structural_audit.csv` / `baseline_audit_summary.json`: reproducible structural descriptors for all 60 **constructed** reference files. NOT human validation or external expert assessment.
- `INDEPENDENT_REVIEW_FORM.md`: blank future reviewer protocol. NOT evidence that the review occurred.
- `framework_tests.log`: observed local tests in this revision. Any skipped test is disclosed.
- `preflight.log`: whether required Radon/Pylint/Bandit binaries were present. This review environment has no network access to install absent dependencies.
- `python_environment.json`: current runtime package versions; NOT the archival pipeline version record.
- Original archived `evidence/` files and 210-row `outputs/metrics.csv` are preserved. Recomputed stats do not constitute a new raw metric extraction.
- `supplementary/`: exploratory post-generation checks, NOT independent prospective held-out tests.

Remaining student/external steps: original Git history; supervisor confirmation; authenticated model generation events; truly blinded external task and baseline review; full offline-container rerun with locked dependencies; signed declaration and screencast.

- `INCOMPLETE_original_test_rerun_attempt.log` is only a progress log. The 210-row original-test rerun exceeded the execution window before results were saved. It is NOT a successful rerun and should not be cited as one.

## Added integrity and future-review readiness (2026-10-15 UTC)

- `archived_integrity_audit.json`: PASS on archive inventory (30 tasks; 210 unique solutions and matching metric rows; 1,680/1,680 expected evidence file names present). Source SHA-256 hashes are included. This is NOT independently regenerated metric data.
- `independent_review_preparation/REVIEWER_PACKET`: 60 constructed examples with no beginner/expert labels and a blank rating sheet. Keep `PRIVATE_KEY_DO_NOT_SEND_TO_RATERS.csv` outside the reviewer packet. No external review has occurred.
- `external_test_author_packet.zip`: specification-only 30-task packet for future independent test author. It includes NO prior code/tests. No external author has submitted tests.
- `framework_tests_excluding_missing_tools.log`: 33 non-tool-dependent tests pass. `test_metric_extraction_on_sample` fails solely because required analyzers are not present in this runtime and was excluded from the 33-pass run.
- `original_tests_complete_attempt_2026-10-16.log`: despite its filename, this is a timed-out incomplete run, NOT a successful original-suite replication; it reached 60/210 before execution stopped.
- `verify.sh` (project root): stops on failure and produces an explicit PASS/FAIL status only after completing every stage. The current environment cannot produce a successful full verification due to missing external dependencies and blocked package download.
