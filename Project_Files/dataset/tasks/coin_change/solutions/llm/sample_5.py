from typing import Dict, List


def coin_change(coins: List[int], amount: int) -> int:
    """Recursive solution with an explicit dictionary cache.

    Mirrors the standard top-down recurrence but manages memoization manually
    in ``cache``. Each remainder maps to its best coin count, or ``-1`` when no
    combination of coins can reach it.
    """
    cache: Dict[int, int] = {0: 0}

    def solve(rem: int) -> int:
        if rem in cache:
            return cache[rem]
        best = -1
        for coin in coins:
            if coin <= rem:
                sub = solve(rem - coin)
                if sub != -1 and (best == -1 or sub + 1 < best):
                    best = sub + 1
        cache[rem] = best
        return best

    return solve(amount) if amount >= 0 else -1
