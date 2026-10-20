"""Sum of decimal digits of an integer (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It peels off one digit at
a time using modulo and integer division.
"""
from __future__ import annotations


def sum_of_digits(n: int) -> int:
    """
    Add together the decimal digits of an integer.

    The sign of the input is ignored, so negative numbers are handled by taking
    the absolute value first. The digits are extracted one at a time from the
    least significant end using the remainder and integer-division operators.

    Args:
        n: The integer whose digits should be summed.

    Returns:
        The sum of the base-10 digits of the absolute value of ``n``.
    """
    # Defensive: coerce a non-integer input to an integer so we never crash.
    if not isinstance(n, int):
        n = int(n)

    # Work with the magnitude so a leading minus sign cannot interfere.
    remaining_value = abs(n)

    # Running total of the digits seen so far.
    digit_sum = 0

    # Repeatedly strip the last digit until nothing is left.
    while remaining_value > 0:
        # The last decimal digit is the remainder modulo 10.
        last_digit = remaining_value % 10
        digit_sum = digit_sum + last_digit
        # Drop that digit by dividing by 10 (integer division).
        remaining_value = remaining_value // 10

    return digit_sum
