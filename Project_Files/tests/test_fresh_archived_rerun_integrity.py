"""Evidence-integrity regression: dated independent local reexecution of visible tests.

Validates the stored 2026-10-16 rerun hashes/outcomes against source bytes;
does NOT rerun tests or authenticate original code generation.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def test_fresh_visible_tests_match_original_archive():
    result=ROOT/'verification/fresh_visible_test_rerun.csv'
    assert result.exists(), 'Record a genuine fresh visible-test rerun'
    with result.open(newline='', encoding='utf-8') as f:
        fresh=list(csv.DictReader(f))
    with (ROOT/'outputs/metrics.csv').open(newline='', encoding='utf-8') as f:
        archived=list(csv.DictReader(f))
    original={(x['task_id'],x['source'],x['sample']):x for x in archived}
    assert len(fresh)==len(original)==210
    for entry in fresh:
        key=(entry['task_id'],entry['source'],entry['sample'])
        assert key in original
        task,source,sample=key
        sol=(ROOT/'dataset/tasks'/task/'solutions'/source/f'sample_{sample}.py' if source=='llm'
             else ROOT/'dataset/tasks'/task/'solutions'/f'{source}.py')
        assert hashlib.sha256(sol.read_bytes()).hexdigest()==entry['source_sha256']
        assert entry['status'] in ('passed','failed'), f'Runner errors not accepted: {key}'
        before=original[key]['functional_pass'].strip().lower() in ('true','1')
        assert before == (entry['status']=='passed')
    summary=json.loads((ROOT/'verification/fresh_visible_test_rerun_summary.json').read_text())
    assert summary['runner_errors']==0
    assert summary['archived_outcome_mismatches']==[]
    assert summary['passed']==193
