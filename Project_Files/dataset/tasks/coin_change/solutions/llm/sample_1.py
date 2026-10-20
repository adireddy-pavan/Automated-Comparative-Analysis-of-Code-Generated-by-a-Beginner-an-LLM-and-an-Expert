from typing import List


def coin_change(coins: List[int], amount: int) -> int:
    """Fewest coins to make ``amount`` via bottom-up dynamic programming.

    ``dp[a]`` is the minimum number of coins needed to total ``a``. We build it
    up from 0, trying every coin at each sub-amount. ``inf`` marks an
    unreachable amount; if the target stays unreachable we return -1.
    """
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a and dp[a - coin] + 1 < dp[a]:
                dp[a] = dp[a - coin] + 1
    return dp[amount] if dp[amount] != INF else -1
