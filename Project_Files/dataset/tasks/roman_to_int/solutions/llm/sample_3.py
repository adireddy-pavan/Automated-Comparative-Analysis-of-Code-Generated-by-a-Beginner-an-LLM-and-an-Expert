def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to its integer value.

    Replaces the six subtractive pairs with additive placeholders of equal
    value, then simply sums every single-symbol value.
    """
    pairs = {
        "IV": "IIII",
        "IX": "VIIII",
        "XL": "XXXX",
        "XC": "LXXXX",
        "CD": "CCCC",
        "CM": "DCCCC",
    }
    expanded = s
    for token, replacement in pairs.items():
        expanded = expanded.replace(token, replacement)

    singles = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    return sum(singles[ch] for ch in expanded)
