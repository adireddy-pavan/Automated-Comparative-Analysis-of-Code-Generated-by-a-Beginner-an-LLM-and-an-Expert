"""Merge overlapping or touching intervals (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. Each interval is copied
into a fresh list so the caller's input is never mutated.
"""
from __future__ import annotations

from typing import List, Sequence


def merge_intervals(intervals: Sequence[Sequence[int]]) -> List[List[int]]:
    """
    Combine every overlapping or touching interval into the smallest set of
    non-overlapping intervals.

    Two intervals are merged when the next interval starts at or before the end
    of the interval currently being built. This means intervals that merely
    touch at a single point (for example ``[1, 4]`` and ``[4, 5]``) are merged
    into one (``[1, 5]``).

    Args:
        intervals: A sequence of ``[start, end]`` pairs in any order.

    Returns:
        A new list of merged ``[start, end]`` pairs sorted by start value.
    """
    # Defensive: coerce a generic iterable into a concrete list so we can sort
    # and index it safely without consuming a one-shot iterator.
    if not isinstance(intervals, list):
        working = list(intervals)
    else:
        working = intervals

    # An empty input trivially produces an empty result.
    if len(working) == 0:
        return []

    # Step 1: sort the intervals by their start value. Sorting guarantees that
    # any interval able to merge with an earlier one appears immediately after
    # it, so a single left-to-right pass is sufficient.
    sorted_intervals = sorted(working, key=lambda pair: pair[0])

    # Step 2: seed the result with a *copy* of the first interval. Copying keeps
    # the original input untouched even though we mutate entries in `merged`.
    first = sorted_intervals[0]
    merged: List[List[int]] = [[first[0], first[1]]]

    # Step 3: walk through the remaining intervals one by one.
    for current in sorted_intervals[1:]:
        current_start = current[0]
        current_end = current[1]
        last = merged[-1]

        # If the current interval starts at or before the end of the last merged
        # interval, the two overlap or touch and must be combined.
        if current_start <= last[1]:
            # Extend the end only if the current interval reaches further right.
            if current_end > last[1]:
                last[1] = current_end
        else:
            # Otherwise there is a gap, so start a new merged interval (copied).
            merged.append([current_start, current_end])

    return merged
