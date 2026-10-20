"""N-th Fibonacci number (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def fibonacci(n: int) -> int:
    """
    Compute the n-th number in the Fibonacci sequence.

    The Fibonacci sequence starts with 0 and 1, and every subsequent value is
    the sum of the two values that come before it:

        0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...

    This implementation uses a simple iterative approach so that it stays fast
    and avoids the deep recursion (and repeated work) of a naive recursive
    version.

    Args:
        n: The zero-based index into the Fibonacci sequence.

    Returns:
        The Fibonacci number located at index ``n``.

    Raises:
        ValueError: If ``n`` is a negative integer.
    """
    # Defensive: coerce a boolean or float-looking integer to a plain int so the
    # arithmetic below behaves predictably for well-formed numeric input.
    if not isinstance(n, int):
        n = int(n)

    # The Fibonacci sequence is not defined for negative indices, so reject them.
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    # Handle the two base cases explicitly for clarity.
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Iteratively build up the sequence.
    # ``previous`` holds fib(k - 2) and ``current`` holds fib(k - 1).
    previous = 0
    current = 1

    # We already have fib(0) and fib(1), so start counting from index 2.
    for _index in range(2, n + 1):
        # The next number is the sum of the two preceding numbers.
        next_value = previous + current
        # Shift the window forward by one position.
        previous = current
        current = next_value

    # After the loop ``current`` holds fib(n).
    return current
