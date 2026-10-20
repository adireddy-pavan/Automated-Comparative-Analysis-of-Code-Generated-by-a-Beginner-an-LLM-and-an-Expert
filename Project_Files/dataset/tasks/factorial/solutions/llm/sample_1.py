def factorial(n: int) -> int:
    """Return ``n!`` for a non-negative integer ``n``.

    Computes the product iteratively. Raises :class:`ValueError` when ``n`` is
    negative, since the factorial is undefined there.
    """
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
