"""Valid parentheses matching (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations


def valid_parentheses(s: str) -> bool:
    """
    Determine whether a string of brackets is correctly matched and nested.

    Every opening bracket must be closed by the same type of bracket, and the
    brackets must close in the correct order (most recently opened closes
    first), which is exactly the behaviour modelled by a stack.

    Args:
        s: The input string consisting of the bracket characters ``()[]{}``.

    Returns:
        True if the brackets are balanced and properly nested, else False.
    """
    # Defensive: coerce a non-string input to a string so we never crash.
    if not isinstance(s, str):
        s = str(s)

    # Map each closing bracket to the opening bracket it must match.
    matching_pairs = {
        ")": "(",
        "]": "[",
        "}": "{",
    }

    # Use a list as a stack of the opening brackets seen so far.
    open_bracket_stack = []

    # Walk through every character one at a time.
    for character in s:
        if character in matching_pairs:
            # This is a closing bracket. There must be a matching opener on top.
            if len(open_bracket_stack) == 0:
                # Nothing is open, so this close cannot be matched.
                return False
            most_recent_open = open_bracket_stack.pop()
            if most_recent_open != matching_pairs[character]:
                # The top of the stack is the wrong kind of bracket.
                return False
        else:
            # Treat anything else as an opening bracket and remember it.
            open_bracket_stack.append(character)

    # Valid only if every opener was eventually closed (stack is empty).
    return len(open_bracket_stack) == 0
