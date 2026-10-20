from solution import second_largest


def test_core_basic():
    assert second_largest([1, 2, 3]) == 2


def test_core_unsorted():
    assert second_largest([3, 1, 2]) == 2


def test_edge_duplicate_max():
    assert second_largest([5, 5, 4]) == 4


def test_edge_many_duplicates():
    assert second_largest([10, 10, 9, 9]) == 9


def test_edge_two_values():
    assert second_largest([1, 2]) == 1


def test_edge_negatives():
    assert second_largest([-1, -2, -3]) == -2
