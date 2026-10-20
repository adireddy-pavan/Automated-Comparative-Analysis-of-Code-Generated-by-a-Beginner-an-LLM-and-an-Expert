import math
from typing import List


def chunk_list(items: List, size: int) -> List[List]:
    """Split ``items`` into consecutive chunks of length ``size``.

    Compute how many chunks are needed with a ceiling division, then
    build each chunk by slicing the appropriate window from the list.
    """
    if size < 1:
        raise ValueError("size must be at least 1")

    chunk_count = math.ceil(len(items) / size)
    return [items[i * size:(i + 1) * size] for i in range(chunk_count)]
