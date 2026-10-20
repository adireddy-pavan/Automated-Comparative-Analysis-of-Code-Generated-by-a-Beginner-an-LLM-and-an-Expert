from solution import coin_change


def test_core_basic():
    assert coin_change([1, 2, 5], 11) == 3


def test_core_greedy_trap():
    # Greedy (4 + 1 + 1) gives 3; optimal is 3 + 3 = 2.
    assert coin_change([1, 3, 4], 6) == 2


def test_edge_impossible():
    assert coin_change([2], 3) == -1


def test_edge_zero_amount():
    assert coin_change([1], 0) == 0


def test_edge_single_coin_impossible():
    assert coin_change([5], 3) == -1


def test_core_larger():
    assert coin_change([2, 5, 10, 1], 27) == 4
