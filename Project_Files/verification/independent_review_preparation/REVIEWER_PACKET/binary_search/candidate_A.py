"""Binary search over a sorted list (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def binary_search(arr: Sequence[int], target: int) -> int:
    """Return the index of *target* in *arr*, or ``-1`` if it is absent.

    Args:
        arr: A list sorted in ascending order.
        target: The value to locate.

    Returns:
        The index of *target* within *arr*, or ``-1`` when it is not present
        (an empty list naturally yields ``-1``).
    """
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
