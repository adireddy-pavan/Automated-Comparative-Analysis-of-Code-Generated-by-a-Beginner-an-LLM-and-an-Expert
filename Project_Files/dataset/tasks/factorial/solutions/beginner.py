def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    res = 1
    i = 2
    while i <= n:
        res = res * i
        i = i + 1
    return res
