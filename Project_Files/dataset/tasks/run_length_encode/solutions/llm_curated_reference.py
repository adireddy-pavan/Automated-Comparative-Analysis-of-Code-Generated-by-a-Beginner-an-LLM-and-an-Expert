"""Run-length encoding of a string (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def run_length_encode(s: str) -> str:
    """
    Encode a string using run-length encoding.

    A "run" is a maximal block of the same character repeated one or more
    times. Each run is represented as the character followed by the number of
    times it repeats. For example ``"aaabbc"`` becomes ``"a3b2c1"`` and the
    empty string maps to the empty string.

    Args:
        s: The input string to encode.

    Returns:
        The run-length encoded representation of the input string.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(s, str):
        s = str(s)

    # An empty input has no runs at all, so the encoding is also empty.
    if len(s) == 0:
        return ""

    # Collect each encoded run as a piece, then join at the very end.
    encoded_pieces = []

    # Track the character of the current run and how long it is so far.
    current_character = s[0]
    current_count = 1

    # Start at the second character because the first seeds the first run.
    for character in s[1:]:
        if character == current_character:
            # Still inside the same run, so just extend the count.
            current_count = current_count + 1
        else:
            # The run ended: record it, then start a fresh run.
            encoded_pieces.append(current_character + str(current_count))
            current_character = character
            current_count = 1

    # Flush the final run, which is never recorded inside the loop.
    encoded_pieces.append(current_character + str(current_count))

    # Concatenate all the encoded runs into the final result string.
    return "".join(encoded_pieces)
