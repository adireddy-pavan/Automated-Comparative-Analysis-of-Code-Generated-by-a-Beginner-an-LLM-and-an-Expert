import re

# Match any single vowel, ignoring case. 'y' is intentionally not included.
_VOWEL_PATTERN = re.compile(r"[aeiou]", re.IGNORECASE)


def count_vowels(text: str) -> int:
    """Return the count of vowels (a, e, i, o, u) in ``text``.

    Uses a compiled regular expression to find all vowel occurrences and
    returns the length of the resulting match list. Case is ignored via the
    ``IGNORECASE`` flag.
    """
    return len(_VOWEL_PATTERN.findall(text))
