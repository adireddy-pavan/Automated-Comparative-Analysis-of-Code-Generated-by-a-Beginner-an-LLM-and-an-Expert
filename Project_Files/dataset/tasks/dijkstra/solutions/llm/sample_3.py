import heapq
from typing import Dict, Hashable


def dijkstra(graph: Dict[Hashable, Dict[Hashable, float]],
             start: Hashable) -> Dict[Hashable, float]:
    """Single-source shortest paths via Dijkstra's algorithm.

    Uses a priority queue plus an explicit ``finalized`` set so each node is
    settled exactly once. Distances start at infinity and are relaxed as
    shorter paths are discovered. Nodes never reached remain at infinity.
    """
    dist: Dict[Hashable, float] = {v: float("inf") for v in graph}
    dist[start] = 0
    finalized = set()
    frontier = [(0.0, start)]

    while frontier:
        d, u = heapq.heappop(frontier)
        if u in finalized:
            continue
        finalized.add(u)
        for v, w in graph[u].items():
            if v not in finalized and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(frontier, (dist[v], v))

    return dist
