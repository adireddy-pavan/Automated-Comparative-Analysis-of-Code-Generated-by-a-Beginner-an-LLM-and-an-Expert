def reverse_string(s: str) -> str:
    """Return ``s`` reversed character by character.

    Joins the characters produced by the built-in ``reversed`` iterator.
    This expresses the intent clearly without relying on slice syntax and
    handles the empty-string case for free.
    """
    return "".join(reversed(s))
