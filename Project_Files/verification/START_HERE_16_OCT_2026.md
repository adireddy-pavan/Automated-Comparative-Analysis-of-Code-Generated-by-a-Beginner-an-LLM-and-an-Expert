# THARUN — latest evidence-based revision — 16 October 2026

Read **Tharun_Independent_Verification_REPORT.docx** first, then the revised dissertation. The original benchmark measurements are preserved within `Project_Files/outputs/metrics.csv`.

## Actually completed on the review computer

- Freshly re-executed all 210 original, generation-visible functional tests in separate temporary subprocesses; 193 passes, 17 expected failing beginner-style solutions; zero runner errors; zero disagreements with archived outcomes. See `Project_Files/verification/fresh_visible_test_rerun.csv` and `_summary.json`.
- Rechecked all archived source file identities with SHA-256 across 210 sampled implementations. This authenticates file identity **only** — not the author or source model.
- Verified 30 tasks and all 1,680 expected archived per-sample evidence files.
- Passed **38 framework unit/regression tests**, excluding **one** test requiring Radon/Pylint/Bandit.
- Tried full pipeline; stopped correctly at preflight with exit 3 because Radon, Pylint and Bandit were unavailable and pip could not reach the package index.
- Prepared an additional GitHub Actions workflow that installs dependencies, executes the full pipeline and captures evidence. **It has NOT been triggered, so no remote success is claimed.**

## Four items still requiring authentic outside/student action

1. Connect a Python-capable machine or GitHub Actions to the package index, push the project and run `.github/workflows/independent-full-verification.yml` or `bash verify.sh`. Archive the actual successful run logs, artifact file hashes and immutable commit SHA.
2. Have a genuine independent expert review the unlabelled 60-source packet, and a different external author freeze hidden tests *from specs only*. The preparation kits are already provided. No reviewers have yet completed them; participant data requires applicable approvals.
3. Ask the original project author for genuine API response IDs/model receipts if any. Their absence cannot be cured from code hashes. The optional `tools/collect_new_model_evidence.py` records **future** provider responses separately, and must never be presented as authentication of earlier samples.
4. The student personally signs/dates the declaration, records a truthful screencast, updates the report URLs and checks the university's resubmission rules and actual reference sources.

## Useful commands

```
cd Project_Files
python tools/audit_repro_evidence.py
python tools/provenance_inventory.py
python -m pytest tests/ -q -k 'not metric_extraction_on_sample'
python tools/verify_archived_tests.py

# Requires installed Radon, Pylint and Bandit and all pip dependencies:
bash verify.sh
```

Use the actual results to revise the numerical analysis if a newer toolchain produces different static metrics; do not silently overwrite the original archive or claim a result that has not run. The revised dissertation is still an empirical study of a **constructed** benchmark with **generation-visible** original tests and **unverified historical model provenance**, not a controlled experiment recruiting genuine novice and expert programmers.
