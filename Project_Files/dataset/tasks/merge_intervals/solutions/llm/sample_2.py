from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Return the merged set of intervals, sorted by start.

    Builds the output without mutating the running interval in place: each
    overlapping interval replaces the last result entry with a widened copy.
    Touching intervals (``end == next start``) count as overlapping.
    """
    result: List[List[int]] = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            prev_start, prev_end = result[-1]
            result[-1] = [prev_start, max(prev_end, end)]
        else:
            result.append([start, end])
    return result
