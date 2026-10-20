from solution import max_profit


def test_core_basic():
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5


def test_core_no_profit():
    assert max_profit([7, 6, 4, 3, 1]) == 0


def test_edge_order_matters():
    # Min (1) occurs after max (4); only a buy-before-sell trade counts -> 2.
    assert max_profit([2, 4, 1]) == 2


def test_edge_empty():
    assert max_profit([]) == 0


def test_edge_two_days():
    assert max_profit([1, 2]) == 1


def test_edge_flat():
    assert max_profit([3, 3, 3]) == 0
