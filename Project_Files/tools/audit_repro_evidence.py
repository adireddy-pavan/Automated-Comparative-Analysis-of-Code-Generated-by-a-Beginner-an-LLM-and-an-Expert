#!/usr/bin/env python3
"""Audit the *archived* benchmark without rerunning unavailable static tools.

This is an inventory and data-integrity check, not a fresh experimental
replication, provenance authentication, or validation of human skill labels.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'verification' / 'archived_integrity_audit.json'
SOURCES = {'beginner': 1, 'llm': 5, 'expert': 1}
EVIDENCE_SUFFIXES = ('pytest.txt','radon_cc.json','radon_hal.json','radon_mi.json','radon_raw.json','pylint.json','pylint.txt','bandit.json')

def audit(root: Path = ROOT) -> dict:
    errors = []
    tasks = sorted(x for x in (root/'dataset/tasks').iterdir() if x.is_dir())
    if len(tasks) != 30: errors.append(f'Expected 30 tasks; found {len(tasks)}')
    by_tier = Counter()
    actual_keys = set()
    source_hashes = {}
    for task in tasks:
        metadata = json.loads((task/'meta.json').read_text())
        by_tier[metadata['difficulty']] += 1
        if metadata['id'] != task.name: errors.append(f'Metadata id mismatch: {task.name}')
        if not (task/'tests/test_solution.py').is_file(): errors.append(f'Missing tests: {task.name}')
        for source,n in SOURCES.items():
            for sample in range(1,n+1):
                code_path=(task/'solutions/llm'/f'sample_{sample}.py') if source=='llm' else (task/'solutions'/f'{source}.py')
                key=(task.name,source,sample)
                if not code_path.is_file():
                    errors.append(f'Missing solution {key}'); continue
                actual_keys.add(key)
                source_hashes['/'.join(map(str,key))] = hashlib.sha256(code_path.read_bytes()).hexdigest()
    if set(by_tier.values()) != {10} or len(by_tier)!=3: errors.append(f'Unexpected difficulty composition: {dict(by_tier)}')
    with (root/'outputs/metrics.csv').open(newline='') as fh:
        rows = list(csv.DictReader(fh))
    metrics_keys=[(x['task_id'],x['source'],int(x['sample'])) for x in rows]
    if Counter(metrics_keys).total() != 210: errors.append(f'Metrics row count is {len(rows)}, not 210')
    if len(set(metrics_keys))!=len(metrics_keys): errors.append('Duplicate task/source/sample metric keys')
    missing = actual_keys - set(metrics_keys)
    extra = set(metrics_keys) - actual_keys
    if missing: errors.append(f'Missing {len(missing)} metric keys, examples: {sorted(missing)[:5]}')
    if extra: errors.append(f'Unexpected {len(extra)} metric keys, examples: {sorted(extra)[:5]}')
    archived_evidence_missing=[]
    for task, source, sample in sorted(actual_keys):
        stem=f'{task}__{source}' if source!='llm' else f'{task}__llm_s{sample}'
        for suffix in EVIDENCE_SUFFIXES:
            if not (root/'evidence'/f'{stem}_{suffix}').exists():
                archived_evidence_missing.append(f'{stem}_{suffix}')
    # Not all historic evidence types must necessarily be present; report separately.
    recorded_pass_by_source=Counter()
    recorded_count_by_source=Counter()
    for row in rows:
        recorded_count_by_source[row['source']]+=1
        recorded_pass_by_source[row['source']]+= int(str(row['functional_pass']).strip().lower() in ('true','1'))
    result={
      'generated_utc': datetime.now(timezone.utc).isoformat(),
      'classification':'Archived-file integrity and presence checks; NOT fresh run or verified model/human provenance',
      'status':'pass' if not errors else 'fail',
      'strict_errors':errors,
      'task_count':len(tasks), 'task_tiers':dict(by_tier),'unique_samples':len(actual_keys),
      'metric_rows':len(rows), 'metrics_sha256':hashlib.sha256((root/'outputs/metrics.csv').read_bytes()).hexdigest(),
      'archive_pass_counts':{s:{'passed':recorded_pass_by_source[s],'total':recorded_count_by_source[s]} for s in SOURCES},
      'evidence_files_present':sum(p.is_file() for p in (root/'evidence').iterdir()),
      'expected_evidence_file_checks':len(actual_keys)*len(EVIDENCE_SUFFIXES),
      'expected_evidence_files_missing_count':len(archived_evidence_missing),
      'expected_evidence_files_missing_examples':archived_evidence_missing[:40],
      'sample_source_sha256':source_hashes,
      'limitations': ['Checks that archived files exist and data indexes match; does not verify tool outputs against a fresh execution',
                       'Does not authenticate any claimed model/provider details or represent actual human programmers',
                       'No validation of experimental independence or prospective blinding'],
    }
    return result

def main():
    result=audit()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sample_source_sha256'},indent=2))
    return 0 if result['status']=='pass' else 1

if __name__=='__main__':raise SystemExit(main())
