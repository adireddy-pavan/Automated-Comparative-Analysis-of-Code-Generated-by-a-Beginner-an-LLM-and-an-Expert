from solution import merge_intervals


def test_core_basic():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_core_two_overlap():
    assert merge_intervals([[1, 4], [2, 5]]) == [[1, 5]]


def test_core_disjoint():
    assert merge_intervals([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]


def test_edge_empty():
    assert merge_intervals([]) == []


def test_edge_touching():
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_edge_unsorted():
    assert merge_intervals([[2, 6], [1, 3]]) == [[1, 6]]


def test_edge_nested():
    assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]


def test_edge_single():
    assert merge_intervals([[5, 7]]) == [[5, 7]]
