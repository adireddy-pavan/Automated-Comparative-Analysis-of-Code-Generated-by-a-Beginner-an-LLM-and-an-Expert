from functools import reduce


def reverse_string(s: str) -> str:
    """Return ``s`` reversed, computed with a functional fold.

    ``functools.reduce`` folds over the characters, prepending each to the
    running accumulator. Starting from an empty string makes the empty
    input case return ``""`` automatically.
    """
    return reduce(lambda acc, char: char + acc, s, "")
