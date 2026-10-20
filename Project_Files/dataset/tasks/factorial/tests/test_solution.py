import pytest

from solution import factorial


def test_core_basic():
    assert factorial(5) == 120


def test_core_three():
    assert factorial(3) == 6


def test_edge_zero():
    assert factorial(0) == 1


def test_edge_one():
    assert factorial(1) == 1


def test_edge_negative_raises():
    with pytest.raises(ValueError):
        factorial(-1)


def test_edge_larger():
    assert factorial(10) == 3628800
