def find_max(nums):
    m = nums[0]
    for x in nums:
        if x > m:
            m = x
    return m
