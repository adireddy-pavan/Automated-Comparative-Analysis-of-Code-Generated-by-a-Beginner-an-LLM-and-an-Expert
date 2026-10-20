from typing import List, Union

Number = Union[int, float]


def sum_list(numbers: List[Number]) -> Number:
    """Return the sum of all numbers in ``numbers``.

    Delegates to the built-in ``sum``, whose default start value of ``0``
    means an empty list correctly produces ``0``.
    """
    return sum(numbers)
