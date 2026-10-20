from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Find two distinct indices whose values add up to ``target``.

    This brute-force variant compares every unordered pair of positions
    and returns the first one that matches. It is O(n^2) but keeps the
    logic explicit and easy to follow.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
