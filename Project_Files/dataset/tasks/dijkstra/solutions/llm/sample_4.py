import heapq
from typing import Any, Dict


def dijkstra(graph: Dict[Any, Dict[Any, float]], start: Any) -> Dict[Any, float]:
    """Compute the shortest distance from ``start`` to each node.

    This variant discovers distances lazily: the result dict starts empty and a
    node's distance is recorded the first time it is popped from the min-heap
    (which guarantees the smallest distance). After the search, any node from
    the graph that was never settled is filled in with infinity.
    """
    settled: Dict[Any, float] = {}
    pq = [(0.0, start)]

    while pq:
        d, node = heapq.heappop(pq)
        if node in settled:
            continue
        settled[node] = d
        for neighbour, weight in graph.get(node, {}).items():
            if neighbour not in settled:
                heapq.heappush(pq, (d + weight, neighbour))

    # Ensure every node in the graph appears in the output.
    return {node: settled.get(node, float("inf")) for node in graph}
