import bisect
from typing import List


def binary_search(items: List[int], target: int) -> int:
    """Return the index of ``target`` in ``items`` (ascending) or -1 if missing.

    Delegates the heavy lifting to :func:`bisect.bisect_left`, then verifies
    that the candidate position actually holds the target value.
    """
    index = bisect.bisect_left(items, target)
    if index < len(items) and items[index] == target:
        return index
    return -1
