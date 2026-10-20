def length_of_lis(nums):
    if not nums:
        return 0
    best = 1
    cur = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best
