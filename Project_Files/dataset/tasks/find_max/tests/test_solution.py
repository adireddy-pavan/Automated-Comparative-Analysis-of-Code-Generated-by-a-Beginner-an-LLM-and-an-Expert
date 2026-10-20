from solution import find_max


def test_core_basic():
    assert find_max([3, 1, 2]) == 3


def test_core_single():
    assert find_max([5]) == 5


def test_edge_all_negative():
    assert find_max([-3, -1, -2]) == -1


def test_edge_duplicates():
    assert find_max([2, 2, 2]) == 2


def test_edge_floats_mixed():
    assert find_max([1.5, 2.5, 0]) == 2.5
