from typing import List, Union

Number = Union[int, float]


def sum_list(numbers: List[Number]) -> Number:
    """Return the total of the values in ``numbers``.

    Accumulates the running total in an explicit loop so the logic is fully
    transparent. The accumulator starts at ``0``, so an empty list yields
    ``0``.
    """
    total: Number = 0
    for value in numbers:
        total += value
    return total
