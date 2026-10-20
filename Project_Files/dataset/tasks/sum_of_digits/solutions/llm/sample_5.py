def _digits(value: int):
    """Yield the decimal digits of a non-negative integer, low to high."""
    if value == 0:
        yield 0
        return
    while value > 0:
        yield value % 10
        value //= 10


def sum_of_digits(n: int) -> int:
    """Return the sum of the decimal digits of the absolute value of ``n``.

    The work is delegated to a small generator helper so the public function
    stays a one-liner and the digit extraction is reusable.
    """
    return sum(_digits(abs(int(n))))
