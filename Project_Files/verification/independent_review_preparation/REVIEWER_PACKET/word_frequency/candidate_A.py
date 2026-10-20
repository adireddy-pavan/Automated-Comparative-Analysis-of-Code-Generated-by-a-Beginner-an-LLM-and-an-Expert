"""Word frequency counting (expert reference solution)."""
from __future__ import annotations

import re
from collections import Counter


def word_frequency(text: str) -> dict[str, int]:
    """Count how often each word appears in *text*.

    A word is a maximal run of alphanumeric characters; comparison is
    case-insensitive, so words are lower-cased before counting and all
    punctuation is ignored.

    Args:
        text: The text to analyse.

    Returns:
        A plain ``dict`` mapping each lower-cased word to its frequency.
    """
    words = re.findall(r"[a-z0-9]+", text.lower())
    return dict(Counter(words))
