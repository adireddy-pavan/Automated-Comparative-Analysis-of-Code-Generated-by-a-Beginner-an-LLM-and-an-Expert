def coin_change(coins, amount):
    coins = sorted(coins, reverse=True)
    count = 0
    for c in coins:
        while amount >= c:
            amount -= c
            count += 1
    if amount == 0:
        return count
    return -1
