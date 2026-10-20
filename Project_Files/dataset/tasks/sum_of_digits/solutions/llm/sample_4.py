from functools import reduce


def sum_of_digits(n: int) -> int:
    """Compute the sum of the digits of ``abs(n)`` with a functional fold."""
    return reduce(lambda acc, ch: acc + int(ch), str(abs(int(n))), 0)
