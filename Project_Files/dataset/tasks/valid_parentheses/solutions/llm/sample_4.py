from collections import deque


def valid_parentheses(s: str) -> bool:
    """Validate bracket matching using an explicit deque as a stack.

    Non-bracket characters are ignored. Each opening bracket is pushed and
    each closing bracket must pop its corresponding opener, otherwise the
    input is rejected immediately.
    """
    matching = {")": "(", "]": "[", "}": "{"}
    stack: deque[str] = deque()

    for char in s:
        if char in "([{":
            stack.append(char)
        elif char in matching:
            expected = matching[char]
            if not stack or stack[-1] != expected:
                return False
            stack.pop()
        # other characters are not brackets and are skipped

    return not stack
