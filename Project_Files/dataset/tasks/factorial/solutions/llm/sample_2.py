def factorial(n: int) -> int:
    """Recursively compute the factorial of a non-negative integer ``n``.

    The base case is ``0! == 1``; each deeper call multiplies ``n`` by the
    factorial of ``n - 1``. A negative argument raises :class:`ValueError`.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)
