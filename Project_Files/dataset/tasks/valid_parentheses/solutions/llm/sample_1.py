def valid_parentheses(s: str) -> bool:
    """Return ``True`` if every bracket in ``s`` is correctly matched.

    A stack holds the closing bracket we expect next. When we meet an
    opening bracket we push its counterpart; when we meet a closing
    bracket it must equal the top of the stack. The string is valid only
    if the stack ends empty.
    """
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []
    for char in s:
        if char in pairs:
            stack.append(pairs[char])
        elif char in (")", "]", "}"):
            if not stack or stack.pop() != char:
                return False
    return not stack
