"""Two-sum index lookup (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """
    Find two distinct positions in ``nums`` whose values add up to ``target``.

    The approach is a single pass using a hash map. For each number we ask:
    "have we already seen the value that would complete the pair?" Because we
    only ever look at numbers we have already passed, the two indices are always
    distinct and we never reuse the same element twice.

    Args:
        nums: A list of integers to search through.
        target: The sum we want a pair of values to reach.

    Returns:
        A tuple ``(i, j)`` of indices (with ``i`` < ``j``) whose values sum to
        ``target``, or ``None`` if no such pair exists.
    """
    # Defensive: accept any sequence-like input by materialising it into a list.
    if not isinstance(nums, list):
        nums = list(nums)

    # Maps a previously-seen value to the index where we first saw it.
    seen_value_to_index: Dict[int, int] = {}

    # Walk through the list once, keeping track of where we are.
    for current_index in range(len(nums)):
        current_value = nums[current_index]

        # The value we would need to pair with the current one to hit the target.
        needed_value = target - current_value

        # If we have already encountered that needed value, we found our pair.
        if needed_value in seen_value_to_index:
            earlier_index = seen_value_to_index[needed_value]
            return (earlier_index, current_index)

        # Otherwise remember the current value for future comparisons.
        seen_value_to_index[current_value] = current_index

    # We scanned the whole list without finding a matching pair.
    return None
