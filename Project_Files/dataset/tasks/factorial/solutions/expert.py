"""Factorial of a non-negative integer (expert reference solution)."""
from __future__ import annotations

from functools import reduce
from operator import mul


def factorial(n: int) -> int:
    """Return ``n!`` for a non-negative integer *n*.

    Args:
        n: The integer whose factorial is computed. Must be ``>= 0``.

    Returns:
        The product ``1 * 2 * ... * n``; ``0!`` is ``1`` by definition.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    return reduce(mul, range(2, n + 1), 1)
