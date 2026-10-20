from typing import List


def quicksort(items: List[int]) -> List[int]:
    """Sort ``items`` ascending and return a new list (in-place quicksort).

    Works on a defensive copy using the Lomuto partition scheme with an
    explicit recursive helper, so the caller's list is left untouched.
    """
    data = list(items)

    def _partition(lo: int, hi: int) -> int:
        pivot = data[hi]
        i = lo
        for j in range(lo, hi):
            if data[j] <= pivot:
                data[i], data[j] = data[j], data[i]
                i += 1
        data[i], data[hi] = data[hi], data[i]
        return i

    def _sort(lo: int, hi: int) -> None:
        if lo < hi:
            p = _partition(lo, hi)
            _sort(lo, p - 1)
            _sort(p + 1, hi)

    _sort(0, len(data) - 1)
    return data
