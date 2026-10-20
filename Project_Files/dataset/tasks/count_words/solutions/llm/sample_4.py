def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``."""
    words = [token for token in text.split() if token]
    return len(words)
