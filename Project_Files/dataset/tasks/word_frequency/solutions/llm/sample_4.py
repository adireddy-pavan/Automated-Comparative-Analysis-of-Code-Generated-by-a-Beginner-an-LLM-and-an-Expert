import re
from collections import Counter
from typing import Dict


def word_frequency(text: str) -> Dict[str, int]:
    """Return word -> count for the given ``text``.

    Uses the ``\\w+`` token pattern (letters, digits, underscore) on the
    lower-cased text and lets ``Counter`` aggregate the matches in one
    pass. The result is converted to an ordinary dictionary.
    """
    if not text:
        return {}
    tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return dict(Counter(tokens))
