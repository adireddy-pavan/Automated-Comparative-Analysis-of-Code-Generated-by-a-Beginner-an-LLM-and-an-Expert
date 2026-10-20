"""Iterative Fibonacci computation."""


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number using bottom-up iteration.

    The sequence is defined as fib(0) = 0, fib(1) = 1, and
    fib(k) = fib(k - 1) + fib(k - 2) for k >= 2.

    Raises:
        ValueError: if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous
