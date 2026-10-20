VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int:
    """Convert a Roman numeral to an integer by walking right to left.

    Iterating from the end lets us compare each symbol against the running
    "highest seen so far" value: anything smaller than that is subtractive.
    """
    total = 0
    highest = 0
    for ch in reversed(s):
        value = VALUES[ch]
        if value < highest:
            total -= value
        else:
            total += value
            highest = value
    return total
