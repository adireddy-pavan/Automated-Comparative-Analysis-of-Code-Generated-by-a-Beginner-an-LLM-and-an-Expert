"""Lightweight integrity regression checks for the coursework archive."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.audit_repro_evidence import audit


def test_archive_has_unique_task_source_sample_keys():
    result=audit()
    assert result['status']=='pass', result['strict_errors']
    assert result['task_count']==30
    assert result['unique_samples']==210
    assert result['metric_rows']==210


def test_expected_condition_sizes():
    result=audit()
    assert result['archive_pass_counts']=={
        'beginner': {'passed':13,'total':30},
        'llm': {'passed':150,'total':150},
        'expert': {'passed':30,'total':30},
    }
