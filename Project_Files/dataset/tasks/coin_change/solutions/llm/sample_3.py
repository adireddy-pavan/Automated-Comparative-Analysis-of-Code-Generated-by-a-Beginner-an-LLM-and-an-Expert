from functools import lru_cache
from typing import List


def coin_change(coins: List[int], amount: int) -> int:
    """Top-down memoized recursion for the minimum-coin problem.

    ``fewest(rem)`` returns the least coins needed for ``rem`` (or infinity if
    impossible). We try every coin that fits and take the cheapest resulting
    sub-solution. Memoization keeps each remainder solved only once.
    """
    coin_tuple = tuple(coins)
    INF = float("inf")

    @lru_cache(maxsize=None)
    def fewest(rem: int) -> float:
        if rem == 0:
            return 0
        best = INF
        for coin in coin_tuple:
            if coin <= rem:
                best = min(best, 1 + fewest(rem - coin))
        return best

    result = fewest(amount)
    return int(result) if result != INF else -1
