"""Longest strictly increasing subsequence length (expert reference solution)."""
from __future__ import annotations

from bisect import bisect_left
from typing import Sequence


def length_of_lis(nums: Sequence[int]) -> int:
    """Return the length of the longest strictly increasing subsequence of *nums*.

    Uses the patience-sorting method: ``tails[i]`` holds the smallest possible
    tail of an increasing subsequence of length ``i + 1``. Each value either
    extends ``tails`` or replaces the first tail that is >= it, giving O(n log n).

    Args:
        nums: A sequence of integers.

    Returns:
        The length of the longest strictly increasing subsequence (0 if empty).
    """
    tails: list[int] = []
    for value in nums:
        index = bisect_left(tails, value)
        if index == len(tails):
            tails.append(value)
        else:
            tails[index] = value
    return len(tails)
