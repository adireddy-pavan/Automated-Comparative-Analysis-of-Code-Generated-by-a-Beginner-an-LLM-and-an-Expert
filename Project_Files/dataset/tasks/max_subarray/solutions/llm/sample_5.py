from functools import reduce
from typing import List, Tuple


def max_subarray(nums: List[int]) -> int:
    """Return the largest sum of a contiguous, non-empty subarray.

    A functional take on Kadane's algorithm: ``reduce`` folds the list into a
    ``(best_ending_here, best_overall)`` pair, updating both at each step.

    Raises:
        ValueError: when ``nums`` is empty.
    """
    if not nums:
        raise ValueError("nums is empty")

    def step(state: Tuple[int, int], value: int) -> Tuple[int, int]:
        ending_here, overall = state
        ending_here = max(value, ending_here + value)
        return ending_here, max(overall, ending_here)

    _, result = reduce(step, nums[1:], (nums[0], nums[0]))
    return result
