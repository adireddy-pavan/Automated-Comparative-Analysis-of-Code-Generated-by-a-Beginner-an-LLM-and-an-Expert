"""Research-integrity checks for constructed styles (not human validation)."""
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tools.audit_baselines import audit, describe


def test_constructed_baselines_exist_parse_and_hash():
    rows=audit()
    assert len(rows)==60
    assert len(set((r["task_id"],r["constructed_label"]) for r in rows))==60
    assert {r["constructed_label"] for r in rows}=={"beginner","expert"}
    assert all(len(r["sha256"])==64 for r in rows)


def test_missing_entrypoint_rejected(tmp_path):
    f=tmp_path/"x.py";f.write_text("def other(): return 1\n")
    with pytest.raises(ValueError,match="Expected one entry point"):
        describe(f,"required")
