from solution import count_vowels


def test_core_basic():
    assert count_vowels("hello") == 2


def test_core_none():
    assert count_vowels("xyz") == 0


def test_core_all():
    assert count_vowels("AEIOU") == 5


def test_edge_empty():
    assert count_vowels("") == 0


def test_edge_word():
    assert count_vowels("Programming") == 3


def test_edge_y_not_vowel():
    assert count_vowels("rhythm") == 0


def test_edge_mixed_case():
    assert count_vowels("aEiOu") == 5
