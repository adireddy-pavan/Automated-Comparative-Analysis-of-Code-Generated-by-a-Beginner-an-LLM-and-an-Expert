"""Prevent partial/nonzero test execution from being scored as passing."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from src import correctness,dataset_loader


def test_nonzero_pytest_exit_not_scored_pass(monkeypatch):
    task=next(t for t in dataset_loader.discover_tasks() if t.task_id=='sum_list')
    monkeypatch.setattr(correctness.utils,'run_command', lambda *a,**kw: subprocess.CompletedProcess(a[0],124,stdout='1 passed in 0.1s',stderr='TIMEOUT'))
    monkeypatch.setattr(correctness.utils,'save_evidence',lambda *a: None)
    outcome=correctness.run_one(task,'expert')
    assert outcome['functional_pass'] is False
    assert '124' in outcome['reason']
