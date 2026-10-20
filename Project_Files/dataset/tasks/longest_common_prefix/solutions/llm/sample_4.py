from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    """Compute the common prefix using ``zip`` to walk the columns together.

    ``zip(*strs)`` yields tuples of aligned characters and naturally stops at
    the shortest word. A column contributes to the prefix only while all of its
    characters are identical.
    """
    if not strs:
        return ""

    result = []
    for column in zip(*strs):
        if len(set(column)) == 1:
            result.append(column[0])
        else:
            break
    return "".join(result)
