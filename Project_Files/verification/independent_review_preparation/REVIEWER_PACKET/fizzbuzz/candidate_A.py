"""FizzBuzz sequence generator (expert reference solution)."""
from __future__ import annotations


def fizzbuzz(n: int) -> list[str]:
    """Return the FizzBuzz sequence for the integers ``1..n`` inclusive.

    Args:
        n: The upper bound of the sequence. Values below 1 yield an empty list.

    Returns:
        A list of strings where multiples of 15 become ``"FizzBuzz"``, multiples
        of 3 become ``"Fizz"``, multiples of 5 become ``"Buzz"``, and every other
        integer becomes its decimal string representation.
    """

    def term(i: int) -> str:
        if i % 15 == 0:
            return "FizzBuzz"
        if i % 3 == 0:
            return "Fizz"
        if i % 5 == 0:
            return "Buzz"
        return str(i)

    return [term(i) for i in range(1, n + 1)]
