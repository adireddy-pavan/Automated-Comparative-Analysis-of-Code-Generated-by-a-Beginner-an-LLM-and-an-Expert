def is_subsequence(s: str, t: str) -> bool:
    """Check whether ``s`` can be formed from ``t`` by deleting characters.

    Implemented with an iterator over ``t``: for each character of ``s`` we ask
    whether it appears somewhere in the remaining suffix of ``t``. ``in`` on an
    iterator consumes it up to (and including) the match, which guarantees the
    relative order is preserved.
    """
    it = iter(t)
    return all(ch in it for ch in s)
