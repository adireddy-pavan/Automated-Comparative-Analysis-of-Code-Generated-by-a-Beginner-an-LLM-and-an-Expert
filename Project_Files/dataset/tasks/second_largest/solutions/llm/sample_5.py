from typing import List, Union

Number = Union[int, float]


def second_largest(numbers: List[Number]) -> Number:
    """Return the second largest distinct value in ``numbers``.

    The distinct values are sorted in descending order; the element at
    index 1 is the second largest.
    """
    ranked = sorted(set(numbers), reverse=True)
    if len(ranked) < 2:
        raise ValueError("list does not contain two distinct values")
    return ranked[1]
