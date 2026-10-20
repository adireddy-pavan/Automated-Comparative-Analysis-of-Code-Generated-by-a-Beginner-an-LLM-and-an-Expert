from typing import List, Union

Number = Union[int, float]


def find_max(numbers: List[Number]) -> Number:
    """Return the largest number by sorting a copy of the input.

    Sorting ascending places the maximum at the end of the list. We copy
    the list first so the caller's data is left untouched.
    """
    if not numbers:
        raise ValueError("expected a non-empty list of numbers")
    ordered = sorted(numbers)
    return ordered[-1]
