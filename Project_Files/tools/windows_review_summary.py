#!/usr/bin/env python3
"""Post-run independent structural comparison for Windows handover.

Only verifies the recorded code metrics and output inventory; this does NOT
validate model authorship, human expertise, originality, or blinded testing.
"""
from __future__ import annotations
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = ROOT / 'verification'

def read_csv(path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def truthy(x):
    return str(x).strip().lower() in ('1', 'true', 'yes')

def main():
    errors = []
    old = VER / 'archived_metrics_before_run.csv'
    fresh = ROOT / 'outputs/metrics.csv'
    st = ROOT / 'outputs/stats.json'
    old_rows = read_csv(old) if old.is_file() else []
    fresh_rows = read_csv(fresh) if fresh.is_file() else []
    if len(old_rows) != 210: errors.append(f'Archived snapshot rows: {len(old_rows)}, expected 210')
    if len(fresh_rows) != 210: errors.append(f'Fresh metric rows: {len(fresh_rows)}, expected 210')
    def keyed(rows):
        return {(r['task_id'],r['source'],str(r['sample'])):r for r in rows}
    old_keys, new_keys = keyed(old_rows), keyed(fresh_rows)
    if len(old_keys) != len(old_rows): errors.append('Archived CSV contains duplicate task/source/sample keys')
    if len(new_keys) != len(fresh_rows): errors.append('Fresh CSV contains duplicate task/source/sample keys')
    if old_keys.keys() != new_keys.keys(): errors.append('Fresh vs archived sample keys differ')
    mismatch = []
    for key in sorted(old_keys.keys() & new_keys.keys()):
        if truthy(old_keys[key].get('functional_pass')) != truthy(new_keys[key].get('functional_pass')):
            mismatch.append(key)
    if mismatch: errors.append(f'Fresh vs archived functional result mismatches: {len(mismatch)}')
    bad = []
    for key,row in new_keys.items():
        if any(str(row.get(x,'')).strip().lower() in ('','none','nan','n/a')
               for x in ('mean_cc','mi','halstead_volume','pylint_score','bandit_total')):
            bad.append(key)
    if bad: errors.append(f'Empty static metrics in {len(bad)} solutions')
    expected_outputs = [
        'outputs/stats.json', 'outputs/stats.md', 'outputs/metrics.csv',
        'figures/matched_inference_summary.png', 'report/report.md',
        'report/report.html', 'report/report.docx', 'report/dashboard.html',
        'evidence/run.log',
    ]
    missing = [f for f in expected_outputs if not (ROOT/f).is_file()]
    if missing: errors.append('Required files missing: '+', '.join(missing))
    try:
        if 'metrics' not in json.loads(st.read_text(encoding='utf-8')):
            errors.append('stats.json lacks metrics section')
    except Exception as ex:
        errors.append('Cannot parse generated stats.json: '+repr(ex))
    # Distinguish reproducible functional outcomes from static-metric drift.
    # A drift is not automatically a defect: tool versions and scores can change.
    # It is never silently hidden from the dissertation reconciliation.
    numerical = ('mean_cc','max_cc','mi','halstead_volume','halstead_effort',
                 'loc','lloc','sloc','comments','pylint_score','pylint_issues',
                 'bandit_low','bandit_medium','bandit_high','bandit_total')
    changed = []
    for key in sorted(old_keys.keys() & new_keys.keys()):
        before, after = old_keys[key], new_keys[key]
        for metric in numerical:
            try:
                a, b = float(before[metric]), float(after[metric])
            except (ValueError, TypeError, KeyError):
                errors.append(f'{key}: numeric metric {metric} could not be parsed')
                continue
            if not all(map(__import__('math').isfinite, (a,b))):
                errors.append(f'{key}: nonfinite value for metric {metric}')
            elif abs(a-b)> max(0.002, abs(a)*1e-5):
                changed.append({'key':list(key),'metric':metric,'archived':a,'fresh':b,'delta':round(b-a,6)})
    # Static differences are explicitly disclosed, not treated as an automatic
    # pipeline failure when tool versions have changed. Manual reconciliation is needed.
    source_counts = Counter((r.get('source'),truthy(r.get('functional_pass'))) for r in fresh_rows)
    report = {
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'classification':'Fresh local Windows outputs compared to archived results; no independent author or provider authentication',
      'status':'PASS' if not errors else 'FAIL',
      'errors':errors,
      'archived_rows':len(old_rows),'fresh_rows':len(fresh_rows),
      'outcome_mismatch_count':len(mismatch),
      'outcome_mismatch_examples':mismatch[:20],
      'missing_static_metrics_count':len(bad),
      'static_metric_drift_count':len(changed),
      'static_metric_drift_by_metric':dict(Counter(x['metric'] for x in changed)),
      'static_metric_drift_examples':changed[:40],
      'requires_dissertation_reconciliation':bool(changed),
      'functional_counts':{s:{'passed':source_counts[(s,True)],'failed':source_counts[(s,False)]}
                           for s in ('beginner','llm','expert')},
      'archived_sha256':sha(old) if old.is_file() else None,
      'fresh_sha256':sha(fresh) if fresh.is_file() else None,
      'limitations':[
          'Static numeric results may vary across tool versions; if static_metric_drift_count is positive, reconcile them with dissertation tables and figures before submission',
          'The original generation-visible tests are not prospective blinded tests',
          'Constructed baselines are not confirmed real programmer cohorts',
          'SHA-256 identifies code bytes, not the model or person that authored them',
      ],
    }
    VER.mkdir(exist_ok=True)
    (VER/'windows_review_summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
