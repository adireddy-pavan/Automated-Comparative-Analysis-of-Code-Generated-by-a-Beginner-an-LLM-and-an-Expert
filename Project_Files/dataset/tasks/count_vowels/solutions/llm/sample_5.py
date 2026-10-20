VOWELS = frozenset("aeiouAEIOU")


def count_vowels(text: str) -> int:
    """Count vowels in ``text`` without altering its case.

    Instead of lower-casing the input, both cases of each vowel are stored in a
    frozenset and membership is tested directly. This keeps the hot loop free
    of per-character string allocations.
    """
    count = 0
    for character in text:
        if character in VOWELS:
            count += 1
    return count
