"""Caesar cipher shift (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def shift_char(character: str, shift: int) -> str:
    """
    Shift a single character by ``shift`` positions, wrapping within its case.

    Lower-case and upper-case letters are each rotated inside their own 26
    letter alphabet, so the result is always a letter of the same case. Any
    character that is not an ASCII letter is returned completely unchanged.

    Args:
        character: A single-character string to shift.
        shift: The number of alphabet positions to rotate by.

    Returns:
        The shifted character (or the original character if it is not a letter).
    """
    # Handle lower-case letters: rotate within 'a'..'z'.
    if "a" <= character <= "z":
        alphabet_start = ord("a")
        offset = ord(character) - alphabet_start
        # The modulo keeps us inside 0..25 even for negative or large shifts.
        new_offset = (offset + shift) % 26
        return chr(alphabet_start + new_offset)

    # Handle upper-case letters: rotate within 'A'..'Z'.
    if "A" <= character <= "Z":
        alphabet_start = ord("A")
        offset = ord(character) - alphabet_start
        new_offset = (offset + shift) % 26
        return chr(alphabet_start + new_offset)

    # Anything else (digits, spaces, punctuation) is left untouched.
    return character


def caesar_cipher(text: str, shift: int) -> str:
    """
    Encipher a string using a Caesar shift cipher.

    Each alphabetic character is shifted by ``shift`` positions, wrapping
    around within its own case, while non-letters such as spaces and
    punctuation are preserved exactly where they are.

    Args:
        text: The input string to encipher.
        shift: The integer amount to shift each letter by (may be negative).

    Returns:
        A new string of the same length with every letter shifted.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(text, str):
        text = str(text)

    # Build the enciphered text one character at a time for clarity.
    shifted_characters = []
    for character in text:
        # Delegate the per-character logic to the helper above.
        shifted_characters.append(shift_char(character, shift))

    # Join the individual characters back into a single string.
    return "".join(shifted_characters)
