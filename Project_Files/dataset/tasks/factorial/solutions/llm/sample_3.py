from functools import reduce
from operator import mul


def factorial(n: int) -> int:
    """Return ``n!`` using a functional fold over ``range(1, n + 1)``.

    For ``n`` of 0 the empty product is returned as 1. Negative inputs are
    rejected with :class:`ValueError`.
    """
    if n < 0:
        raise ValueError(f"factorial undefined for negative input: {n}")
    return reduce(mul, range(1, n + 1), 1)
