from collections import defaultdict
from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Return a pair of indices summing to ``target`` or ``None``.

    Build a mapping from each value to the sorted list of indices where it
    occurs, then look for a complementing value. This separates the index
    bookkeeping from the matching logic, which makes the duplicate-value
    case (e.g. ``[3, 3]``) straightforward to reason about.
    """
    if not nums:
        return None

    positions: dict[int, List[int]] = defaultdict(list)
    for idx, val in enumerate(nums):
        positions[val].append(idx)

    for i, value in enumerate(nums):
        complement = target - value
        candidates = positions.get(complement, ())
        for j in candidates:
            if j != i:
                return (i, j) if i < j else (j, i)
    return None
