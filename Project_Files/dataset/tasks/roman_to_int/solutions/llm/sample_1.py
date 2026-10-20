def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to its integer value.

    Scans left to right: when a symbol is smaller than the one after it, it is
    a subtractive pair (e.g. ``IV``) and is subtracted; otherwise it is added.
    """
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        current = values[ch]
        if i + 1 < len(s) and current < values[s[i + 1]]:
            total -= current
        else:
            total += current
    return total
