import string


def caesar_cipher(text: str, shift: int) -> str:
    """Apply a Caesar shift to ``text`` using a precomputed translation table.

    Builds rotated copies of the lower- and upper-case alphabets and uses
    :meth:`str.translate` for a single-pass transformation. Non-letters are
    left untouched because they are absent from the table.
    """
    shift %= 26
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    rotated_lower = lower[shift:] + lower[:shift]
    rotated_upper = upper[shift:] + upper[:shift]
    table = str.maketrans(lower + upper, rotated_lower + rotated_upper)
    return text.translate(table)
