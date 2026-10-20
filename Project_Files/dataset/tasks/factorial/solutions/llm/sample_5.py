def factorial(n: int) -> int:
    """Compute ``n!`` for a non-negative integer using an accumulator loop.

    Walks the integers from ``n`` down to ``2`` and multiplies them together.
    ``0!`` and ``1!`` both yield the empty/identity product of 1. Negative
    inputs are invalid and raise :class:`ValueError`.
    """
    if n < 0:
        raise ValueError("Cannot compute factorial of a negative number.")

    product = 1
    current = n
    while current > 1:
        product *= current
        current -= 1
    return product
