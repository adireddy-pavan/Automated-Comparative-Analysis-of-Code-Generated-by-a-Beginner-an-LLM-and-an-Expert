from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Merge all overlapping or touching intervals.

    Intervals are first sorted by start. Walking left to right, each interval
    either extends the current merged interval (when it overlaps or touches it)
    or starts a fresh one. The result is returned sorted by start.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged
