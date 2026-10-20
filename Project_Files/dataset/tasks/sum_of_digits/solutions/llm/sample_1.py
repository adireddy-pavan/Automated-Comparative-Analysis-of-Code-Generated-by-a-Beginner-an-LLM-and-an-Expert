def sum_of_digits(n: int) -> int:
    """Return the sum of the decimal digits of the absolute value of ``n``.

    The sign is ignored, so ``sum_of_digits(-123)`` and ``sum_of_digits(123)``
    both yield ``6``.
    """
    total = 0
    value = abs(int(n))
    while value > 0:
        total += value % 10
        value //= 10
    return total
