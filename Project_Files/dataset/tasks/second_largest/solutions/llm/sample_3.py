from typing import List, Union

Number = Union[int, float]


def second_largest(numbers: List[Number]) -> Number:
    """Return the second largest distinct value in ``numbers``.

    Find the maximum of the distinct values, then take the maximum of
    everything strictly below it.
    """
    distinct = set(numbers)
    if len(distinct) < 2:
        raise ValueError("at least two distinct values are required")

    top = max(distinct)
    return max(value for value in distinct if value < top)
