def reverse_string(s: str) -> str:
    """Return the reversed form of ``s`` using index arithmetic.

    Walks the string from the last index down to the first, collecting the
    characters into a list and joining them at the end. Returns an empty
    string unchanged.
    """
    chars = []
    for i in range(len(s) - 1, -1, -1):
        chars.append(s[i])
    return "".join(chars)
