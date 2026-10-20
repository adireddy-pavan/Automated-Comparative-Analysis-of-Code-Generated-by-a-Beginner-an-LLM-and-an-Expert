def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b != 0:
        t = b
        b = a % b
        a = t
    return a
