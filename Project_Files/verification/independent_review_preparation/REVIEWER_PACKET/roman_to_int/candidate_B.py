"""Roman numeral to integer conversion (expert reference solution)."""
from __future__ import annotations


def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string *s* to its integer value.

    A symbol that is smaller than the symbol immediately after it is
    subtracted (e.g. ``IV`` is 4); otherwise its value is added.

    Args:
        s: A valid Roman numeral built from ``I V X L C D M``.

    Returns:
        The integer represented by the numeral.
    """
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for index, symbol in enumerate(s):
        current = values[symbol]
        if index + 1 < len(s) and current < values[s[index + 1]]:
            total -= current
        else:
            total += current
    return total
