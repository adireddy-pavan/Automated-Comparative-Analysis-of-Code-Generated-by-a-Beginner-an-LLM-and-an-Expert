"""Count whitespace-separated words (expert reference solution)."""
from __future__ import annotations


def count_words(s: str) -> int:
    """Return the number of whitespace-separated words in *s*.

    ``str.split()`` with no argument splits on arbitrary runs of whitespace and
    discards empty tokens, so leading/trailing/multiple spaces are handled and a
    blank string yields 0.

    Args:
        s: The input string.

    Returns:
        The count of words in *s*.
    """
    return len(s.split())
