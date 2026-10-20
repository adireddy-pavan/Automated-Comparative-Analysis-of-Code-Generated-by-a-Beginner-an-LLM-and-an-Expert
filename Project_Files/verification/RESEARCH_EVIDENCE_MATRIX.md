# Research evidence matrix — 16 October 2026

## Verified in the current review

| Item | Actual evidence | Status and meaning |
|---|---|---|
| Archived benchmark | `verification/archived_integrity_audit.json` | 30 tasks, 210 indexed records and 1,680 expected evidence file checks present; byte/presence verification, not fresh static scoring |
| Fresh archived visible-test rerun | `verification/fresh_visible_test_rerun.csv` and `_summary.json` | 210/210 executed; 193 passing and 17 expected solution failures; 0 runner errors; 0 mismatches vs old archived pass/fail |
| Model-labelled code identity | `verification/provenance_inventory.json` | 210 per-source code-file SHA-256 fingerprints and duplicate checks; original model provider **NOT** authenticated |
| Framework tests | `verification/2026-10-16_framework_available_tests.log` | 38 tests passed locally; static-tool integration test deselected because required packages are missing |
| Strict pipeline preflight | `verification/2026-10-16_preflight.log` and `.exit` | Exit 3, correctly rejects unavailable Radon, Pylint and Bandit; no false "full rerun passed" claim |
| Programmatic matched-statistics correction | `outputs/stats.json`, `src/statistics_engine.py` | Calculated from archived measurements, not freshly extracted static metrics |
| External reviewer and spec-only author kits | `verification/INDEPENDENT_REVIEW_FORM.md`, `verification/external_test_author_packet.zip` | Materials ONLY; no external ratings or externally generated holdout cases returned |

## Independent-source evidence that **does not exist in the supplied archive**

- Original Anthropic/model provider response ID, exact returned model ID, authenticated original generation timestamp and provider API response body for 150 archived samples. The 2026 provenance statement is **self-reported**.
- Verified novice and experienced programmer participant samples, or blinded reviewers' completed classifications/ratings of the constructed baseline set.
- Independently authored and frozen holdout tests that had never been exposed to the evaluated authors or investigator prior to collection. The 80 supplementary cases are retrospective.
- Remote CI execution proof for `.github/workflows/independent-full-verification.yml`. Adding a workflow is not the same as running it.

## Unblocked follow-through

1. The student or authorised maintainer must push the revised project to GitHub; trigger the verification workflow on a connected runner; archive the resulting run URL, immutable commit SHA, Python/package inventory, fresh evidence and pass/fail results. Ensure the historical original metrics file is preserved for comparison.
2. Ask an external test author to generate and hash a genuinely independent set of tests using **only** `verification/external_test_author_packet.zip`. The test author must record their identity, test freeze date, task-clarification decisions, oracle review and non-access to source programs. For old archived solutions this is post-generation external evaluation, NOT prospective sample generation.
3. Have a different independent reviewer score the constructed beginner/expert baselines from the unlabelled packet, using a rubric and dated signed record. These ratings are additional construct-validation, not real-human programming observations.
4. For strong human-versus-model claims, recruit actual novice and experienced programmers prospectively with consent/ethics approval where needed. Pre-register tasks, disclosure, exclusion criteria and independent hidden tests.
5. For authentic new model output, run `python tools/collect_new_model_evidence.py --task is_palindrome --model EXACT_MODEL_FROM_PROVIDER --samples 5 --execute` with your own API credential. This creates **new** provider receipts in `prospective_model_runs/` and NEVER authenticates the original 150 files.
6. Complete student signature/date, actual screencast and supervisor resubmission rules. Do not manufacture these materials.

**Academic interpretation:** The original study remains a constructed-benchmark comparison with visible tests, a self-reported LLM source and retroactive supplementary checks. The current rerun establishes repeatability of the archived *functional* evaluation only, not population-level novice/expert generalisation or model-origin authentication.
