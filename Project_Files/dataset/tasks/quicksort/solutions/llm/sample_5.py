from typing import List


def quicksort(items: List[int]) -> List[int]:
    """Sort ``items`` ascending with a median-of-three pivot quicksort.

    Picking the median of the first, middle, and last elements as the pivot
    improves the partition balance on common inputs. Returns a new list.
    """
    if len(items) <= 1:
        return list(items)

    first, mid, last = items[0], items[len(items) // 2], items[-1]
    pivot = sorted((first, mid, last))[1]

    below: List[int] = []
    same: List[int] = []
    above: List[int] = []
    for value in items:
        if value < pivot:
            below.append(value)
        elif value > pivot:
            above.append(value)
        else:
            same.append(value)

    return quicksort(below) + same + quicksort(above)
