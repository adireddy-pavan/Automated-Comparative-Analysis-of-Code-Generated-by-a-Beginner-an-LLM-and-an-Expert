"""Dijkstra single-source shortest paths (expert reference solution)."""
from __future__ import annotations

import heapq
from typing import Dict, Hashable, Mapping


def dijkstra(
    graph: Mapping[Hashable, Mapping[Hashable, float]],
    start: Hashable,
) -> Dict[Hashable, float]:
    """Compute shortest-path distances from *start* to every node.

    Args:
        graph: A mapping ``node -> {neighbour: weight}`` with non-negative
            weights.
        start: The source node to measure distances from.

    Returns:
        A dict mapping every node in *graph* to its shortest distance from
        *start*. The start maps to ``0`` and any unreachable node maps to
        ``float('inf')``.
    """
    distances: Dict[Hashable, float] = {node: float("inf") for node in graph}
    distances[start] = 0.0

    heap: list[tuple[float, Hashable]] = [(0.0, start)]
    while heap:
        current_distance, node = heapq.heappop(heap)
        # Skip stale heap entries superseded by a shorter path already found.
        if current_distance > distances[node]:
            continue
        for neighbour, weight in graph[node].items():
            candidate = current_distance + weight
            if candidate < distances[neighbour]:
                distances[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))

    return distances
