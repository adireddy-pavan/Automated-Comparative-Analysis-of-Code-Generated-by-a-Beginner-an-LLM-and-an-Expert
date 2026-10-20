"""Second largest distinct value (expert reference solution)."""
from __future__ import annotations

from typing import Sequence


def second_largest(nums: Sequence[float]) -> float:
    """Return the second largest *distinct* value in *nums*.

    Args:
        nums: A sequence containing at least two distinct values.

    Returns:
        The second largest distinct value (duplicates are collapsed first).

    Raises:
        ValueError: If *nums* has fewer than two distinct values.
    """
    distinct = sorted(set(nums), reverse=True)
    if len(distinct) < 2:
        raise ValueError("need at least two distinct values")
    return distinct[1]
