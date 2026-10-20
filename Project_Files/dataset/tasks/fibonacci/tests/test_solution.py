import pytest

from solution import fibonacci


def test_core_one():
    assert fibonacci(1) == 1


def test_core_two():
    assert fibonacci(2) == 1


def test_core_ten():
    assert fibonacci(10) == 55


def test_edge_zero():
    assert fibonacci(0) == 0


def test_edge_twenty():
    assert fibonacci(20) == 6765


def test_edge_negative_raises():
    with pytest.raises(ValueError):
        fibonacci(-1)


def test_edge_large():
    assert fibonacci(30) == 832040
