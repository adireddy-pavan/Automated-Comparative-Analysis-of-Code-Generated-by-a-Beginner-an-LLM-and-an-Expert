from solution import count_words


def test_core_basic():
    assert count_words("hello world") == 2


def test_core_single():
    assert count_words("one") == 1


def test_edge_empty():
    assert count_words("") == 0


def test_edge_only_spaces():
    assert count_words("   ") == 0


def test_edge_multiple_spaces():
    assert count_words("a b  c") == 3


def test_edge_leading_space():
    assert count_words(" leading") == 1
