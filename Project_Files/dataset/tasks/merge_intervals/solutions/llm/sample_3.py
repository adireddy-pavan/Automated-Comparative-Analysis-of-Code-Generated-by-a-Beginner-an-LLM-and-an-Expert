from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """Merge overlapping or adjacent intervals using an accumulator pair.

    Rather than indexing into the output list, this keeps the currently open
    interval in two local variables and only commits it once a true gap is
    found. The final open interval is flushed at the end.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: (iv[0], iv[1]))
    merged: List[List[int]] = []
    cur_start, cur_end = ordered[0]

    for start, end in ordered[1:]:
        if start <= cur_end:
            cur_end = max(cur_end, end)
        else:
            merged.append([cur_start, cur_end])
            cur_start, cur_end = start, end

    merged.append([cur_start, cur_end])
    return merged
