from typing import List


def _term(i: int) -> str:
    """Map a single integer to its FizzBuzz term by concatenation."""
    word = ("Fizz" if i % 3 == 0 else "") + ("Buzz" if i % 5 == 0 else "")
    return word or str(i)


def fizzbuzz(n: int) -> List[str]:
    """Return the FizzBuzz sequence for 1..n as a list of strings.

    Builds each term by concatenating "Fizz" and/or "Buzz"; the number is
    used when neither applies. ``n <= 0`` produces an empty list.
    """
    return [_term(i) for i in range(1, n + 1)]
