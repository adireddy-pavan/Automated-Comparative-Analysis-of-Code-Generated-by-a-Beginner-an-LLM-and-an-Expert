def fibonacci(n):
    a = 1
    b = 1
    if n == 1 or n == 2:
        return 1
    i = 3
    while i <= n:
        c = a + b
        a = b
        b = c
        i = i + 1
    return b
