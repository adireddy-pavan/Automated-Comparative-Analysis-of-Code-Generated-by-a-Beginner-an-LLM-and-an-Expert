def sum_of_digits(n: int) -> int:
    """Sum the decimal digits of ``abs(n)`` using string iteration."""
    digits = str(abs(int(n)))
    return sum(int(ch) for ch in digits)
