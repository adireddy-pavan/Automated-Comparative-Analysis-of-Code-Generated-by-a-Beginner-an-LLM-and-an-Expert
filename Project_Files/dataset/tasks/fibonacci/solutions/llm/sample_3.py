"""Fibonacci via fast-doubling.

The fast-doubling identities let us compute the n-th Fibonacci number in
O(log n) arithmetic operations:

    F(2k)   = F(k) * (2 * F(k + 1) - F(k))
    F(2k+1) = F(k)^2 + F(k + 1)^2

This is markedly faster than linear iteration for large ``n``.
"""

from typing import Tuple


def _fib_pair(n: int) -> Tuple[int, int]:
    """Return the tuple ``(F(n), F(n + 1))`` using fast doubling."""
    if n == 0:
        return (0, 1)

    # Recurse on the high bits, then combine.
    a, b = _fib_pair(n >> 1)
    c = a * (2 * b - a)
    d = a * a + b * b

    if n & 1:
        return (d, c + d)
    return (c, d)


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number using the fast-doubling method.

    Raises:
        ValueError: when ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    return _fib_pair(n)[0]
