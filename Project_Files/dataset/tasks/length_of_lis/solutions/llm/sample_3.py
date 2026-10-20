from typing import List


def length_of_lis(nums: List[int]) -> int:
    """LIS length with an explicit binary search over the ``tails`` array.

    This is the same O(n log n) idea as patience sorting, but the lower-bound
    search is written out by hand instead of relying on the ``bisect`` module,
    which makes the strict-increase invariant easy to follow.
    """
    tails: List[int] = []
    for num in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < num:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(num)
        else:
            tails[lo] = num
    return len(tails)
