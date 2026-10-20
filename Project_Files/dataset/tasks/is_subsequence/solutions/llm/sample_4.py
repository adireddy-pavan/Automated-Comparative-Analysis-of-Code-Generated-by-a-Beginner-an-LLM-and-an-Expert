def is_subsequence(s: str, t: str) -> bool:
    """Recursive definition of the subsequence relation.

    Base cases:
      * an empty ``s`` is trivially a subsequence of anything;
      * a non-empty ``s`` cannot fit in an empty ``t``.
    Otherwise, if the leading characters match we consume both, else we drop
    one character from ``t`` and recurse.
    """

    def helper(i: int, j: int) -> bool:
        if i == len(s):
            return True
        if j == len(t):
            return False
        if s[i] == t[j]:
            return helper(i + 1, j + 1)
        return helper(i, j + 1)

    return helper(0, 0)
