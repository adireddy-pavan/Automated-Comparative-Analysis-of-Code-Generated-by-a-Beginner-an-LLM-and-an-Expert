from typing import List


def length_of_lis(nums: List[int]) -> int:
    """Length of the longest strictly increasing subsequence (O(n^2) DP).

    ``dp[i]`` is the length of the longest increasing subsequence that ends at
    index ``i``. For each ``i`` we extend the best earlier subsequence whose
    final value is strictly smaller than ``nums[i]``.
    """
    if not nums:
        return 0

    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    return max(dp)
