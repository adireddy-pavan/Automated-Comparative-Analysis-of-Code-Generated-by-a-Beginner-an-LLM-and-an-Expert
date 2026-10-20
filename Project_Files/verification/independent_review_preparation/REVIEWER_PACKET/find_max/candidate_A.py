"""Find the maximum of a list (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def find_max(nums: Sequence[float]) -> float:
    """Return the largest element of *nums*.

    Args:
        nums: A non-empty sequence of comparable numbers.

    Returns:
        The maximum value in *nums*.

    Raises:
        ValueError: If *nums* is empty.
    """
    if not nums:
        raise ValueError("find_max() arg is an empty sequence")
    return max(nums)
