def sum_of_digits(n):
    n = abs(n)
    s = 0
    while n > 0:
        s = s + n % 10
        n = n // 10
    return s
