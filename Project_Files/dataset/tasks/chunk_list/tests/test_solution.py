from solution import chunk_list


def test_core_even():
    assert chunk_list([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_core_remainder():
    assert chunk_list([1, 2, 3], 2) == [[1, 2], [3]]


def test_core_remainder_size3():
    assert chunk_list([1, 2, 3, 4, 5], 3) == [[1, 2, 3], [4, 5]]


def test_edge_empty():
    assert chunk_list([], 2) == []


def test_edge_size_one():
    assert chunk_list([1], 1) == [[1]]
