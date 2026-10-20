from functools import lru_cache


@lru_cache(maxsize=None)
def _fib(n: int) -> int:
    if n < 2:
        return n
    return _fib(n - 1) + _fib(n - 2)


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number via memoized recursion.

    Uses an ``lru_cache``-backed helper so repeated and large calls stay
    efficient. Negative inputs are rejected.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return _fib(n)
