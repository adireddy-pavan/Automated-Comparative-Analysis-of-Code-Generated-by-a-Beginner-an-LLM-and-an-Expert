import heapq
from typing import Dict, Hashable

Graph = Dict[Hashable, Dict[Hashable, float]]


def dijkstra(graph: Graph, start: Hashable) -> Dict[Hashable, float]:
    """Compute shortest-path distances from ``start`` to every node in ``graph``.

    ``graph`` maps each node to a dict of ``neighbour -> edge_weight``. The
    return value maps every node to its shortest distance from ``start``;
    unreachable nodes (including the case where ``start`` has no outgoing
    edges) map to ``float('inf')``.

    Implementation: classic Dijkstra with a binary min-heap as the priority
    queue. Stale heap entries are skipped via a distance comparison.
    """
    distances: Dict[Hashable, float] = {node: float("inf") for node in graph}
    distances[start] = 0

    heap = [(0, start)]
    while heap:
        current_dist, node = heapq.heappop(heap)
        if current_dist > distances[node]:
            continue  # outdated entry
        for neighbour, weight in graph[node].items():
            candidate = current_dist + weight
            if candidate < distances[neighbour]:
                distances[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))

    return distances
