"""Valid palindrome check (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def is_palindrome(s: str) -> bool:
    """
    Determine whether the given string is a palindrome.

    The comparison ignores character case and skips any character that is not
    alphanumeric (for example spaces and punctuation), which is the common
    definition used in interview-style problems.

    Args:
        s: The input string to evaluate.

    Returns:
        True if the normalised string reads the same forwards and backwards,
        otherwise False.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(s, str):
        s = str(s)

    # Step 1: normalise — keep only alphanumeric characters, lower-cased.
    normalised_characters = []
    for character in s:
        if character.isalnum():
            normalised_characters.append(character.lower())

    # Step 2: build the reverse for an explicit comparison.
    forward_sequence = normalised_characters
    backward_sequence = list(reversed(normalised_characters))

    # Step 3: an empty (or fully stripped) string is treated as a palindrome.
    if len(forward_sequence) == 0:
        return True

    # Step 4: compare the normalised sequence against its reverse.
    return forward_sequence == backward_sequence
