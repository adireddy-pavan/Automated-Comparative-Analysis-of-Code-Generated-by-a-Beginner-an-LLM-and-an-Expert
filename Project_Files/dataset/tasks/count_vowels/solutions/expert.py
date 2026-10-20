"""Vowel counter (expert reference solution)."""
from __future__ import annotations


def count_vowels(s: str) -> int:
    """Return the number of vowels in *s*, case-insensitively.

    Args:
        s: The string to scan. The letter ``y`` is not treated as a vowel.

    Returns:
        The count of characters that are one of ``a``, ``e``, ``i``, ``o``, ``u``
        regardless of case.
    """
    return sum(1 for ch in s.lower() if ch in "aeiou")
