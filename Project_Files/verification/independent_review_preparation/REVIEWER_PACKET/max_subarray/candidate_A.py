def max_subarray(nums):
    best = 0
    cur = 0
    for x in nums:
        cur = cur + x
        if cur < 0:
            cur = 0
        if cur > best:
            best = cur
    return best
