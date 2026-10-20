def valid_parentheses(s: str) -> bool:
    """Check that brackets in ``s`` are balanced and properly nested.

    This version pushes opening brackets and, on each closing bracket,
    verifies it matches the most recent unmatched opener via a lookup that
    maps closers to their openers.
    """
    closer_to_opener = {")": "(", "]": "[", "}": "{"}
    openers = set(closer_to_opener.values())
    stack: list[str] = []

    for char in s:
        if char in openers:
            stack.append(char)
        elif char in closer_to_opener:
            if not stack:
                return False
            if stack.pop() != closer_to_opener[char]:
                return False

    return len(stack) == 0
