"""N-th Fibonacci number (expert reference solution)."""
from __future__ import annotations


def fibonacci(n: int) -> int:
    """Return the *n*-th Fibonacci number.

    The sequence is defined by ``fib(0) = 0``, ``fib(1) = 1`` and
    ``fib(k) = fib(k - 1) + fib(k - 2)`` for ``k >= 2``.

    Args:
        n: The (zero-based) index into the Fibonacci sequence.

    Returns:
        The n-th Fibonacci number.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
