from typing import List


def _format_word(word: str) -> str:
    """Upper-case the first character of a word and lower-case the rest."""
    if not word:
        return word
    return word[0].upper() + word[1:].lower()


def title_case(text: str) -> str:
    """Return ``text`` with every space-separated word in title case.

    The string is split on single spaces, each word is reformatted, and
    the words are rejoined so the spacing is unchanged.
    """
    words: List[str] = text.split(" ")
    formatted = [_format_word(word) for word in words]
    return " ".join(formatted)
