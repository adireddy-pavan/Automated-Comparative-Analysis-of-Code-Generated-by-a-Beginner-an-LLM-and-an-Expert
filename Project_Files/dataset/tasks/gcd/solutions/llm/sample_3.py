"""GCD using the binary (Stein's) algorithm.

Stein's algorithm replaces the modulo operation of classical Euclid with
subtractions and bit shifts, which can be cheaper on hardware lacking fast
division. It relies on three facts:

    gcd(0, b) = b
    gcd(2a, 2b) = 2 * gcd(a, b)
    gcd(2a, b) = gcd(a, b)  when b is odd
"""


def gcd(a: int, b: int) -> int:
    """Return the non-negative greatest common divisor of ``a`` and ``b``."""
    a, b = abs(a), abs(b)
    if a == 0:
        return b
    if b == 0:
        return a

    # Factor out the common powers of two.
    shift = 0
    while ((a | b) & 1) == 0:
        a >>= 1
        b >>= 1
        shift += 1

    # Make ``a`` odd.
    while (a & 1) == 0:
        a >>= 1

    while b != 0:
        while (b & 1) == 0:
            b >>= 1
        if a > b:
            a, b = b, a
        b -= a

    return a << shift
