#!/usr/bin/env python3
"""Concise machine-readable evidence status; NEVER silently marks external tasks complete."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
VER = ROOT / 'verification'
EX = VER / 'external_results'


def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError): return {}


def main():
    review = load(VER/'external_review_analysis.json')
    test = load(EX/'independent_tests'/'external_input_validation.json')
    runs = sorted((VER/'windows_runs').glob('*/WINDOWS_STATUS.json')) if (VER/'windows_runs').is_dir() else []
    # A manually written 'status: PASS' is NOT sufficient. Require the dated
    # runner's step exit codes and its post-run comparison status too.
    expected_steps = {'02_install_requirements','08_all_framework_tests',
                      '09_pylint_quality_gate','10_bandit_quality_gate',
                      '11_complete_analysis','12_validate_new_outputs',
                      '12b_fresh_stats_independent_check'}
    def credible_technical_run(path):
        r = load(path)
        steps = r.get('steps',[])
        if r.get('status') != 'PASS' or not isinstance(steps,list):return False
        observed = {x.get('step') for x in steps if isinstance(x,dict) and x.get('exit_code') == 0}
        post = load(path.parent/'windows_review_summary.json')
        return expected_steps.issubset(observed) and post.get('status')=='PASS'
    successes = [p for p in runs if credible_technical_run(p)]
    checked_tests = sorted((EX/'independent_tests'/'executed_results').glob('*/external_results.json')) if (EX/'independent_tests'/'executed_results').is_dir() else []
    passed_external = [p for p in checked_tests if load(p).get('evaluation',{}).get('status')=='COMPLETE_WITHOUT_RUNNER_ERRORS']
    history = load(VER/'iteration_evidence_audit.json')
    historical = history.get('external_history_evidence_files', [])
    authentic_model_files = [p for p in (EX/'original_model_records').glob('*') if p.is_file() and not p.name.startswith('NOT_YET_COMPLETED')]
    statuses = {
        'complete_full_windows_pipeline': {'status':'PASS_TECHNICAL_ONLY' if successes else 'PENDING', 'successful_logs':[str(p.relative_to(ROOT)) for p in successes]},
        'reviewer_01_and_02_forms': {'status':review.get('status','PENDING')},
        'independently_authored_case_package': {'status':test.get('status','PENDING')},
        'independent_test_execution': {'status':'EXECUTED' if passed_external else 'PENDING', 'output_files':[str(p.relative_to(ROOT)) for p in passed_external]},
        'original_development_history':{'status':'PRESENT_REQUIRES_MANUAL_AUTHENTICATION' if historical else 'PENDING', 'files':historical},
        'original_model_provider_records':{'status':'PRESENT_REQUIRES_MANUAL_AUTHENTICATION' if authentic_model_files else 'PENDING'},
        'declaration_and_screencast':{'status':'STUDENT_ACTION_REQUIRED'},
    }
    out = {'generated_utc':datetime.now(timezone.utc).isoformat(),'checks':statuses,
      'warning':'A PASS reflects technical validation only; external independence, ethics and historical authorship require human verification. Missing evidence is NOT complete.'}
    (VER/'evidence_completion_status.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    for key,info in statuses.items(): print(f"{key}: {info['status']}")
    return 0

if __name__ == '__main__':raise SystemExit(main())
