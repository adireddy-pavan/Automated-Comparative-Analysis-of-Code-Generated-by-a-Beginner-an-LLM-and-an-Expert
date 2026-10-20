from itertools import accumulate
from typing import List


def max_profit(prices: List[int]) -> int:
    """Vectorised-style pass using a running minimum of past prices.

    ``accumulate(prices, min)`` produces, for every day, the cheapest price up
    to and including that day -- the best price we could have bought at. The
    answer is the largest gap between a day's price and its running minimum.
    """
    if not prices:
        return 0

    running_min = accumulate(prices, min)
    return max(price - low for price, low in zip(prices, running_min))
