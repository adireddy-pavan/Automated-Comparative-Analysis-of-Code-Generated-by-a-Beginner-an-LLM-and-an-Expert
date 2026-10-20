"""Quicksort (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the explanatory,
step-by-step style typical of an LLM coding assistant. It partitions the input
into three buckets (less-than, equal-to, greater-than the pivot) so that
duplicate values are never lost.
"""
from __future__ import annotations

from typing import List, Sequence


def quicksort(arr: Sequence[int]) -> List[int]:
    """
    Sort the elements of *arr* into ascending order and return a new list.

    The algorithm picks the first element as the pivot and splits the remaining
    elements into three groups:

    * ``less``    -- elements strictly smaller than the pivot,
    * ``equal``   -- elements equal to the pivot (including the pivot itself),
    * ``greater`` -- elements strictly larger than the pivot.

    The ``less`` and ``greater`` groups are sorted recursively, and the three
    groups are concatenated. Keeping an explicit ``equal`` group ensures that
    duplicate values are preserved rather than dropped.

    Args:
        arr: A sequence of comparable elements.

    Returns:
        A brand-new list containing the same elements in ascending order.
    """
    # Defensive: coerce a generic iterable into a concrete list so indexing and
    # repeated iteration are safe.
    if not isinstance(arr, list):
        items: List[int] = list(arr)
    else:
        items = list(arr)

    # Base case: a list of length 0 or 1 is already sorted.
    if len(items) <= 1:
        return items

    # Step 1: choose a pivot. The first element is a simple, deterministic pick.
    pivot = items[0]

    # Step 2: distribute every element into one of three buckets.
    less: List[int] = []
    equal: List[int] = []
    greater: List[int] = []
    for value in items:
        if value < pivot:
            less.append(value)
        elif value > pivot:
            greater.append(value)
        else:
            # value == pivot; collecting these preserves duplicates.
            equal.append(value)

    # Step 3: recursively sort the outer buckets and stitch everything together.
    sorted_less = quicksort(less)
    sorted_greater = quicksort(greater)
    return sorted_less + equal + sorted_greater
