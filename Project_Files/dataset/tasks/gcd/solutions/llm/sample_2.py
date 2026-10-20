def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of ``a`` and ``b``.

    Implemented with the classic recursive Euclidean algorithm,
    ``gcd(a, b) = gcd(b, a mod b)``. Inputs are normalised to their
    magnitudes so the GCD is non-negative; ``gcd(0, 0)`` is ``0``.
    """
    a, b = abs(a), abs(b)
    if b == 0:
        return a
    return gcd(b, a % b)
