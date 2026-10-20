"""Factorial of a non-negative integer (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It validates the input,
then multiplies the running product up from 1 to ``n``.
"""
from __future__ import annotations


def factorial(n: int) -> int:
    """
    Compute the factorial of a non-negative integer.

    The factorial ``n!`` is the product of every integer from 1 through ``n``
    inclusive. Two base cases are worth noting: both ``0!`` and ``1!`` equal 1.
    Negative inputs are rejected because the factorial is undefined for them.

    Args:
        n: The non-negative integer whose factorial is required.

    Returns:
        The factorial of ``n``.

    Raises:
        ValueError: If ``n`` is negative.
    """
    # Defensive: coerce a non-integer input to an integer so we never crash.
    if not isinstance(n, int):
        n = int(n)

    # Validate the domain: factorial is only defined for non-negative integers.
    if n < 0:
        raise ValueError("n must be non-negative")

    # Start the running product at the multiplicative identity, 1.
    running_product = 1

    # Multiply by each factor from 2 up to and including n.
    for factor in range(2, n + 1):
        running_product = running_product * factor

    return running_product
