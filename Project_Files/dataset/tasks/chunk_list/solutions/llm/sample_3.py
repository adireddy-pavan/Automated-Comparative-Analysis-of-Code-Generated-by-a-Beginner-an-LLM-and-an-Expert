from itertools import islice
from typing import List


def chunk_list(items: List, size: int) -> List[List]:
    """Split ``items`` into consecutive chunks of length ``size``.

    An iterator over the input is repeatedly drained ``size`` elements at
    a time using ``itertools.islice`` until it is exhausted.
    """
    if size < 1:
        raise ValueError("size must be >= 1")

    iterator = iter(items)
    chunks: List[List] = []
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            break
        chunks.append(chunk)
    return chunks
