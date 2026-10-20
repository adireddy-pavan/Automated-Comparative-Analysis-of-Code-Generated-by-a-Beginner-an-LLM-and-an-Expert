def is_subsequence(s: str, t: str) -> bool:
    """Greedy left-to-right search using ``str.find``.

    Starting just after the previously matched position, locate each character
    of ``s`` in ``t``. If any character is missing in the remaining region the
    search fails immediately.
    """
    pos = 0
    for ch in s:
        found = t.find(ch, pos)
        if found == -1:
            return False
        pos = found + 1
    return True
