"""Greatest common divisor via the iterative Euclidean algorithm."""


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of two integers.

    The result is always non-negative, so negative inputs are handled by
    taking absolute values first. By convention ``gcd(0, 0) == 0``.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
