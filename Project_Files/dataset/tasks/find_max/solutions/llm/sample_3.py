from functools import reduce
from typing import List, Union

Number = Union[int, float]


def find_max(numbers: List[Number]) -> Number:
    """Return the largest number using a functional fold."""
    if not numbers:
        raise ValueError("input list must not be empty")
    return reduce(lambda a, b: a if a >= b else b, numbers)
