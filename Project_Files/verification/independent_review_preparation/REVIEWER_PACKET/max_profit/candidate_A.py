def max_profit(prices):
    if not prices:
        return 0
    return max(prices) - min(prices)
