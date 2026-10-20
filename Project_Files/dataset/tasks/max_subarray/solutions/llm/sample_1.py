"""Maximum subarray sum using Kadane's algorithm."""

from typing import Sequence


def max_subarray(nums: Sequence[int]) -> int:
    """Return the largest sum of any contiguous, non-empty subarray.

    Implements Kadane's algorithm in a single O(n) pass: ``best_here`` tracks
    the best sum ending at the current position, and ``best`` the best seen
    overall.

    Raises:
        ValueError: if ``nums`` is empty.
    """
    if not nums:
        raise ValueError("input sequence must be non-empty")

    best = best_here = nums[0]
    for value in nums[1:]:
        best_here = max(value, best_here + value)
        best = max(best, best_here)
    return best
