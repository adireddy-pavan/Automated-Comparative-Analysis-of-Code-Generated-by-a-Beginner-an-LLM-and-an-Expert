from solution import two_sum


def test_core_basic():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)


def test_core_unsorted():
    assert two_sum([3, 2, 4], 6) == (1, 2)


def test_core_negative_target():
    assert two_sum([-1, -2, -3], -5) == (1, 2)


def test_edge_no_solution():
    assert two_sum([1, 2, 3], 100) is None


def test_edge_empty():
    assert two_sum([], 5) is None


def test_edge_duplicates():
    assert two_sum([3, 3], 6) == (0, 1)


def test_edge_same_element_not_reused():
    assert two_sum([5, 1, 2], 10) is None
