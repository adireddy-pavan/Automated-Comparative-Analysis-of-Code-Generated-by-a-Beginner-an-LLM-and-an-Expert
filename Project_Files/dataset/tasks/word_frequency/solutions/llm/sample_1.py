import re
from typing import Dict


def word_frequency(text: str) -> Dict[str, int]:
    """Count how often each word appears in ``text``.

    Words are extracted as maximal runs of alphanumeric characters using a
    regular expression, lower-cased so that case is ignored, and any
    surrounding punctuation is naturally dropped. Returns a mapping from
    each word to its occurrence count.
    """
    counts: Dict[str, int] = {}
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        counts[word] = counts.get(word, 0) + 1
    return counts
