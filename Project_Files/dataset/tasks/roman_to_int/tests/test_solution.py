from solution import roman_to_int


def test_core_additive():
    assert roman_to_int("III") == 3


def test_core_mixed():
    assert roman_to_int("LVIII") == 58


def test_core_simple():
    assert roman_to_int("XII") == 12


def test_edge_subtractive_four():
    assert roman_to_int("IV") == 4


def test_edge_subtractive_nine():
    assert roman_to_int("IX") == 9


def test_edge_large():
    assert roman_to_int("MCMXCIV") == 1994


def test_edge_max():
    assert roman_to_int("MMMCMXCIX") == 3999
