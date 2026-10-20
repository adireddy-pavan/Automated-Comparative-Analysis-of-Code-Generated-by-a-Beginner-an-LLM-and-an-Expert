def reverse_string(s: str) -> str:
    """Return the reverse of the input string ``s``.

    Builds the result by iterating over the characters and prepending each
    one to an accumulator, which naturally yields the reversed order.
    """
    reversed_chars = ""
    for char in s:
        reversed_chars = char + reversed_chars
    return reversed_chars
