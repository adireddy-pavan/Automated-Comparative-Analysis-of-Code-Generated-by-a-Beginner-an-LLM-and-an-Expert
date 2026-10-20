"""Greatest common divisor via the Euclidean algorithm (expert reference solution)."""
from __future__ import annotations


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of *a* and *b*.

    The result is always non-negative; the sign of the inputs is ignored. By the
    usual convention ``gcd(0, 0)`` is defined to be ``0``.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The greatest common divisor of ``abs(a)`` and ``abs(b)``.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
