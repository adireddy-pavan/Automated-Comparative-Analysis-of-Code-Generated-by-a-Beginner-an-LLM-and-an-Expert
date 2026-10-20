from solution import reverse_string


def test_core_basic():
    assert reverse_string("abc") == "cba"


def test_core_word():
    assert reverse_string("racecar") == "racecar"


def test_edge_empty():
    assert reverse_string("") == ""


def test_edge_single():
    assert reverse_string("a") == "a"


def test_edge_symbols_case():
    assert reverse_string("Ab!") == "!bA"
