def reverse_string(s: str) -> str:
    """Return ``s`` with its characters in reverse order.

    Uses Python's extended slicing with a step of ``-1``, which is the
    idiomatic and efficient way to reverse a string. An empty string
    simply reverses to an empty string.
    """
    return s[::-1]
