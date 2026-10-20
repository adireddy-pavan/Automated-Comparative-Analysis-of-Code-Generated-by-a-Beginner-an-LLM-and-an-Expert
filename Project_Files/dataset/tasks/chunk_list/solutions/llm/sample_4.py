from typing import List


def chunk_list(items: List, size: int) -> List[List]:
    """Split ``items`` into chunks by accumulating elements one by one.

    Each element is appended to the current chunk; once the chunk reaches
    the requested size it is flushed to the result and a fresh chunk is
    started. Any leftover partial chunk is flushed at the end.
    """
    if size < 1:
        raise ValueError("size must be a positive integer")

    chunks: List[List] = []
    current: List = []
    for item in items:
        current.append(item)
        if len(current) == size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks
