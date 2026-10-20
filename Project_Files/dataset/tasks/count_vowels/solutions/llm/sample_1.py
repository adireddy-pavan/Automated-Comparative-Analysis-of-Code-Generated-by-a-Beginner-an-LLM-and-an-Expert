def count_vowels(text: str) -> int:
    """Return the number of vowels (a, e, i, o, u) in ``text``.

    The comparison is case-insensitive; the letter 'y' is not counted as a
    vowel.
    """
    vowels = set("aeiou")
    total = 0
    for char in text.lower():
        if char in vowels:
            total += 1
    return total
