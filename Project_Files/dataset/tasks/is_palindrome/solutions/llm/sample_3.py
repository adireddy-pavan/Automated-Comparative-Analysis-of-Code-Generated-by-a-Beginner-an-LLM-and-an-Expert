"""Palindrome validation using a regular expression for normalisation.

The regex strips every character that is not a letter or digit before the
forward/backward comparison, which keeps the intent compact and explicit.
"""

import re

_NON_ALNUM = re.compile(r"[^a-z0-9]")


def is_palindrome(s: str) -> bool:
    """Return ``True`` when ``s`` is a palindrome (case/punctuation agnostic)."""
    normalised = _NON_ALNUM.sub("", s.lower())
    return normalised == normalised[::-1]
