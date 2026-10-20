from solution import is_subsequence


def test_core_true():
    assert is_subsequence("abc", "ahbgdc") is True


def test_core_false_order():
    assert is_subsequence("axc", "ahbgdc") is False


def test_core_spread():
    assert is_subsequence("ace", "abcde") is True


def test_edge_empty_s():
    assert is_subsequence("", "abc") is True


def test_edge_empty_t():
    assert is_subsequence("abc", "") is False


def test_edge_repeats_need_count():
    assert is_subsequence("aaa", "aa") is False
