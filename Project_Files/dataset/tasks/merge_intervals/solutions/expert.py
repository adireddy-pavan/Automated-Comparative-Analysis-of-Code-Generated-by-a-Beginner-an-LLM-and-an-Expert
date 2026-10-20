"""Merge overlapping or touching intervals (expert reference solution)."""
from __future__ import annotations

from typing import List, Sequence


def merge_intervals(intervals: Sequence[Sequence[int]]) -> List[List[int]]:
    """Merge all overlapping or touching intervals.

    Args:
        intervals: A sequence of ``[start, end]`` pairs in any order.

    Returns:
        A new list of merged ``[start, end]`` pairs sorted by start. Intervals
        that overlap or merely touch (``end == next start``) are combined.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged: List[List[int]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged
