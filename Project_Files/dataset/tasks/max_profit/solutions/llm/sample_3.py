from typing import List


def max_profit(prices: List[int]) -> int:
    """Brute-force check of every valid (buy, sell) day pair.

    For each possible buy day we test every later sell day and keep the largest
    profit. Quadratic in the number of days, but a direct, easy-to-verify
    statement of what the problem is asking for.
    """
    n = len(prices)
    if n < 2:
        return 0

    best = 0
    for buy in range(n):
        for sell in range(buy + 1, n):
            profit = prices[sell] - prices[buy]
            if profit > best:
                best = profit
    return best
