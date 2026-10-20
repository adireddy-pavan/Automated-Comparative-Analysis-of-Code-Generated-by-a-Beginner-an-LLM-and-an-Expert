#!/usr/bin/env python3
"""Independent calculation of selected archived matched-task statistics.

This is a *secondary audit of stored CSV*, not new Radon/Pylint/Bandit evidence,
and not evidence that any human or named provider generated the source files.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.stats import friedmanchisquare

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'outputs' / 'metrics.csv'
STATS = ROOT / 'outputs' / 'stats.json'
DEST = ROOT / 'verification' / 'archived_scientific_crosscheck.json'
FIELDS = ('mi', 'mean_cc', 'halstead_volume', 'pylint_score', 'bandit_total')


def crosscheck(csv_path: Path = CSV, stats_path: Path = STATS) -> dict:
    errors = []
    df = pd.read_csv(csv_path)
    required = {'task_id', 'source', 'sample', 'functional_pass', *FIELDS}
    missing_cols = required - set(df.columns)
    if missing_cols:
        return {'status':'FAIL', 'errors':[f'Missing CSV fields: {sorted(missing_cols)}']}
    dupes = df.duplicated(['task_id','source','sample'])
    if bool(dupes.any()): errors.append(f'Duplicate source/task/sample rows: {int(dupes.sum())}')
    if len(df)!=210 or df.task_id.nunique()!=30: errors.append('Expected 30 tasks and 210 rows')
    expected_by_source = {'beginner':30,'llm':150,'expert':30}
    counts = {str(k):int(v) for k,v in df.groupby('source').size().items()}
    if counts!=expected_by_source: errors.append(f'Unexpected group counts: {counts}')
    old_stats = json.loads(stats_path.read_text(encoding='utf-8'))
    computed = {}
    for metric in FIELDS:
        # Consistent one observation per task/source; medians across 5 LLM replicates.
        wide = df.pivot_table(index='task_id', columns='source', values=metric, aggfunc='median')
        wide = wide.reindex(columns=['beginner','llm','expert']).dropna()
        if len(wide)!=30: errors.append(f'{metric}: only {len(wide)} paired task triples')
        if wide.empty: continue
        stat, p = friedmanchisquare(wide['beginner'], wide['llm'], wide['expert'])
        stored = old_stats.get('metrics',{}).get(metric,{}).get('friedman',{})
        stored_p, stored_stat = stored.get('p'), stored.get('statistic')
        if stored_p is None or stored_stat is None:
            errors.append(f'{metric}: stored test statistic/p-value missing')
        elif abs(float(stored_stat)-float(stat))>0.002 or abs(float(stored_p)-float(p))>max(2e-5,abs(float(p))*0.001):
            errors.append(f'{metric}: archived stats differ from independent calculation')
        computed[metric] = {'n_matched_tasks':len(wide), 'friedman_statistic':round(float(stat),8),
                            'p_value':float(p), 'archived_statistic':stored_stat,
                            'archived_p_value':stored_p}
    return {'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'ARCHIVED_CSV_ONLY_NOT_FRESH_STATIC_ANALYSIS_OR_BLIND_TESTING',
            'status':'PASS_ARCHIVE_ONLY' if not errors else 'FAIL', 'errors':errors,
            'source_counts':counts,'metrics':computed}


def main() -> int:
    try:
        result=crosscheck()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        result={'status':'FAIL','errors':[f'{type(exc).__name__}: {exc}']}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'], 'errors':result['errors'], 'metrics':result.get('metrics',{})}, indent=2))
    return 0 if result['status']=='PASS_ARCHIVE_ONLY' else 1


if __name__=='__main__':raise SystemExit(main())
