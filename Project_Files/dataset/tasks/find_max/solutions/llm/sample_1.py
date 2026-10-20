from typing import List, Union

Number = Union[int, float]


def find_max(numbers: List[Number]) -> Number:
    """Return the largest number in a non-empty list of numbers."""
    if not numbers:
        raise ValueError("find_max() requires a non-empty list")
    return max(numbers)
