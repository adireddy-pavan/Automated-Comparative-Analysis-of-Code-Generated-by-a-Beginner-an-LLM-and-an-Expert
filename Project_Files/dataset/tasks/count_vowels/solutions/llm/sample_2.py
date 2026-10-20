def count_vowels(text: str) -> int:
    """Count the vowels in ``text`` case-insensitively.

    Implemented as a single ``sum`` over a generator expression that tests
    each lower-cased character for membership in the vowel set ``aeiou``.
    """
    return sum(1 for ch in text.lower() if ch in "aeiou")
