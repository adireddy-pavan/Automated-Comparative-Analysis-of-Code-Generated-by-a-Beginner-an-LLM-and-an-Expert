"""GCD computed by intersecting the divisor sets of both inputs.

This brute-force approach is slower than Euclid but is easy to reason about:
the greatest common divisor is simply the largest integer dividing both
numbers. It is included as a readable, self-contained alternative.
"""


def _divisors(value: int) -> set:
    """Return the set of positive divisors of a positive integer."""
    found = set()
    i = 1
    while i * i <= value:
        if value % i == 0:
            found.add(i)
            found.add(value // i)
        i += 1
    return found


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of ``a`` and ``b`` (non-negative)."""
    a, b = abs(a), abs(b)

    # Handle zeros explicitly: every integer divides 0, so the GCD is the
    # other operand, and gcd(0, 0) is defined as 0.
    if a == 0:
        return b
    if b == 0:
        return a

    common = _divisors(a) & _divisors(b)
    return max(common)
