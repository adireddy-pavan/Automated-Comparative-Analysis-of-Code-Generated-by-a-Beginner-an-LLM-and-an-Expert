from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    """Vertical scan: compare characters column by column across all strings.

    For each index we look at the character of the first string and confirm
    every other string agrees (and is long enough). The first mismatch -- or
    the end of the shortest string -- marks where the common prefix ends.
    """
    if not strs:
        return ""

    first = strs[0]
    for col, ch in enumerate(first):
        for other in strs[1:]:
            if col >= len(other) or other[col] != ch:
                return first[:col]
    return first
