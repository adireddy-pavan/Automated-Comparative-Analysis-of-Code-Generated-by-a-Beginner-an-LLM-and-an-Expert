"""Sum of decimal digits of an integer (expert reference solution)."""
from __future__ import annotations


def sum_of_digits(n: int) -> int:
    """Return the sum of the decimal digits of ``abs(n)``.

    Args:
        n: The integer whose digits are summed. The sign is ignored.

    Returns:
        The sum of the base-10 digits of the absolute value of *n*.
    """
    return sum(int(d) for d in str(abs(n)))
