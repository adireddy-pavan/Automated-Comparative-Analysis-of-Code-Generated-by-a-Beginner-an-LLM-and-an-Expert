from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Return indices of two numbers adding to ``target``, else ``None``.

    Works on a sorted copy of the values (paired with their original
    indices) using the classic two-pointer technique, then normalises the
    result back to ascending original-index order.
    """
    indexed = sorted(enumerate(nums), key=lambda pair: pair[1])
    left, right = 0, len(indexed) - 1
    while left < right:
        total = indexed[left][1] + indexed[right][1]
        if total == target:
            i, j = indexed[left][0], indexed[right][0]
            return (i, j) if i < j else (j, i)
        if total < target:
            left += 1
        else:
            right -= 1
    return None
