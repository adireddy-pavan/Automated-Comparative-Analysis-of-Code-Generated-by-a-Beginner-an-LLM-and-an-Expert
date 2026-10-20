"""Check the source-hash chain-of-custody inventory's verifiable scope."""
from tools.provenance_inventory import audit


def test_manifest_has_exact_archived_sample_counts():
    report = audit()
    assert report['status'] == 'pass'
    assert report['record_count'] == 210
    assert report['counts'] == {'beginner': 30, 'llm': 150, 'expert': 30}
    assert len({(r['task'], r['source_label'], r['sample']) for r in report['source_records']}) == 210


def test_manifest_does_not_pretend_model_authentication():
    report = audit()
    assert 'original model provider' in report['claims_not_verified']
    assert all(len(r['sha256']) == 64 for r in report['source_records'])
    assert all('NOT provider-authenticated' in r['provenance'] for r in report['source_records'] if r['source_label'] == 'llm')


def test_new_model_collector_is_offline_by_default():
    from tools.collect_new_model_evidence import collect_new
    preview=collect_new('is_palindrome','explicit-model-placeholder',1)
    assert preview[0].startswith('DRY RUN ONLY')
    assert 'No task tests' in preview[1]


def test_new_model_collector_requires_valid_samples():
    from tools.collect_new_model_evidence import collect_new
    import pytest
    with pytest.raises(ValueError):
        collect_new('is_palindrome','test',0)
