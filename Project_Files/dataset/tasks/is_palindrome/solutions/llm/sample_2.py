def is_palindrome(s: str) -> bool:
    """Return whether ``s`` is a palindrome ignoring case and punctuation.

    Uses a two-pointer scan over the original string, skipping any
    non-alphanumeric characters and comparing the rest case-insensitively.
    This avoids allocating a separate cleaned copy of the input.
    """
    left, right = 0, len(s) - 1
    while left < right:
        if not s[left].isalnum():
            left += 1
            continue
        if not s[right].isalnum():
            right -= 1
            continue
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
