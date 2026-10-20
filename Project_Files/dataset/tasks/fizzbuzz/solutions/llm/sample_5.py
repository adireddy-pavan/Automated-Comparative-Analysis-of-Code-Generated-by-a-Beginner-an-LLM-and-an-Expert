from typing import Iterator, List


def _generate(n: int) -> Iterator[str]:
    """Yield FizzBuzz terms one at a time for the range 1..n."""
    for i in range(1, max(n, 0) + 1):
        if i % 3 == 0 and i % 5 == 0:
            yield "FizzBuzz"
        elif i % 3 == 0:
            yield "Fizz"
        elif i % 5 == 0:
            yield "Buzz"
        else:
            yield str(i)


def fizzbuzz(n: int) -> List[str]:
    """Return the FizzBuzz sequence for 1..n inclusive as a list.

    Internally a generator produces the terms lazily; the public function
    materialises them into a list. A non-positive ``n`` gives ``[]``.
    """
    return list(_generate(n))
