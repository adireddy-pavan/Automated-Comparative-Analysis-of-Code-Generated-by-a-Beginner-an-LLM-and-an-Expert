import re


def count_words(text: str) -> int:
    """Return the count of whitespace-separated words in ``text``.

    A regular expression matches maximal runs of non-whitespace
    characters; the number of matches is the word count. Empty or
    whitespace-only input produces no matches and therefore 0.
    """
    return len(re.findall(r"\S+", text))
