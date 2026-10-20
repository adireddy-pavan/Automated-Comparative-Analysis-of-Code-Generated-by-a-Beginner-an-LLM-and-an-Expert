"""Binary search over a sorted list (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations

from typing import List


def binary_search(arr: List[int], target: int) -> int:
    """
    Search for ``target`` inside the ascending-sorted list ``arr``.

    Binary search repeatedly halves the remaining search window. At each step we
    look at the middle element and decide whether the target must be in the left
    half, the right half, or exactly at the middle.

    Args:
        arr: A list of values sorted in ascending order.
        target: The value we are trying to find.

    Returns:
        The index of ``target`` if it exists in the list, otherwise ``-1``.
    """
    # Defensive: accept any sequence-like input by materialising it into a list.
    if not isinstance(arr, list):
        arr = list(arr)

    # An empty list cannot contain the target, so report "not found" immediately.
    if len(arr) == 0:
        return -1

    # ``low`` and ``high`` mark the inclusive bounds of the current search window.
    low = 0
    high = len(arr) - 1

    # Keep narrowing the window until it becomes empty.
    while low <= high:
        # Compute the midpoint without risking overflow on very large bounds.
        mid = low + (high - low) // 2
        mid_value = arr[mid]

        if mid_value == target:
            # Found it: return the position where it lives.
            return mid
        elif mid_value < target:
            # The target is larger, so discard the left half (including mid).
            low = mid + 1
        else:
            # The target is smaller, so discard the right half (including mid).
            high = mid - 1

    # The window collapsed without a match, so the target is not present.
    return -1
