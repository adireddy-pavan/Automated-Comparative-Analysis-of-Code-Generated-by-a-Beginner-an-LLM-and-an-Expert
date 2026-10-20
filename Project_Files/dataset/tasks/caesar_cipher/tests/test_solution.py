from solution import caesar_cipher


def test_core_basic():
    assert caesar_cipher("abc", 1) == "bcd"


def test_core_upper():
    assert caesar_cipher("ABC", 1) == "BCD"


def test_core_word():
    assert caesar_cipher("hello", 2) == "jgnnq"


def test_edge_wraparound():
    assert caesar_cipher("xyz", 3) == "abc"


def test_edge_upper_wrap():
    assert caesar_cipher("XYZ", 3) == "ABC"


def test_edge_non_alpha():
    assert caesar_cipher("a-b c", 1) == "b-c d"


def test_edge_negative_shift():
    assert caesar_cipher("bcd", -1) == "abc"


def test_edge_large_shift():
    assert caesar_cipher("abc", 27) == "bcd"
