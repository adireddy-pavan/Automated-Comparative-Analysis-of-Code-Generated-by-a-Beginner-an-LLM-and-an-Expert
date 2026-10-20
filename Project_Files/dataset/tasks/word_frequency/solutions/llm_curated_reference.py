"""Word frequency counting (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def word_frequency(text: str) -> dict[str, int]:
    """
    Build a frequency table of the words appearing in a piece of text.

    A "word" is defined as a maximal run of alphanumeric characters, so any
    punctuation acts as a separator and is otherwise ignored. Counting is
    case-insensitive, which we achieve by lower-casing the text first.

    Args:
        text: The input text to analyse.

    Returns:
        A dictionary mapping each lower-cased word to the number of times it
        occurs in the text.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(text, str):
        text = str(text)

    # Normalise case up front so that "The" and "the" count as one word.
    lowered_text = text.lower()

    # Manually tokenise: accumulate alphanumeric runs, flushing on separators.
    words = []
    current_word_characters = []
    for character in lowered_text:
        if character.isalnum():
            # Still inside a word: keep collecting its characters.
            current_word_characters.append(character)
        else:
            # Hit a separator: if we were building a word, finish it.
            if current_word_characters:
                words.append("".join(current_word_characters))
                current_word_characters = []
    # Flush any trailing word left over at the end of the text.
    if current_word_characters:
        words.append("".join(current_word_characters))

    # Tally the occurrences of each word into a plain dictionary.
    frequencies: dict[str, int] = {}
    for word in words:
        if word in frequencies:
            frequencies[word] = frequencies[word] + 1
        else:
            frequencies[word] = 1

    return frequencies
