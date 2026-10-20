from functools import reduce
from typing import List


def _absorb(acc: List[List[int]], interval: List[int]) -> List[List[int]]:
    """Fold one interval into the accumulated, start-sorted result list."""
    start, end = interval
    if acc and start <= acc[-1][1]:
        acc[-1][1] = max(acc[-1][1], end)
    else:
        acc.append([start, end])
    return acc


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Merge overlapping/touching intervals via a functional reduction.

    The intervals are sorted by start and then folded left with ``_absorb``,
    which either extends the trailing interval or appends a new one.
    """
    ordered = sorted(intervals, key=lambda iv: iv[0])
    return reduce(_absorb, ordered, [])
