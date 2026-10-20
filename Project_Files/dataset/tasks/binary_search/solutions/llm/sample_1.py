from typing import List


def binary_search(items: List[int], target: int) -> int:
    """Return the index of ``target`` in the sorted list ``items``, or -1 if absent.

    Uses the classic iterative two-pointer binary search over a list that is
    assumed to be sorted in ascending order.
    """
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        value = items[mid]
        if value == target:
            return mid
        if value < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
