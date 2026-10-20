def valid_parentheses(s: str) -> bool:
    """Return whether ``s`` is a well-formed bracket string.

    Repeatedly collapse adjacent matching pairs ("()", "[]", "{}") until
    the string stops shrinking. If nothing is left, the brackets were
    balanced; any remainder means a mismatch.
    """
    previous = None
    current = s
    while current != previous:
        previous = current
        current = current.replace("()", "").replace("[]", "").replace("{}", "")
    return current == ""
