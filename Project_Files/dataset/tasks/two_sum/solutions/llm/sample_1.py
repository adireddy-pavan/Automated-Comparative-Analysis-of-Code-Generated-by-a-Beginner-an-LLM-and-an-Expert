from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """Return the indices of the first pair of values summing to ``target``.

    A single hash map records each value's index as we scan. For every
    element we check whether its complement has already been seen, which
    gives a single-pass O(n) solution. Returns ``None`` when no pair
    exists. The same element is never reused for both positions.
    """
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return (seen[complement], index)
        seen[value] = index
    return None
