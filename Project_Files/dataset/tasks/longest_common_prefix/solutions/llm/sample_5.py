from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    """Binary-search the length of the longest common prefix.

    The answer cannot exceed the shortest string. We binary search the prefix
    length: a length is feasible if every string shares the first ``length``
    characters with the first string. We keep the largest feasible length.
    """
    if not strs:
        return ""

    def shared_by_all(length: int) -> bool:
        candidate = strs[0][:length]
        return all(word.startswith(candidate) for word in strs)

    lo, hi = 0, min(len(word) for word in strs)
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if shared_by_all(mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return strs[0][:best]
