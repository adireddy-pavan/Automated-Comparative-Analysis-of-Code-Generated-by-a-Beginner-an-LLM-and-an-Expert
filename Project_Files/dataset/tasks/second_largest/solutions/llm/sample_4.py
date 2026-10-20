import heapq
from typing import List, Union

Number = Union[int, float]


def second_largest(numbers: List[Number]) -> Number:
    """Return the second largest distinct value via ``heapq.nlargest``.

    After de-duplicating, the two largest distinct values are requested
    and the smaller of the two is the answer.
    """
    distinct = set(numbers)
    if len(distinct) < 2:
        raise ValueError("expected at least two distinct values")
    top_two = heapq.nlargest(2, distinct)
    return top_two[1]
