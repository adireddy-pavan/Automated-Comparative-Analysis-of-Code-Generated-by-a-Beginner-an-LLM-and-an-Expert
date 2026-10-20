"""Fewest-coins change (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def coin_change(coins: Sequence[int], amount: int) -> int:
    """Return the minimum number of coins that sum to *amount*, or -1.

    A bottom-up dynamic program: ``best[a]`` is the fewest coins for sub-amount
    ``a``. Greedy choice is intentionally avoided because it is not optimal for
    arbitrary denominations (e.g. coins ``[1, 3, 4]``, amount ``6``).

    Args:
        coins: Available denominations (positive integers).
        amount: Target amount (non-negative integer).

    Returns:
        The fewest coins needed, or -1 if *amount* cannot be formed.
    """
    infinity = amount + 1
    best = [0] + [infinity] * amount
    for sub in range(1, amount + 1):
        for coin in coins:
            if coin <= sub:
                best[sub] = min(best[sub], best[sub - coin] + 1)
    return best[amount] if best[amount] != infinity else -1
