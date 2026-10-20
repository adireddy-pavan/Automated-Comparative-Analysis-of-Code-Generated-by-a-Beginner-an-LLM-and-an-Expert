import bisect
from typing import List


def length_of_lis(nums: List[int]) -> int:
    """Patience-sorting LIS in O(n log n) using ``bisect``.

    ``tails[k]`` holds the smallest possible tail value of an increasing
    subsequence of length ``k + 1``. For each number we replace the first tail
    that is >= it (keeping subsequences strictly increasing); if none exists the
    number extends the longest run found so far.
    """
    tails: List[int] = []
    for num in nums:
        idx = bisect.bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)
