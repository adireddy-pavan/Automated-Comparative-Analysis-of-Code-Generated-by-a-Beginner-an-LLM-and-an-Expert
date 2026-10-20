"""Classic FizzBuzz with explicit divisibility checks."""

from typing import List


def fizzbuzz(n: int) -> List[str]:
    """Return the FizzBuzz sequence for the integers 1..n inclusive.

    For each integer ``i``:
      * "FizzBuzz" if divisible by both 3 and 5,
      * "Fizz" if divisible by 3,
      * "Buzz" if divisible by 5,
      * otherwise the number itself as a string.

    Non-positive ``n`` yields an empty list.
    """
    result: List[str] = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
