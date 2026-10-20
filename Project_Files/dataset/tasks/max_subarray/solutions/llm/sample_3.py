"""Maximum subarray sum via divide and conquer.

The array is split in half; the answer is the best of:
  * the maximum subarray entirely in the left half,
  * the maximum subarray entirely in the right half,
  * the maximum subarray crossing the midpoint.

This runs in O(n log n), which is asymptotically slower than Kadane but is
a well-known alternative formulation.
"""

from typing import List


def _max_crossing(nums: List[int], lo: int, mid: int, hi: int) -> int:
    """Best sum of a subarray that must include ``nums[mid]`` and ``nums[mid+1]``."""
    left_best = float("-inf")
    total = 0
    for i in range(mid, lo - 1, -1):
        total += nums[i]
        left_best = max(left_best, total)

    right_best = float("-inf")
    total = 0
    for i in range(mid + 1, hi + 1):
        total += nums[i]
        right_best = max(right_best, total)

    return int(left_best + right_best)


def _solve(nums: List[int], lo: int, hi: int) -> int:
    if lo == hi:
        return nums[lo]
    mid = (lo + hi) // 2
    return max(
        _solve(nums, lo, mid),
        _solve(nums, mid + 1, hi),
        _max_crossing(nums, lo, mid, hi),
    )


def max_subarray(nums: List[int]) -> int:
    """Return the largest contiguous non-empty subarray sum.

    Raises:
        ValueError: if ``nums`` is empty.
    """
    if not nums:
        raise ValueError("cannot compute maximum subarray of an empty list")
    return _solve(nums, 0, len(nums) - 1)
