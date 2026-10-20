from itertools import groupby


def count_words(text: str) -> int:
    """Return the word count by grouping consecutive whitespace/non-whitespace.

    ``itertools.groupby`` collapses the string into alternating groups of
    whitespace and non-whitespace characters. Counting the groups whose
    key is "not whitespace" gives the number of words.
    """
    return sum(1 for is_space, _ in groupby(text, key=str.isspace) if not is_space)
