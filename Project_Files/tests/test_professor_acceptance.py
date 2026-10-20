"""Integrity checks; these tests cannot manufacture external research evidence."""
from __future__ import annotations
import json
import shutil
from pathlib import Path

import pandas as pd

from tools import archive_scientific_crosscheck, evidence_completion_status, windows_review_summary


def test_archived_statistics_independently_reproduced():
    output=archive_scientific_crosscheck.crosscheck()
    assert output['status']=='PASS_ARCHIVE_ONLY'
    assert output['source_counts']=={'beginner':30,'expert':30,'llm':150}
    assert output['metrics']['mi']['n_matched_tasks']==30
    assert output['metrics']['mi']['p_value']<1e-8


def test_independent_crosscheck_detects_manipulated_statistic(tmp_path):
    saved=json.loads(archive_scientific_crosscheck.STATS.read_text(encoding='utf-8'))
    saved['metrics']['mi']['friedman']['statistic']=0
    tampered=tmp_path/'stats.json'
    tampered.write_text(json.dumps(saved),encoding='utf-8')
    result=archive_scientific_crosscheck.crosscheck(stats_path=tampered)
    assert result['status']=='FAIL'
    assert any('mi:' in issue for issue in result['errors'])


def test_outcome_truthy_handling():
    assert windows_review_summary.truthy(True)
    assert windows_review_summary.truthy('TRUE')
    assert not windows_review_summary.truthy('False')


def test_technical_pass_cannot_be_faked_by_status_only(tmp_path, monkeypatch):
    monkeypatch.setattr(evidence_completion_status,'VER',tmp_path)
    monkeypatch.setattr(evidence_completion_status,'EX',tmp_path/'external_results')
    runs=tmp_path/'windows_runs'/'made_up_run'
    runs.mkdir(parents=True)
    (runs/'WINDOWS_STATUS.json').write_text('{"status":"PASS"}',encoding='utf-8')
    # The check must not classify the run as complete without logs and a matching report.
    assert evidence_completion_status.main()==0
    output=json.loads((tmp_path/'evidence_completion_status.json').read_text())
    assert output['checks']['complete_full_windows_pipeline']['status']=='PENDING'


def test_external_manifest_with_future_freeze_rejected(monkeypatch, tmp_path):
    import hashlib
    from datetime import datetime, timedelta, timezone
    from tools import run_external_validation
    monkeypatch.setattr(run_external_validation,'DIR',tmp_path)
    # We need all 30 tasks for a valid complete case payload.
    tasks=sorted(p.name for p in run_external_validation.TASK_ROOT.iterdir() if p.is_dir())
    cases={task:[{'args':[],'expected':True}] for task in tasks}
    content=json.dumps(cases)
    (tmp_path/'cases.json').write_text(content,encoding='utf-8')
    manifest={'test_author_identifier':'external-01',
              'frozen_at_utc':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),
              'cases_sha256':__import__('hashlib').sha256(content.encode()).hexdigest(),
              'specifications_only_attestation':'YES',
              'independent_oracle_review_notes':'Tests created against specifications only'}
    (tmp_path/'frozen_manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    result,_=run_external_validation.check()
    assert result['status']=='INVALID_EXTERNAL_INPUT'
    assert any('future' in error for error in result['errors'])


def test_windows_comparison_detects_numeric_static_drift_without_faking_failure(tmp_path, monkeypatch):
    import csv
    import json
    from tools import windows_review_summary as checker
    root=tmp_path/'Project_Files'; (root/'outputs').mkdir(parents=True)
    (root/'verification').mkdir()
    for relative in ('outputs/stats.json','outputs/metrics.csv'):
        dest=root/relative
        dest.write_bytes((checker.ROOT/relative).read_bytes())
    shutil.copy2(root/'outputs/metrics.csv',root/'verification/archived_metrics_before_run.csv')
    for p in ('outputs/stats.md','report/report.md','report/report.html',
              'report/report.docx','report/dashboard.html',
              'figures/matched_inference_summary.png','evidence/run.log'):
        dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('fixture',encoding='utf-8')
    monkeypatch.setattr(checker,'ROOT',root)
    monkeypatch.setattr(checker,'VER',root/'verification')
    assert checker.main()==0
    original=json.loads((root/'verification/windows_review_summary.json').read_text())
    assert original['static_metric_drift_count']==0
    rows=list(csv.DictReader((root/'outputs/metrics.csv').open(encoding='utf-8')))
    rows[0]['mi']=str(float(rows[0]['mi'])+10)
    with (root/'outputs/metrics.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    assert checker.main()==0
    changed=json.loads((root/'verification/windows_review_summary.json').read_text())
    assert changed['static_metric_drift_count']==1
    assert changed['static_metric_drift_by_metric']['mi']==1
    assert changed['requires_dissertation_reconciliation']
