from typing import List


def max_profit(prices: List[int]) -> int:
    """Best buy/sell profit reframed as max-subarray on daily price changes.

    The profit of buying on day ``i`` and selling on day ``j > i`` equals the
    sum of consecutive day-to-day deltas between them. So the maximum profit is
    the maximum contiguous-sum (Kadane) of the delta sequence, floored at 0.
    """
    best = 0
    running = 0
    for prev, curr in zip(prices, prices[1:]):
        running = max(0, running + (curr - prev))
        best = max(best, running)
    return best
