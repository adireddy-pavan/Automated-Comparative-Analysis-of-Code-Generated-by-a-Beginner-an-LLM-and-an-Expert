from collections import Counter
from typing import Dict


def word_frequency(text: str) -> Dict[str, int]:
    """Return a dictionary of word counts for ``text``.

    Each token is split on whitespace, lower-cased, and stripped of any
    leading/trailing punctuation so that ``"Hi,"`` and ``"hi!"`` collapse
    to the same word. ``collections.Counter`` does the tallying.
    """
    words = []
    for raw in text.lower().split():
        cleaned = raw.strip(".,!?;:\"'()[]{}-")
        if cleaned:
            words.append(cleaned)
    return dict(Counter(words))
