from typing import List


def binary_search(items: List[int], target: int) -> int:
    """Binary search using a half-open ``[lo, hi)`` interval convention.

    The window shrinks until it is empty. This variant keeps ``hi`` one past
    the last candidate, which avoids any off-by-one handling at the high end.
    """
    lo = 0
    hi = len(items)
    while lo < hi:
        mid = (lo + hi) >> 1
        if items[mid] < target:
            lo = mid + 1
        elif items[mid] > target:
            hi = mid
        else:
            return mid
    return -1
