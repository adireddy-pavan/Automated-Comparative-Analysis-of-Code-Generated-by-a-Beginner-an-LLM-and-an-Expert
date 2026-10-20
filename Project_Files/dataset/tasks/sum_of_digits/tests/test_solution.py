from solution import sum_of_digits


def test_core_basic():
    assert sum_of_digits(123) == 6


def test_core_single():
    assert sum_of_digits(7) == 7


def test_core_large():
    assert sum_of_digits(99999) == 45


def test_edge_zero():
    assert sum_of_digits(0) == 0


def test_edge_negative():
    assert sum_of_digits(-123) == 6


def test_edge_trailing_zeros():
    assert sum_of_digits(1000) == 1
