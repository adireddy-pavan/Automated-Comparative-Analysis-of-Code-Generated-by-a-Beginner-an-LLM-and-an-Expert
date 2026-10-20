from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    """Find the common prefix by only comparing the lexicographic extremes.

    After sorting, the smallest and largest strings differ the most, so the
    common prefix of the whole collection equals the common prefix of just
    those two endpoints.
    """
    if not strs:
        return ""

    lowest = min(strs)
    highest = max(strs)

    end = 0
    limit = min(len(lowest), len(highest))
    while end < limit and lowest[end] == highest[end]:
        end += 1
    return lowest[:end]
