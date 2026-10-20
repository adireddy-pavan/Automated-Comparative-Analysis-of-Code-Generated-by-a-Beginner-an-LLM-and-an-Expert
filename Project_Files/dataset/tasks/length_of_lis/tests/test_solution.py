from solution import length_of_lis


def test_core_classic():
    assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4


def test_core_interleaved():
    assert length_of_lis([0, 1, 0, 3, 2, 3]) == 4


def test_edge_all_equal():
    assert length_of_lis([7, 7, 7, 7]) == 1


def test_edge_empty():
    assert length_of_lis([]) == 0


def test_edge_increasing():
    assert length_of_lis([1, 2, 3]) == 3


def test_edge_decreasing():
    assert length_of_lis([3, 2, 1]) == 1
