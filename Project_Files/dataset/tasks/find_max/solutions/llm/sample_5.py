from typing import List, Union

Number = Union[int, float]


def find_max(numbers: List[Number]) -> Number:
    """Return the largest number using a divide-and-conquer recursion."""
    if not numbers:
        raise ValueError("non-empty list required")

    def _max(items: List[Number]) -> Number:
        if len(items) == 1:
            return items[0]
        mid = len(items) // 2
        left = _max(items[:mid])
        right = _max(items[mid:])
        return left if left >= right else right

    return _max(numbers)
