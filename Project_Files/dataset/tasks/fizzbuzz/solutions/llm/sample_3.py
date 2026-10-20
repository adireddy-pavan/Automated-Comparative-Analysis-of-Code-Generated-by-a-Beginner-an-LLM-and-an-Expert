"""FizzBuzz driven by a divisor -> label rule table.

Keeping the rules in data rather than control flow makes the function easy
to extend (e.g. adding a "Bazz" for 7) without touching the core loop.
"""

from typing import List, Tuple

RULES: Tuple[Tuple[int, str], ...] = ((3, "Fizz"), (5, "Buzz"))


def fizzbuzz(n: int) -> List[str]:
    """Return the FizzBuzz sequence for the integers 1..n inclusive."""
    sequence: List[str] = []
    for i in range(1, n + 1):
        label = "".join(word for divisor, word in RULES if i % divisor == 0)
        sequence.append(label if label else str(i))
    return sequence
