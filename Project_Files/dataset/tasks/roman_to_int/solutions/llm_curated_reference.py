"""Roman numeral to integer conversion (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def roman_to_int(s: str) -> int:
    """
    Convert a Roman numeral string into its integer value.

    Roman numerals are usually additive (symbols are summed left to right),
    but six subtractive combinations exist (IV, IX, XL, XC, CD, CM). The
    general rule that captures all of these: if a symbol's value is smaller
    than the value of the symbol that follows it, subtract it instead of
    adding it.

    Args:
        s: The Roman numeral string, using the symbols ``I V X L C D M``.

    Returns:
        The integer value represented by the numeral.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(s, str):
        s = str(s)

    # Look-up table mapping each Roman symbol to its integer value.
    symbol_values = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
    }

    # Running total that we will accumulate as we scan the numeral.
    running_total = 0

    # The number of characters, cached so we can safely look one ahead.
    length = len(s)

    # Examine each symbol together with the symbol that comes after it.
    for position in range(length):
        current_value = symbol_values[s[position]]

        # Determine the value of the next symbol, if there is one.
        if position + 1 < length:
            next_value = symbol_values[s[position + 1]]
        else:
            next_value = 0

        # Subtractive case: a smaller symbol in front of a larger one.
        if current_value < next_value:
            running_total = running_total - current_value
        else:
            # Additive case: simply add this symbol's value.
            running_total = running_total + current_value

    return running_total
