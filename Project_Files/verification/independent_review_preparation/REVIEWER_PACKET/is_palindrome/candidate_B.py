"""Valid palindrome check (expert reference solution)."""
from __future__ import annotations


def is_palindrome(s: str) -> bool:
    """Return True if *s* is a palindrome, ignoring case and non-alphanumerics.

    Args:
        s: The string to test.

    Returns:
        True when the normalised characters read identically in reverse.
    """
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]
