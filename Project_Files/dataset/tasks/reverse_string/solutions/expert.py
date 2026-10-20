"""Reverse a string (expert reference solution)."""
from __future__ import annotations


def reverse_string(s: str) -> str:
    """Return *s* with its characters in reverse order.

    Args:
        s: The string to reverse.

    Returns:
        A new string containing the characters of *s* in reverse order; the
        empty string maps to the empty string.
    """
    return s[::-1]
