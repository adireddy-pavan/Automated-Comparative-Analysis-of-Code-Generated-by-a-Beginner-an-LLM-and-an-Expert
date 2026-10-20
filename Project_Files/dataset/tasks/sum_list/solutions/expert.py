"""Sum a list of numbers (expert reference solution)."""
from __future__ import annotations

from numbers import Number
from typing import Sequence


def sum_list(nums: Sequence[Number]) -> Number:
    """Return the arithmetic sum of *nums*.

    Args:
        nums: A sequence of numbers (ints and/or floats).

    Returns:
        The sum of every element, or 0 for an empty sequence.
    """
    return sum(nums)
