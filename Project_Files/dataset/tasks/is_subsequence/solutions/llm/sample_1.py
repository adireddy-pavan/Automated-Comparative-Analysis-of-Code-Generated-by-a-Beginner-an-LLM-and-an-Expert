def is_subsequence(s: str, t: str) -> bool:
    """Return True if ``s`` is a subsequence of ``t``.

    Uses the classic two-pointer scan: walk through ``t`` once and advance a
    pointer into ``s`` whenever the current characters match. ``s`` is a
    subsequence exactly when every character of ``s`` gets matched in order.
    """
    i = 0  # next character of s we still need to find
    n = len(s)
    for ch in t:
        if i < n and s[i] == ch:
            i += 1
    return i == n
