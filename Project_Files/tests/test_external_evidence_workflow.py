"""Negative/pending-path checks without fabricating human research evidence."""
from tools import external_evidence_review, run_external_validation


def test_blind_candidate_files_still_match_private_key():
    keys = external_evidence_review.expected_samples()
    assert len(keys) == 60
    assert not external_evidence_review.verify_packet(keys)


def test_empty_reviewer_folder_is_pending(monkeypatch, tmp_path):
    monkeypatch.setattr(external_evidence_review, 'EXTERNAL', tmp_path)
    expected = set(external_evidence_review.expected_samples())
    for number in (1, 2):
        status, data = external_evidence_review.read_reviewer(number, expected)
        assert status['status'] == 'pending'
        assert not data


def test_missing_independent_cases_is_pending(monkeypatch, tmp_path):
    monkeypatch.setattr(run_external_validation, 'DIR', tmp_path)
    status, cases = run_external_validation.check()
    assert status['status'] == 'PENDING'
    assert cases is None


def test_authored_cases_require_actual_freeze_manifest(monkeypatch, tmp_path):
    import json
    monkeypatch.setattr(run_external_validation, 'DIR', tmp_path)
    (tmp_path/'cases.json').write_text(json.dumps({'any_task':[{'args':[],'expected':True}]}))
    (tmp_path/'frozen_manifest.json').write_text(json.dumps({'cases_sha256':'not-a-real-hash'}))
    status, cases = run_external_validation.check()
    assert status['status'] != 'READY_FOR_EXECUTION_UNVERIFIED_AUTHORSHIP'
    assert cases is None
