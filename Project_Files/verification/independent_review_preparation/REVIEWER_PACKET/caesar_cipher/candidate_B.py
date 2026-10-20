"""Caesar cipher shift (expert reference solution)."""
from __future__ import annotations


def caesar_cipher(text: str, shift: int) -> str:
    """Shift each letter of *text* by *shift* positions within its own case.

    Alphabetic characters wrap around within their case (so ``z`` shifted by 1
    becomes ``a`` and ``Z`` becomes ``A``); every non-letter is copied
    unchanged. The shift may be negative or larger than 26.

    Args:
        text: The string to encipher.
        shift: The number of positions to rotate each letter by.

    Returns:
        The enciphered string, the same length as *text*.
    """
    result: list[str] = []
    for ch in text:
        if "a" <= ch <= "z":
            base = ord("a")
        elif "A" <= ch <= "Z":
            base = ord("A")
        else:
            result.append(ch)
            continue
        result.append(chr((ord(ch) - base + shift) % 26 + base))
    return "".join(result)
