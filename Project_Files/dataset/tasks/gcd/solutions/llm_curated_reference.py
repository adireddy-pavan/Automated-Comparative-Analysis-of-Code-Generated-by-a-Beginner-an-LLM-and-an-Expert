"""Greatest common divisor (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It implements the classic
Euclidean algorithm and documents every step.
"""
from __future__ import annotations


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor (GCD) of two integers.

    The Euclidean algorithm is used: repeatedly replace the pair ``(a, b)`` with
    ``(b, a % b)`` until the second value reaches zero, at which point the first
    value is the GCD. The sign of the inputs is ignored, so the result is always
    non-negative. By convention ``gcd(0, 0)`` is ``0``.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The greatest common divisor of the absolute values of ``a`` and ``b``.
    """
    # Defensive: coerce non-integer inputs to integers so we never crash.
    if not isinstance(a, int):
        a = int(a)
    if not isinstance(b, int):
        b = int(b)

    # Work with magnitudes only; the GCD is independent of sign.
    first_value = abs(a)
    second_value = abs(b)

    # Apply the Euclidean reduction until the second value becomes zero.
    while second_value != 0:
        # The remainder of the division becomes the next second value.
        remainder = first_value % second_value
        # Shift the pair: the old second value moves into the first slot.
        first_value = second_value
        second_value = remainder

    # When the loop ends, the first value holds the greatest common divisor.
    return first_value
