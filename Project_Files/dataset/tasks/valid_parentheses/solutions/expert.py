"""Valid parentheses matching (expert reference solution)."""
from __future__ import annotations


def valid_parentheses(s: str) -> bool:
    """Return True if every bracket in *s* is correctly matched and nested.

    Args:
        s: A string containing the bracket characters ``()[]{}``.

    Returns:
        True when the brackets close in the correct order, otherwise False.
    """
    closing_to_opening = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for char in s:
        if char in closing_to_opening:
            if not stack or stack.pop() != closing_to_opening[char]:
                return False
        else:
            stack.append(char)
    return not stack
