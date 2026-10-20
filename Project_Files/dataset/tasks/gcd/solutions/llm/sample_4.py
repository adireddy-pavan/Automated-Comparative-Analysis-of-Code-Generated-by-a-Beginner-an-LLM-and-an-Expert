import math


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of two integers.

    Delegates to :func:`math.gcd`, which already returns a non-negative
    result and defines ``gcd(0, 0)`` as ``0``. Inputs are passed through
    ``abs`` defensively to keep the contract explicit.
    """
    return math.gcd(abs(a), abs(b))
