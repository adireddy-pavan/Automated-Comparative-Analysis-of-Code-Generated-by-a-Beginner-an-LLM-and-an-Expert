from typing import List


def max_profit(prices: List[int]) -> int:
    """State-machine DP with explicit "holding" and "cash" positions.

    ``hold`` is the best balance while currently owning the stock (best
    negative cost so far); ``cash`` is the best profit while holding nothing.
    Each day we may keep our state, buy (entering ``hold``), or sell (entering
    ``cash``). With a single allowed transaction, ``cash`` is the answer.
    """
    if not prices:
        return 0

    hold = float("-inf")
    cash = 0
    for price in prices:
        hold = max(hold, -price)        # buy at the lowest cost seen
        cash = max(cash, hold + price)  # or sell at today's price
    return int(cash)
