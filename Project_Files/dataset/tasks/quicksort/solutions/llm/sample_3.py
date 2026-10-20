from typing import List


def quicksort(items: List[int]) -> List[int]:
    """Return a sorted copy of ``items`` using an iterative quicksort.

    An explicit stack of ``(low, high)`` ranges replaces recursion, which keeps
    the call depth flat regardless of input size. Uses Hoare-style two-pointer
    partitioning around a middle pivot.
    """
    data = list(items)
    stack = [(0, len(data) - 1)]

    while stack:
        low, high = stack.pop()
        if low >= high:
            continue

        pivot = data[(low + high) // 2]
        left, right = low, high
        while left <= right:
            while data[left] < pivot:
                left += 1
            while data[right] > pivot:
                right -= 1
            if left <= right:
                data[left], data[right] = data[right], data[left]
                left += 1
                right -= 1

        stack.append((low, right))
        stack.append((left, high))

    return data
