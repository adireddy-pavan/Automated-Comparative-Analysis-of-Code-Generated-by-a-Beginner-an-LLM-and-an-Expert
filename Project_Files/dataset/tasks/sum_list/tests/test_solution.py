from solution import sum_list


def test_core_basic():
    assert sum_list([1, 2, 3]) == 6


def test_core_single():
    assert sum_list([5]) == 5


def test_edge_empty():
    assert sum_list([]) == 0


def test_edge_negatives():
    assert sum_list([-1, 1]) == 0


def test_edge_floats():
    assert sum_list([1.5, 2.5]) == 4.0
