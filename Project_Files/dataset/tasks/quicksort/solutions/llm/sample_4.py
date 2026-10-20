import random
from typing import List


def quicksort(items: List[int]) -> List[int]:
    """Return a new ascending-sorted list using randomized quicksort.

    Choosing the pivot at random makes worst-case behaviour (already-sorted or
    reverse-sorted input) unlikely. Implemented purely functionally with list
    comprehensions, so nothing is mutated in place.
    """
    if len(items) <= 1:
        return list(items)

    pivot = random.choice(items)
    less = [x for x in items if x < pivot]
    equal = [x for x in items if x == pivot]
    greater = [x for x in items if x > pivot]
    return quicksort(less) + equal + quicksort(greater)
