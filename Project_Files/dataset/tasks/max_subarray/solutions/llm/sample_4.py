from itertools import accumulate
from typing import List


def max_subarray(nums: List[int]) -> int:
    """Return the maximum contiguous subarray sum.

    Uses the prefix-sum identity: the best subarray ending at index ``i`` is
    ``prefix[i] - min(prefix[:i])``. By scanning prefix sums while tracking
    the minimum prefix seen so far, the answer is found in one O(n) pass.

    Raises:
        ValueError: if ``nums`` is empty.
    """
    if not nums:
        raise ValueError("input must not be empty")

    best = nums[0]
    min_prefix = 0
    for prefix in accumulate(nums):
        best = max(best, prefix - min_prefix)
        min_prefix = min(min_prefix, prefix)
    return best
