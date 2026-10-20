import heapq
from typing import Dict, Hashable, List, Tuple

INF = float("inf")


def _relax(distances: Dict[Hashable, float],
           heap: List[Tuple[float, Hashable]],
           node: Hashable,
           base_dist: float,
           neighbours: Dict[Hashable, float]) -> None:
    """Relax all outgoing edges of ``node`` and push any improvements."""
    for neighbour, weight in neighbours.items():
        proposed = base_dist + weight
        if proposed < distances[neighbour]:
            distances[neighbour] = proposed
            heapq.heappush(heap, (proposed, neighbour))


def dijkstra(graph: Dict[Hashable, Dict[Hashable, float]],
             start: Hashable) -> Dict[Hashable, float]:
    """Return a mapping of node -> shortest distance from ``start``.

    A fairly verbose, well-factored implementation of Dijkstra's algorithm.
    Edge relaxation is delegated to a helper. Unreachable nodes keep the
    initial value of ``inf``.
    """
    distances: Dict[Hashable, float] = {node: INF for node in graph}
    distances[start] = 0

    heap: List[Tuple[float, Hashable]] = [(0.0, start)]
    while heap:
        current_dist, current = heapq.heappop(heap)

        # Skip if we have already found a strictly better route to this node.
        if current_dist > distances[current]:
            continue

        _relax(distances, heap, current, current_dist, graph[current])

    return distances
