from typing import List


def chunk_list(items: List, size: int) -> List[List]:
    """Split ``items`` into consecutive chunks of at most ``size`` items.

    A while-loop walks an index forward by ``size`` each iteration,
    appending the slice between the current and next cursor positions.
    """
    if size < 1:
        raise ValueError("chunk size must be a positive integer")

    chunks: List[List] = []
    index = 0
    while index < len(items):
        chunks.append(items[index:index + size])
        index += size
    return chunks
