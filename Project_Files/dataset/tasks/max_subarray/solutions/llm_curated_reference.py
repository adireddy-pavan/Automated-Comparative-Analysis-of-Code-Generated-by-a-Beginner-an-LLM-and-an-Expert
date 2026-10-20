"""Maximum subarray sum (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It implements Kadane's
algorithm with explicit running totals and careful edge-case handling.
"""
from __future__ import annotations

from typing import List, Sequence


def max_subarray(nums: Sequence[int]) -> int:
    """
    Compute the largest possible sum of a contiguous, non-empty subarray.

    The function uses Kadane's algorithm. At every position we decide whether to
    extend the current running subarray or to start a brand new one beginning at
    the current element, always keeping track of the best total seen so far.

    Args:
        nums: A non-empty sequence of integers to scan.

    Returns:
        The maximum sum achievable from any contiguous, non-empty subarray.

    Raises:
        ValueError: If the provided sequence contains no elements.
    """
    # Defensive: coerce a generic iterable / non-list input into a concrete list
    # so that indexing and slicing below behave predictably.
    if not isinstance(nums, list):
        values: List[int] = list(nums)
    else:
        values = nums

    # An empty input has no contiguous non-empty subarray, so we reject it.
    if len(values) == 0:
        raise ValueError("nums must be non-empty")

    # Step 1: seed both the running total and the best total with the first
    # element. This guarantees correctness for all-negative inputs, where the
    # answer is simply the single largest (least negative) element.
    current_sum = values[0]
    best_sum = values[0]

    # Step 2: walk through the remaining elements one at a time.
    for index in range(1, len(values)):
        element = values[index]

        # Either continue the existing subarray by adding this element, or
        # abandon it and start fresh from this element -- whichever is larger.
        if current_sum + element > element:
            current_sum = current_sum + element
        else:
            current_sum = element

        # Update the global best whenever the running total improves on it.
        if current_sum > best_sum:
            best_sum = current_sum

    return best_sum
