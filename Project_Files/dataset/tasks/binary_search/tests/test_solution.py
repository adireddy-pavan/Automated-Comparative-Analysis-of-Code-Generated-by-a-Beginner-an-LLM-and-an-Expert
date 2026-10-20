from solution import binary_search


def test_core_found_mid():
    assert binary_search([1, 2, 3, 4, 5], 3) == 2


def test_core_found_first():
    assert binary_search([1, 2, 3, 4, 5], 1) == 0


def test_core_found_last():
    assert binary_search([1, 2, 3, 4, 5], 5) == 4


def test_edge_empty():
    assert binary_search([], 3) == -1


def test_edge_not_found():
    assert binary_search([1, 2, 3], 4) == -1


def test_edge_single_found():
    assert binary_search([7], 7) == 0


def test_edge_not_found_low():
    assert binary_search([2, 4, 6], 1) == -1
