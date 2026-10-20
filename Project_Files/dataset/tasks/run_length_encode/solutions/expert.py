"""Run-length encoding of a string (expert reference solution)."""
from __future__ import annotations


def run_length_encode(s: str) -> str:
    """Encode *s* so each run of identical characters becomes char + count.

    For example ``"aaabbc"`` encodes to ``"a3b2c1"``.

    Args:
        s: The string to encode.

    Returns:
        The run-length encoded string; the empty string encodes to "".
    """
    if not s:
        return ""

    parts: list[str] = []
    current = s[0]
    count = 1
    for char in s[1:]:
        if char == current:
            count += 1
        else:
            parts.append(f"{current}{count}")
            current = char
            count = 1
    parts.append(f"{current}{count}")
    return "".join(parts)
