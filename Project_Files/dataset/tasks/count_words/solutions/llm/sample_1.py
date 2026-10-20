def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``.

    ``str.split()`` with no argument collapses runs of whitespace and
    ignores leading/trailing whitespace, so an empty or whitespace-only
    string naturally yields zero words.
    """
    return len(text.split())
