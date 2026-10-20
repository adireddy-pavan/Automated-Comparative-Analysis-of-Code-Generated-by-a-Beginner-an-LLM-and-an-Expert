from typing import Dict


def roman_to_int(s: str) -> int:
    """Convert a Roman numeral to an integer using explicit pair lookups."""
    singles: Dict[str, int] = {
        "I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000,
    }
    subtractive: Dict[str, int] = {
        "IV": 4, "IX": 9, "XL": 40, "XC": 90, "CD": 400, "CM": 900,
    }

    total = 0
    i = 0
    n = len(s)
    while i < n:
        pair = s[i:i + 2]
        if pair in subtractive:
            total += subtractive[pair]
            i += 2
        else:
            total += singles[s[i]]
            i += 1
    return total
