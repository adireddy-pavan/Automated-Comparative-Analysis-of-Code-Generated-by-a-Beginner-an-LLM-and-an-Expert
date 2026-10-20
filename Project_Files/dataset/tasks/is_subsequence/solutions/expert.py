"""Subsequence check (expert reference solution)."""
from __future__ import annotations


def is_subsequence(s: str, t: str) -> bool:
    """Return whether *s* is a subsequence of *t*.

    A two-pointer scan advances through *t* once, consuming a character of *s*
    each time it matches; *s* is a subsequence iff every character is consumed.

    Args:
        s: The candidate subsequence.
        t: The string to search within.

    Returns:
        True if *s* is a subsequence of *t*, otherwise False.
    """
    it = iter(t)
    return all(ch in it for ch in s)
