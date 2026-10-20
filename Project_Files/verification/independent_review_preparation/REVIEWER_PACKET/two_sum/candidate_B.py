"""Two-sum index lookup (expert reference solution)."""
from __future__ import annotations

from typing import Optional, Sequence, Tuple


def two_sum(nums: Sequence[int], target: int) -> Optional[Tuple[int, int]]:
    """Return the indices of two values in *nums* that sum to *target*.

    Args:
        nums: A list of integers.
        target: The desired sum of the two selected values.

    Returns:
        A tuple ``(i, j)`` with ``i < j`` and ``nums[i] + nums[j] == target``,
        or ``None`` when no such pair exists.
    """
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return (seen[complement], index)
        seen[value] = index
    return None
