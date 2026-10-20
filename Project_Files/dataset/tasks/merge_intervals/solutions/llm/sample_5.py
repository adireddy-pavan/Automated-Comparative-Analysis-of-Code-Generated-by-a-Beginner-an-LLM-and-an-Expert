from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Merge overlapping or touching intervals and return them sorted by start.

    Uses an index-driven sweep over the sorted intervals. For each new group,
    an inner loop greedily extends the upper bound while subsequent intervals
    keep overlapping the running maximum.
    """
    ordered = sorted(intervals, key=lambda iv: iv[0])
    n = len(ordered)
    merged: List[List[int]] = []

    i = 0
    while i < n:
        start, end = ordered[i]
        j = i + 1
        while j < n and ordered[j][0] <= end:
            end = max(end, ordered[j][1])
            j += 1
        merged.append([start, end])
        i = j

    return merged
