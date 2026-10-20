from solution import gcd


def test_core_basic():
    assert gcd(12, 18) == 6


def test_core_coprime():
    assert gcd(7, 5) == 1


def test_core_multiple():
    assert gcd(100, 10) == 10


def test_edge_zero_left():
    assert gcd(0, 5) == 5


def test_edge_zero_both():
    assert gcd(0, 0) == 0


def test_edge_negative():
    assert gcd(-12, 18) == 6


def test_edge_equal():
    assert gcd(9, 9) == 9
