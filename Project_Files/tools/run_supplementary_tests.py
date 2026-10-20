#!/usr/bin/env python3
"""Post-generation, task-matched specification sensitivity tests.

This CLI does not assert historical test blindness or security sandboxing.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASK_ROOT = ROOT / 'dataset' / 'tasks'
CASES = ROOT / 'supplementary' / 'cases.json'
RESULTS = ROOT / 'supplementary' / 'results.json'
SOURCES = ('beginner', 'llm', 'expert')

CHILD = r'''
import importlib.util, json, math, sys, traceback
from pathlib import Path
req=json.loads(sys.stdin.read())
try:
    spec=importlib.util.spec_from_file_location('isolated_solution',str(Path('solution.py').resolve()))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func=getattr(module,req['entry_point'])
    detail=[]
    for case in req['cases']:
        try:
            value=func(*case['args'])
            normal=json.loads(json.dumps(value,allow_nan=True))
            expected=case['expected']
            ok=(normal==expected)
            detail.append({'passed':bool(ok),'observed':normal if not ok else None})
        except Exception as ex:
            detail.append({'passed':False,'exception':type(ex).__name__, 'message':str(ex)[:160]})
    print('RESULT_JSON:'+json.dumps(detail,allow_nan=True))
except BaseException as exc:
    print('RESULT_ERROR:'+type(exc).__name__+':'+str(exc)[:180])
'''


def _quota():
    """Best-effort resource quota for POSIX; not a sandbox."""
    if os.name == 'posix':
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(3,4))
        resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
        resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024*1024,8*1024*1024))


def main():
    all_cases=json.loads(CASES.read_text(encoding='utf-8'))
    records=[]
    for task_index, (task, tests) in enumerate(sorted(all_cases.items()), 1):
        print(f"Checking {task_index}/30: {task}",flush=True)
        meta=json.loads((TASK_ROOT/task/'meta.json').read_text(encoding='utf-8'))
        for source in SOURCES:
            paths=([TASK_ROOT/task/'solutions'/source/f'sample_{n}.py' for n in range(1,6)]
                   if source=='llm' else [TASK_ROOT/task/'solutions'/f'{source}.py'])
            for num, path in enumerate(paths,1):
                with tempfile.TemporaryDirectory(prefix='tharun_posthoc_') as temp:
                    code=path.read_bytes()
                    (Path(temp)/'solution.py').write_bytes(code)
                    cmd=[sys.executable,'-I','-c',CHILD]
                    payload=json.dumps({'entry_point':meta['entry_point'],'cases':tests})
                    try:
                        process=subprocess.run(cmd,input=payload,stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,text=True,cwd=temp,timeout=4,
                            env={'PATH':os.environ.get('PATH',''),'PYTHONDONTWRITEBYTECODE':'1'},
                            preexec_fn=_quota if os.name=='posix' else None,check=False)
                        marker=[x.partition('RESULT_JSON:')[2] for x in process.stdout.splitlines()
                                if x.startswith('RESULT_JSON:')]
                        details=json.loads(marker[-1]) if marker else []
                        status='executed' if marker and len(details)==len(tests) else 'runner_error'
                        error='' if status=='executed' else (process.stderr or process.stdout)[-200:]
                    except subprocess.TimeoutExpired:
                        details=[];status='timeout';error='4-second process timeout'
                success=sum(bool(x.get('passed')) for x in details)
                records.append({'task_id':task,'source':source,'sample':num,
                    'tests_total':len(tests),'tests_passed':success,
                    'solution_passed':status=='executed' and success==len(tests),
                    'runner_status':status,'error':error,
                    'sha256':hashlib.sha256(code).hexdigest(),
                    'case_details':details})
    RESULTS.write_text(json.dumps({'date':'2026-10-15','test_design':'post-generation, not independently blinded',
                      'process_isolation':'separate subprocess with resource limits; not sandbox',
                      'rows':records},indent=2,ensure_ascii=False,allow_nan=True)+'\n',encoding='utf-8')
    with (RESULTS.parent/'results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['task_id','source','sample','tests_total',
            'tests_passed','solution_passed','runner_status','error','sha256'])
        writer.writeheader()
        for r in records: writer.writerow({k:r.get(k) for k in writer.fieldnames})
    for src in SOURCES:
        subs=[r for r in records if r['source']==src]
        print(f'{src}: {sum(r["solution_passed"] for r in subs)}/{len(subs)} solutions pass all post-generation cases')
    errs=[r for r in records if r['runner_status']!='executed']
    print('Runner issues:',len(errs),'of',len(records))
    return 1 if errs else 0

if __name__=='__main__':raise SystemExit(main())
