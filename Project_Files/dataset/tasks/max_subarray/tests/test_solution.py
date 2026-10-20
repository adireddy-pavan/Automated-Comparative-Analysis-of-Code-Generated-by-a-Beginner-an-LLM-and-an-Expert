import pytest

from solution import max_subarray


def test_core_mixed():
    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6


def test_core_positive():
    assert max_subarray([1, 2, 3, 4]) == 10


def test_core_single_pos():
    assert max_subarray([5]) == 5


def test_edge_all_negative():
    assert max_subarray([-3, -1, -2]) == -1


def test_edge_single_negative():
    assert max_subarray([-7]) == -7


def test_edge_empty_raises():
    with pytest.raises(ValueError):
        max_subarray([])


def test_edge_mixed2():
    assert max_subarray([-1, -2, 5, -1, 3]) == 7
