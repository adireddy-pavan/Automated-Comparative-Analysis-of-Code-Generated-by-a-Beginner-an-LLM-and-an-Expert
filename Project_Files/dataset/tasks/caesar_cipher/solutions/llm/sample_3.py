def _shift_char(char: str, shift: int) -> str:
    """Shift a single character within its alphabet case, leaving others as-is."""
    if char.isupper():
        return chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
    if char.islower():
        return chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
    return char


def caesar_cipher(text: str, shift: int) -> str:
    """Return ``text`` with every alphabetic character Caesar-shifted.

    The work is factored into a per-character helper so the top-level function
    is just a comprehension. Shifts of any sign or magnitude are supported.
    """
    normalized = shift % 26
    return "".join(_shift_char(c, normalized) for c in text)
