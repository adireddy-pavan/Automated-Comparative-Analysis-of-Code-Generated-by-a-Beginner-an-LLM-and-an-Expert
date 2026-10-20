"""Title-case a string (expert reference solution)."""
from __future__ import annotations


def title_case(s: str) -> str:
    """Capitalise each space-separated word and lowercase the remaining letters.

    The string is split on single spaces so the original spacing (including empty
    tokens from consecutive spaces) is preserved on re-joining.

    Args:
        s: The input string.

    Returns:
        The title-cased string.
    """
    return " ".join(word.capitalize() for word in s.split(" "))
