def sum_of_digits(n: int) -> int:
    """Return the digit sum of the absolute value of an integer recursively.

    Each recursive step peels off the least-significant digit until nothing
    remains, which makes the base case (``0``) handle the zero input cleanly.
    """
    value = abs(int(n))
    if value < 10:
        return value
    return value % 10 + sum_of_digits(value // 10)
