from typing import List, Sequence


def binary_search(items: Sequence[int], target: int) -> int:
    """Recursively locate ``target`` in a sorted sequence.

    Returns the matching index, or -1 when the value is not present. The
    recursion narrows an inclusive ``[low, high]`` window on each call.
    """

    def search(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = low + (high - low) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            return search(mid + 1, high)
        else:
            return search(low, mid - 1)

    return search(0, len(items) - 1)
