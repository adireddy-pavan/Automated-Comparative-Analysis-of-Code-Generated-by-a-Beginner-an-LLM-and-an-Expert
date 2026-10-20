"""Longest common prefix (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def longest_common_prefix(strs: Sequence[str]) -> str:
    """Return the longest common prefix of all strings in *strs*.

    Comparing the lexicographic minimum and maximum strings is sufficient: any
    prefix common to those two extremes is common to every string between them.

    Args:
        strs: A sequence of strings (possibly empty).

    Returns:
        The longest common prefix, or "" when the sequence is empty or the
        strings share no common prefix.
    """
    if not strs:
        return ""
    lo, hi = min(strs), max(strs)
    for i, ch in enumerate(lo):
        if i >= len(hi) or hi[i] != ch:
            return lo[:i]
    return lo
