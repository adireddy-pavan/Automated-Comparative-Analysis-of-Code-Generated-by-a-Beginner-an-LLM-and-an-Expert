from typing import List


def max_subarray(nums: List[int]) -> int:
    """Return the maximum contiguous subarray sum.

    This variant of Kadane's algorithm resets the running sum to zero
    whenever it drops below zero, since a negative prefix can never improve
    a later subarray. It tracks the best sum separately so all-negative
    inputs still return their largest single element.

    Raises:
        ValueError: when ``nums`` is empty.
    """
    if len(nums) == 0:
        raise ValueError("nums must contain at least one element")

    best = nums[0]
    running = 0
    for value in nums:
        running += value
        if running > best:
            best = running
        if running < 0:
            running = 0
    return best
