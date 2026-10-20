"""FizzBuzz sequence generator (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It walks through the
classic FizzBuzz rules one integer at a time and documents each decision.
"""
from __future__ import annotations


def fizzbuzz(n: int) -> list[str]:
    """
    Build the FizzBuzz sequence for the integers from 1 up to ``n`` inclusive.

    The rules are applied to each integer in order:

    * If it is divisible by both 3 and 5, the term is ``"FizzBuzz"``.
    * If it is divisible by 3 only, the term is ``"Fizz"``.
    * If it is divisible by 5 only, the term is ``"Buzz"``.
    * Otherwise, the term is the integer rendered as a string.

    Args:
        n: The inclusive upper bound of the sequence.

    Returns:
        A list of FizzBuzz terms as strings. When ``n`` is less than 1 the
        resulting list is empty.
    """
    # Defensive: coerce a non-integer input to an integer so we never crash.
    if not isinstance(n, int):
        n = int(n)

    # The accumulated sequence of FizzBuzz terms.
    sequence: list[str] = []

    # Walk through every integer in the inclusive range 1..n.
    for current_number in range(1, n + 1):
        # Pre-compute the divisibility checks for readability.
        divisible_by_three = current_number % 3 == 0
        divisible_by_five = current_number % 5 == 0

        if divisible_by_three and divisible_by_five:
            # Both factors apply, so use the combined word.
            sequence.append("FizzBuzz")
        elif divisible_by_three:
            # Only the factor of 3 applies.
            sequence.append("Fizz")
        elif divisible_by_five:
            # Only the factor of 5 applies.
            sequence.append("Buzz")
        else:
            # No factor applies, so use the plain decimal string.
            sequence.append(str(current_number))

    return sequence
