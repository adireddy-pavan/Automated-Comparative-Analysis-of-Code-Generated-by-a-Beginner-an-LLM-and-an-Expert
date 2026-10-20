def count_words(text: str) -> int:
    """Return the number of words by scanning the characters manually.

    We walk through the string and increment a counter every time we
    transition from whitespace into a non-whitespace character. This is
    the start of a new word.
    """
    count = 0
    in_word = False
    for char in text:
        if char.isspace():
            in_word = False
        elif not in_word:
            in_word = True
            count += 1
    return count
