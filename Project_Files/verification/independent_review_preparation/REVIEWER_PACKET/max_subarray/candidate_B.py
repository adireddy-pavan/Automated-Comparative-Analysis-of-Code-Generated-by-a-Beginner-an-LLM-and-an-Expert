"""Maximum subarray sum via Kadane's algorithm (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def max_subarray(nums: Sequence[int]) -> int:
    """Return the largest sum of any contiguous non-empty subarray.

    Args:
        nums: A non-empty sequence of integers.

    Returns:
        The maximum sum obtainable from a contiguous, non-empty slice.

    Raises:
        ValueError: If *nums* is empty.
    """
    if not nums:
        raise ValueError("nums must be non-empty")

    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
