def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to its integer value.

    Builds a list of symbol values first, then sums them while flipping the
    sign of any value that is strictly less than its successor.
    """
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    nums = [values[ch] for ch in s]
    result = nums[-1] if nums else 0
    for left, right in zip(nums, nums[1:]):
        result += left if left >= right else -left
    return result
