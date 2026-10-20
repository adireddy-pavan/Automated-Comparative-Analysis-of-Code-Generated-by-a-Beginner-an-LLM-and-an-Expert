from typing import List


def longest_common_prefix(strs: List[str]) -> str:
    """Return the longest common prefix of all strings via horizontal scanning.

    Start with the first string as the candidate prefix and repeatedly shorten
    it until it is a prefix of the next string. If the candidate becomes empty
    we can stop early -- nothing can be common.
    """
    if not strs:
        return ""
    prefix = strs[0]
    for word in strs[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
