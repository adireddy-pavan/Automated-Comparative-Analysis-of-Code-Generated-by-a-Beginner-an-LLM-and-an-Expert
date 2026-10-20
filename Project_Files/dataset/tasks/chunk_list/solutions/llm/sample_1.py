from typing import List


def chunk_list(items: List, size: int) -> List[List]:
    """Split ``items`` into consecutive chunks of length ``size``.

    Iterate over the start indices in steps of ``size`` and slice out a
    window at each one. The final slice is automatically shorter when the
    list does not divide evenly.
    """
    if size < 1:
        raise ValueError("size must be at least 1")
    return [items[start:start + size] for start in range(0, len(items), size)]
