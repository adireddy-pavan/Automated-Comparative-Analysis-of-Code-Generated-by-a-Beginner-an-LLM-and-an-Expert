from typing import List


def max_profit(prices: List[int]) -> int:
    """Maximum single buy/sell profit via one pass tracking the lowest price.

    As we scan left to right we remember the cheapest day seen so far and, for
    each day, consider selling at the current price. The best such difference is
    the answer; it never drops below 0 because we only sell after buying.
    """
    if not prices:
        return 0

    min_so_far = prices[0]
    best = 0
    for price in prices[1:]:
        best = max(best, price - min_so_far)
        min_so_far = min(min_so_far, price)
    return best
