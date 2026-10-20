def is_palindrome(s: str) -> bool:
    """Check if ``s`` is a valid palindrome, ignoring case and symbols."""
    if not isinstance(s, str):
        raise TypeError("input must be a string")

    filtered = "".join(filter(str.isalnum, s)).casefold()
    n = len(filtered)
    for i in range(n // 2):
        if filtered[i] != filtered[n - 1 - i]:
            return False
    return True
