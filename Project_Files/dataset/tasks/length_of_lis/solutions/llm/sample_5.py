from typing import List


def length_of_lis(nums: List[int]) -> int:
    """Quadratic DP that also tracks the running maximum length.

    A small variation on the standard ``dp`` approach: instead of taking
    ``max(dp)`` at the end we update a ``best`` counter as we go, which keeps the
    answer correct even for the empty input (where the loop never runs).
    """
    dp: List[int] = []
    best = 0
    for i, value in enumerate(nums):
        run = 1
        for j in range(i):
            if nums[j] < value:
                run = max(run, dp[j] + 1)
        dp.append(run)
        best = max(best, run)
    return best
