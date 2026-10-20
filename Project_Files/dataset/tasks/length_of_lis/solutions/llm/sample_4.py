from functools import lru_cache
from typing import List


def length_of_lis(nums: List[int]) -> int:
    """Top-down memoized recursion for the LIS length.

    ``best(i)`` returns the length of the longest strictly increasing
    subsequence that starts at index ``i``. The overall answer is the maximum
    over every possible starting position.
    """
    if not nums:
        return 0

    n = len(nums)

    @lru_cache(maxsize=None)
    def best(i: int) -> int:
        longest = 1
        for j in range(i + 1, n):
            if nums[j] > nums[i]:
                longest = max(longest, 1 + best(j))
        return longest

    return max(best(i) for i in range(n))
