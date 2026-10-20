from typing import List, Union

Number = Union[int, float]


def find_max(numbers: List[Number]) -> Number:
    """Return the largest number by scanning the list once.

    We keep track of the best value seen so far and update it whenever
    a larger element is encountered. This avoids relying on the built-in
    ``max`` and makes the linear scan explicit.
    """
    if not numbers:
        raise ValueError("cannot find the maximum of an empty list")

    largest = numbers[0]
    for value in numbers[1:]:
        if value > largest:
            largest = value
    return largest
