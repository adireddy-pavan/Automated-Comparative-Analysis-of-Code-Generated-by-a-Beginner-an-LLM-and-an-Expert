from typing import List, Union

Number = Union[int, float]


def second_largest(numbers: List[Number]) -> Number:
    """Return the second largest distinct value in ``numbers``.

    Duplicates are removed by converting to a set, the distinct values
    are sorted ascending, and the second-from-last element is returned.
    """
    distinct = sorted(set(numbers))
    if len(distinct) < 2:
        raise ValueError("need at least two distinct values")
    return distinct[-2]
