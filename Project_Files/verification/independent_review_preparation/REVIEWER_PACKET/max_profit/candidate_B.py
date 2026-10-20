"""Best single buy/sell profit (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def max_profit(prices: Sequence[int]) -> int:
    """Return the maximum profit from one buy followed by one later sell.

    A single left-to-right pass tracks the lowest price seen so far and the best
    profit achievable by selling at the current day. Buying must precede selling,
    so the running minimum captures the only valid buy points.

    Args:
        prices: Daily prices in chronological order.

    Returns:
        The maximum achievable profit, or 0 if no profitable trade exists.
    """
    best = 0
    lowest = None
    for price in prices:
        if lowest is None or price < lowest:
            lowest = price
        elif price - lowest > best:
            best = price - lowest
    return best
