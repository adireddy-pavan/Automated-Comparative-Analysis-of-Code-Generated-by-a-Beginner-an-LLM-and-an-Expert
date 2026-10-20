from solution import quicksort


def test_core_basic():
    assert quicksort([3, 1, 2]) == [1, 2, 3]


def test_core_reverse():
    assert quicksort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_core_mixed():
    assert quicksort([3, 7, 1, 9, 2]) == [1, 2, 3, 7, 9]


def test_edge_empty():
    assert quicksort([]) == []


def test_edge_single():
    assert quicksort([42]) == [42]


def test_edge_duplicates():
    assert quicksort([3, 1, 2, 3, 1, 2]) == [1, 1, 2, 2, 3, 3]


def test_edge_negatives():
    assert quicksort([-3, 5, -1, 0, 2]) == [-3, -1, 0, 2, 5]


def test_edge_already_sorted():
    assert quicksort([1, 2, 3, 4]) == [1, 2, 3, 4]
