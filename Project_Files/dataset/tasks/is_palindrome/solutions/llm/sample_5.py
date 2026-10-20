"""Palindrome check using a normalised deque compared from both ends."""

from collections import deque


def is_palindrome(s: str) -> bool:
    """Return ``True`` if ``s`` is a palindrome.

    Only alphanumeric characters are considered and the comparison is
    case-insensitive. The cleaned characters are loaded into a deque and
    consumed from both ends until at most one element remains.
    """
    chars = deque(ch for ch in s.lower() if ch.isalnum())
    while len(chars) > 1:
        if chars.popleft() != chars.pop():
            return False
    return True
