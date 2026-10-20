#!/usr/bin/env python3
"""Freshly rerun each archived task pytest without overwriting original evidence.

THIS DOES NOT run static tooling, authenticate generation, or prove unseen-test
accuracy. Use only trusted samples or an externally sandboxed runtime.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'verification'

def run_one(arg):
    task,source,sample,solution,test = arg
    with tempfile.TemporaryDirectory(prefix='audit_pytest_') as tmp:
        shutil.copyfile(solution,Path(tmp)/'solution.py')
        shutil.copyfile(test,Path(tmp)/'test_solution.py')
        env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=tmp)
        try:
            result=subprocess.run([sys.executable,'-m','pytest','-q','--tb=no','-p','no:cacheprovider','.'],cwd=tmp,
                capture_output=True,text=True,env=env,timeout=35,check=False)
            stdout=result.stdout+'\n'+result.stderr
            passed=sum(int(x) for x in re.findall(r'(\d+) passed',stdout))
            failed=sum(int(x) for x in re.findall(r'(\d+) failed',stdout))
            errors=sum(int(x) for x in re.findall(r'(\d+) errors?',stdout))
            skipped=sum(int(x) for x in re.findall(r'(\d+) skipped',stdout))
            status='passed' if result.returncode==0 and passed>0 and not (failed+errors+skipped) else 'failed' if result.returncode==1 and (failed+errors)>0 else 'runner_error'
            snippet=' | '.join(stdout.splitlines()[-5:])[-360:]
            exitcode=result.returncode
        except subprocess.TimeoutExpired:
            status='timeout';passed=failed=errors=skipped=0;exitcode=124;snippet='timeout 35 seconds'
    return {'task_id':task,'source':source,'sample':sample,'status':status,'passed_count':passed,'failed_count':failed,'error_count':errors,'skipped_count':skipped,'exit_code':exitcode,
            'source_sha256':hashlib.sha256(solution.read_bytes()).hexdigest(),'output_tail':snippet}

def main():
    args=[]
    for task in sorted((ROOT/'dataset/tasks').iterdir()):
        if not task.is_dir():continue
        t=task.name
        for source in ['beginner','llm','expert']:
            for sample in range(1,6 if source=='llm' else 2):
                sol=task/'solutions'/source/f'sample_{sample}.py' if source=='llm' else task/'solutions'/f'{source}.py'
                args.append((t,source,sample,sol,task/'tests/test_solution.py'))
    DEST.mkdir(exist_ok=True)
    start=time.monotonic()
    rows=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(run_one,x) for x in args]
        for i,future in enumerate(as_completed(futures),1):
            rows.append(future.result())
            if i%30==0:print(f'Completed {i}/210',flush=True)
    rows.sort(key=lambda r:(r['task_id'],r['source'],r['sample']))
    with (DEST/'fresh_visible_test_rerun.csv').open('w',newline='',encoding='utf-8') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    import pandas as pd
    original=pd.read_csv(ROOT/'outputs/metrics.csv')
    mismatch=[]
    for row in rows:
        before=original[(original.task_id==row['task_id'])&(original.source==row['source'])&(original['sample']==row['sample'])]
        if len(before)!=1 or bool(before.iloc[0]['functional_pass'])!=(row['status']=='passed'):
            mismatch.append(f"{row['task_id']} {row['source']} s{row['sample']}")
    summary={'experiment':'Fresh rerun of ARCHIVED GENERATION-VISIBLE tests only',
             'n':len(rows),'passed':sum(r['status']=='passed' for r in rows),
             'failed_as_test_data':sum(r['status']=='failed' for r in rows),
             'runner_errors':sum(r['status'] not in ('passed','failed') for r in rows),
             'archived_outcome_mismatches':mismatch,'seconds':round(time.monotonic()-start,1),
             'not_tested':['Radon','Pylint','Bandit','model generation identity','independent held-out tests']}
    (DEST/'fresh_visible_test_rerun_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return 1 if mismatch or summary['runner_errors'] else 0
if __name__=='__main__':raise SystemExit(main())
