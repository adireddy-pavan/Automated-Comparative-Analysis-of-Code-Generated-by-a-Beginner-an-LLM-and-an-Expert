def valid_parentheses(s: str) -> bool:
    """Return ``True`` when the bracket sequence ``s`` is balanced.

    A counter-free stack approach written compactly: we track expected
    closers in a list and short-circuit on the first inconsistency.
    """
    open_for = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in open_for and (not stack or stack.pop() != open_for[ch]):
            return False
    return not stack
