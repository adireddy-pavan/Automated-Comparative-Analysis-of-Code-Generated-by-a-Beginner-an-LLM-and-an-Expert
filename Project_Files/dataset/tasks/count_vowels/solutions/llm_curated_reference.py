"""Vowel counter (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It lower-cases each
character and checks membership against an explicit set of vowels.
"""
from __future__ import annotations

# The set of vowel characters, stored in lower case for case-insensitive checks.
VOWELS = set("aeiou")


def count_vowels(s: str) -> int:
    """
    Count how many vowels appear in the given string.

    The comparison is case-insensitive, so both ``A`` and ``a`` count as a
    vowel. The letter ``y`` is deliberately excluded because it is treated as a
    consonant for the purposes of this task.

    Args:
        s: The input string to evaluate.

    Returns:
        The total number of vowel characters found in the string.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(s, str):
        s = str(s)

    # Running total of vowels discovered so far.
    vowel_count = 0

    # Inspect each character one at a time.
    for character in s:
        # Normalise to lower case before the membership test.
        lowered_character = character.lower()

        # If the normalised character is one of our known vowels, count it.
        if lowered_character in VOWELS:
            vowel_count += 1

    return vowel_count
