from typing import List, Union

Number = Union[int, float]


def sum_list(numbers: List[Number]) -> Number:
    """Return the sum of a list of numbers via recursion.

    Recursively adds the first element to the sum of the remaining slice.
    The base case is the empty list, whose sum is defined as ``0``.
    """
    if not numbers:
        return 0
    return numbers[0] + sum_list(numbers[1:])
