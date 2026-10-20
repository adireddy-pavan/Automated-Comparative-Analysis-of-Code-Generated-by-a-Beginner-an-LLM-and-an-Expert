#!/usr/bin/env python3
"""Check and optionally execute externally authored JSON test cases.

Cases must be provided/frozen by a genuine independent author. This tool
never generates or pretends to authenticate such cases. Evaluated code runs in
child Python processes with timeouts, NOT a security sandbox: use a disposable,
network-disabled VM for untrusted code.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'verification' / 'external_results' / 'independent_tests'
TASK_ROOT = ROOT / 'dataset' / 'tasks'
SRC = ('beginner', 'llm', 'expert')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> tuple[dict, dict | None]:
    cases_path, manifest_path = DIR / 'cases.json', DIR / 'frozen_manifest.json'
    report = {'status':'PENDING', 'errors':[], 'cases_sha256':None, 'manifest':None,
              'limitations':['Presence and hashes do not independently prove authorship, ethics approval, or blindness.',
                             'Post-generation frozen tests of archived code are not prospective generation.',
                             'The execution subprocess does NOT sandbox arbitrary malicious programs.']}
    if not cases_path.exists() or not manifest_path.exists():
        report['errors'].append('Missing independently supplied cases.json or frozen_manifest.json')
        return report, None
    try:
        cases = json.loads(cases_path.read_text(encoding='utf-8'))
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        report['errors'].append(f'Cannot read the submitted files: {exc}')
        return report, None
    report['cases_sha256'] = sha(cases_path)
    report['manifest'] = manifest
    if manifest.get('cases_sha256') != report['cases_sha256']:
        report['errors'].append('Frozen manifest hash does not match cases.json')
    for field in ('test_author_identifier', 'frozen_at_utc', 'specifications_only_attestation', 'independent_oracle_review_notes'):
        if not str(manifest.get(field, '')).strip():
            report['errors'].append(f'Missing frozen manifest field: {field}')
    if str(manifest.get('specifications_only_attestation', '')).strip().lower() not in ('yes', 'true', 'i confirm'):
        report['errors'].append('specifications_only_attestation must explicitly confirm YES')
    if manifest.get('frozen_at_utc'):
        try:
            frozen = datetime.fromisoformat(str(manifest['frozen_at_utc']).replace('Z', '+00:00'))
            if frozen.tzinfo is None:
                raise ValueError('timezone offset is required')
            if frozen.astimezone(timezone.utc) > datetime.now(timezone.utc):
                raise ValueError('freeze date cannot be in the future')
        except ValueError as exc:
            report['errors'].append(f'Invalid frozen_at_utc: {exc}')
    tasks = {p.name for p in TASK_ROOT.iterdir() if p.is_dir()}
    if not isinstance(cases, dict) or set(cases) != tasks:
        report['errors'].append('Expected test cases for exactly all 30 known task IDs')
        return report, None
    ncases = 0
    for task, items in cases.items():
        if not isinstance(items, list) or not items:
            report['errors'].append(f'{task}: empty test list')
            continue
        for index, item in enumerate(items, 1):
            if not isinstance(item, dict) or not isinstance(item.get('args'), list) or 'expected' not in item:
                report['errors'].append(f'{task} case {index}: expected args list and expected value')
            ncases += 1
    report['task_count'], report['case_count'] = len(cases), ncases
    report['status'] = 'READY_FOR_EXECUTION_UNVERIFIED_AUTHORSHIP' if not report['errors'] else 'INVALID_EXTERNAL_INPUT'
    return report, cases


def run(cases: dict) -> dict:
    # Reuse the reviewed isolated JSON function-call protocol without modifying
    # the original retrospective cases or outcomes.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.run_supplementary_tests import CHILD, _quota
    from subprocess import TimeoutExpired
    results = []
    for pos, (task, task_cases) in enumerate(sorted(cases.items()), 1):
        print(f'External case evaluation {pos}/30: {task}', flush=True)
        meta = json.loads((TASK_ROOT / task / 'meta.json').read_text(encoding='utf-8'))
        for source in SRC:
            paths = ([TASK_ROOT / task / 'solutions' / source / f'sample_{i}.py' for i in range(1, 6)]
                     if source == 'llm' else [TASK_ROOT / task / 'solutions' / f'{source}.py'])
            for sample, path in enumerate(paths, 1):
                with tempfile.TemporaryDirectory(prefix='tharun_external_') as location:
                    (Path(location)/'solution.py').write_bytes(path.read_bytes())
                    try:
                        proc = subprocess.run([sys.executable, '-I', '-c', CHILD],
                            input=json.dumps({'entry_point':meta['entry_point'], 'cases':task_cases}),
                            capture_output=True, text=True, cwd=location, timeout=8, check=False,
                            env={'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE':'1'},
                            preexec_fn=_quota if os.name == 'posix' else None)
                        matches = [ln[len('RESULT_JSON:'):] for ln in proc.stdout.splitlines() if ln.startswith('RESULT_JSON:')]
                        details = json.loads(matches[-1]) if matches else []
                        ok = proc.returncode == 0 and len(details) == len(task_cases)
                        status = 'executed' if ok else 'runner_error'
                        error = '' if ok else (proc.stderr or proc.stdout)[-300:]
                    except (TimeoutExpired, ValueError, json.JSONDecodeError) as exc:
                        details, status, error = [], 'runner_error', str(exc)[:300]
                n_passed = sum(bool(c.get('passed')) for c in details)
                results.append({'task_id':task, 'source':source, 'sample':sample,
                    'source_sha256':sha(path), 'test_count':len(task_cases),
                    'tests_passed':n_passed, 'all_pass': status == 'executed' and n_passed == len(task_cases),
                    'runner_status':status,'error':error, 'details':details})
    errors = [r for r in results if r['runner_status'] != 'executed']
    return {'rows':results, 'runner_errors':len(errors),
        'passes_by_source': {s: {'passed':sum(r['all_pass'] for r in results if r['source']==s),
                                'total':sum(r['source']==s for r in results)} for s in SRC},
        'status':'COMPLETE_WITHOUT_RUNNER_ERRORS' if not errors else 'INCOMPLETE_RUNNER_ERRORS'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', help='Actually execute source code; use trusted isolation')
    args = parser.parse_args()
    report, cases = check()
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR/'external_input_validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if report['status'] != 'READY_FOR_EXECUTION_UNVERIFIED_AUTHORSHIP':
        print(json.dumps(report, indent=2))
        return 2 if args.execute else 0
    if not args.execute:
        print('Submitted case file is well-formed and hash-matched. NOT EXECUTED. Original authorship not authenticated.')
        return 0
    time = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    out = DIR / 'executed_results' / time
    out.mkdir(parents=True, exist_ok=False)
    evaluated = run(cases)
    payload = {'executed_at_utc':datetime.now(timezone.utc).isoformat(),
               'source_input_hash_sha256':report['cases_sha256'],
               'provenance':'Externally supplied cases, independently authored status not machine authenticated',
               'evaluation':evaluated}
    (out/'external_results.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (out/'external_results.csv').open('w', newline='', encoding='utf-8') as file:
        columns = ['task_id','source','sample','source_sha256','test_count','tests_passed','all_pass','runner_status','error']
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows({col:r.get(col) for col in columns} for r in evaluated['rows'])
    print(f"External cases evaluated: {len(evaluated['rows'])} implementations; {evaluated['runner_errors']} runner errors; saved to {out}")
    return 1 if evaluated['runner_errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
