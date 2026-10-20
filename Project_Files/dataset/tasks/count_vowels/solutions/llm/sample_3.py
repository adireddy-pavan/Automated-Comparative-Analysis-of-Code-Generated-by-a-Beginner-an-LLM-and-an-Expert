from collections import Counter


def count_vowels(text: str) -> int:
    """Return how many vowels appear in ``text`` (case-insensitive).

    Tallies every character with :class:`collections.Counter`, then sums the
    counts for the five vowels. 'y' is deliberately excluded.
    """
    counts = Counter(text.lower())
    return sum(counts[vowel] for vowel in "aeiou")
