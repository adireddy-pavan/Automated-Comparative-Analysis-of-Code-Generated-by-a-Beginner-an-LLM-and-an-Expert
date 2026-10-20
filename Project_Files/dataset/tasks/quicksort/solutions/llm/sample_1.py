from typing import List


def quicksort(items: List[int]) -> List[int]:
    """Return a new list with ``items`` sorted ascending using quicksort.

    This is the classic three-way partition: the first element is chosen as the
    pivot and the rest are split into smaller, equal, and larger buckets, each
    sorted recursively. The input list is not mutated.
    """
    if len(items) <= 1:
        return list(items)

    pivot = items[0]
    smaller = [x for x in items[1:] if x < pivot]
    equal = [x for x in items if x == pivot]
    larger = [x for x in items[1:] if x > pivot]
    return quicksort(smaller) + equal + quicksort(larger)
