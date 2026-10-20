from typing import List, Optional


def _find(items: List[int], target: int) -> Optional[int]:
    """Return the index of target, or None if it is not in the list."""
    left, right = 0, len(items) - 1
    while left <= right:
        middle = (left + right) // 2
        candidate = items[middle]
        if candidate == target:
            return middle
        # Discard the half that cannot contain the target.
        if target > candidate:
            left = middle + 1
        else:
            right = middle - 1
    return None


def binary_search(items: List[int], target: int) -> int:
    """Locate ``target`` in a sorted ascending list.

    Returns the zero-based index of the first matching element, or -1 when the
    target is absent. Wraps an internal helper that uses ``None`` as its
    "not found" sentinel for clarity.
    """
    result = _find(items, target)
    return -1 if result is None else result
