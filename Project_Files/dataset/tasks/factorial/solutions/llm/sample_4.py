import math


def factorial(n: int) -> int:
    """Return the factorial of ``n`` for non-negative integers.

    Thin wrapper around :func:`math.factorial`. We validate the sign first so
    that a negative argument produces a :class:`ValueError` with a clear
    message rather than relying on the implementation's own error type.
    """
    if not isinstance(n, int):
        raise ValueError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    return math.factorial(n)
