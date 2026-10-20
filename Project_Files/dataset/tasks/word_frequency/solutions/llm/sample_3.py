import string
from collections import defaultdict
from typing import Dict


def word_frequency(text: str) -> Dict[str, int]:
    """Build a frequency map of the words in ``text``.

    Punctuation is removed by translating every punctuation character to a
    space, after which the text is lower-cased and split on whitespace. A
    ``defaultdict`` accumulates the per-word counts, returned as a plain
    ``dict``.
    """
    translation = str.maketrans(string.punctuation, " " * len(string.punctuation))
    normalised = text.translate(translation).lower()

    counts: Dict[str, int] = defaultdict(int)
    for word in normalised.split():
        counts[word] += 1
    return dict(counts)
