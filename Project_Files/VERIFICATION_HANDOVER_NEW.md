# Tharun — updated verification handover (16 October 2026)

The goal is to create **verifiable research evidence**, not fabricate missing experiments or original history.

## A. Full Windows run — automatic
1. Unzip to a short folder, install Python 3.11 and ensure internet for pip.
2. In `Project_Files`, double-click `START_WINDOWS_RUN.cmd` (or inspect/run `RUN_WINDOWS_AND_SAVE.ps1`).
3. The script uses a separate workspace, installs requirements, runs the **complete** framework/static/pipeline suite, compares original/fresh CSV and reports, then runs additional evidence-status checks.
4. All results go into `verification/windows_runs/<timestamp>_<id>/`; the top-level `RESULTS_*.zip` is what the friend returns.
5. Only a real `WINDOWS_STATUS.json` with `status=PASS` and actual successful logs establishes a full local rerun. No such Windows run is present in the delivered archive.
6. If a stage fails, retain the failed ZIP and fix only the actual error. Old `outputs/` are not overwritten.

## B. Genuine iteration evidence
- `python tools/iteration_evidence_audit.py` outputs `verification/iteration_evidence_audit.json` from Git metadata and flags the inability to authenticate original student development history.
- Search the student's own Git remote and historical backups for real pre-existing changes and feedback records. Put genuine originals in `verification/external_results/development_history`.
- In Appendix B.3 link each authentic issue → commit/diff → failed test → fix → passing retest. Never rewrite or backdate commit history. Review-period commits do not prove original development activity.

## C. Independent reviewers (requires humans)
- Send ONLY `verification/independent_review_preparation/REVIEWER_PACKET` (not the parent directory or private key) to approved qualified reviewers.
- Each reviewer rates the 60 blinded candidates in `BLANK_RATING_FORM.csv`, includes `perceived_level` (beginner/expert/uncertain), and returns dated ratings and a completed attestation.
- Save their original files under `verification/external_results/reviewer_01/` and `/reviewer_02/` (one ratings CSV each, plus `REVIEWER_ATTESTATION.txt`).
- Run `python tools/external_evidence_review.py`. This validates formats, candidate hashes and calculates inter-rater agreement and class-label correspondence ONLY AFTER both forms exist. It does not certify reviewer identity/independence or turn constructed code into real human submissions.

## D. Independently authored tests (requires external author)
- Send ONLY `verification/external_test_author_packet.zip` to an independently appointed qualified test author.
- The author supplies `cases.json` and a genuine frozen `frozen_manifest.json`, with SHA-256 hash and a dated attestations BEFORE evaluating source code, following `verification/external_results/independent_tests/EXTERNAL_TEST_AUTHOR_INSTRUCTIONS.txt`.
- Place originals inside `verification/external_results/independent_tests`.
- Run `python tools/run_external_validation.py` to check structure/hash; then use a disposable **network-disabled VM/container** before running `python tools/run_external_validation.py --execute` because evaluated code is not securely sandboxed.
- This produces `executed_results/<timestamp>/external_results.json` and `.csv`, describing archived-code POST-generation testing. The original solutions and archived metrics are unchanged.

## E. Current status
- Run `python tools/evidence_completion_status.py` after adding new external evidence. Missing items remain PENDING, not PASS.
- Provider generation transaction receipts and actual human reviewer attestations must come from their original owners. They cannot be generated from the existing code or hashes.
- The student's own signature/declaration and screencast remain student tasks.
- Research findings in dissertation must be updated ONLY using completed checks and actual new data.

## The current revision does NOT assert 90+ and does not replace the university rubric.
