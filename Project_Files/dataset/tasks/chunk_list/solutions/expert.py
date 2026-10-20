"""Split a list into fixed-size chunks (expert reference solution)."""
from __future__ import annotations

from typing import Any, Sequence


def chunk_list(items: Sequence[Any], size: int) -> list[list[Any]]:
    """Split *items* into consecutive chunks of length *size*.

    Args:
        items: The sequence to split.
        size: Chunk length (must be a positive integer).

    Returns:
        A list of chunks; the final chunk is shorter when *items* does not divide
        evenly, and an empty input yields an empty list.

    Raises:
        ValueError: If *size* is not a positive integer.
    """
    if size < 1:
        raise ValueError("size must be a positive integer")
    return [list(items[i:i + size]) for i in range(0, len(items), size)]
