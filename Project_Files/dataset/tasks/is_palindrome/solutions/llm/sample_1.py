"""Valid-palindrome check by normalising then reversing."""


def is_palindrome(s: str) -> bool:
    """Return ``True`` if ``s`` reads the same forwards and backwards.

    Comparison ignores character case and any non-alphanumeric characters,
    so ``"A man, a plan, a canal: Panama"`` is a palindrome. An empty (or
    fully punctuation) string is treated as a palindrome.
    """
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]
