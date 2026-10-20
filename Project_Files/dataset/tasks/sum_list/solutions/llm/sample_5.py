import math
from typing import List, Union

Number = Union[int, float]


def sum_list(numbers: List[Number]) -> Number:
    """Return the total of ``numbers``.

    Uses ``math.fsum`` when any floating-point value is present to reduce
    rounding error, and the plain ``sum`` otherwise so integer inputs keep
    their integer type. An empty list returns ``0``.
    """
    if not numbers:
        return 0
    if any(isinstance(value, float) for value in numbers):
        return math.fsum(numbers)
    return sum(numbers)
