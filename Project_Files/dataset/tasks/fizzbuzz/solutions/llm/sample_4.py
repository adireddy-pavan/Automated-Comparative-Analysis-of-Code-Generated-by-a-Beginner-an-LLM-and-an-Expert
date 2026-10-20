from typing import List


def fizzbuzz(n: int) -> List[str]:
    """Return the FizzBuzz list for 1..n (empty if n is not positive)."""
    if n < 1:
        return []

    out = []
    for i in range(1, n + 1):
        by3 = i % 3 == 0
        by5 = i % 5 == 0
        if by3 and by5:
            out.append("FizzBuzz")
        elif by3:
            out.append("Fizz")
        elif by5:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
