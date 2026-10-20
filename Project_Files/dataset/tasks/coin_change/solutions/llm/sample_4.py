from typing import List


def coin_change(coins: List[int], amount: int) -> int:
    """Unbounded-knapsack style DP with the coins in the outer loop.

    For each denomination we relax every amount it can contribute to. Because a
    coin may be reused, the inner loop runs forwards over the amounts. The order
    of the loops does not change the final minimum.
    """
    INF = amount + 1  # a value larger than any real coin count
    dp = [0] + [INF] * amount

    for coin in coins:
        if coin <= 0:
            continue
        for a in range(coin, amount + 1):
            candidate = dp[a - coin] + 1
            if candidate < dp[a]:
                dp[a] = candidate

    return dp[amount] if dp[amount] != INF else -1
