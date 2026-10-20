"""Quicksort with three-way partitioning (expert reference solution)."""
from __future__ import annotations

from typing import List, Sequence


def quicksort(arr: Sequence[int]) -> List[int]:
    """Return a new list with the elements of *arr* sorted ascending.

    Uses a Dutch-national-flag style three-way partition around a pivot so that
    duplicate values are preserved and handled efficiently.

    Args:
        arr: A sequence of comparable elements.

    Returns:
        A new sorted list; the input is not modified.
    """
    if len(arr) <= 1:
        return list(arr)

    pivot = arr[0]
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return quicksort(less) + equal + quicksort(greater)
