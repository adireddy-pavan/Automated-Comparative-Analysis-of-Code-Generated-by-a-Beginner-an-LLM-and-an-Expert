from typing import Dict, Hashable, Set


def dijkstra(graph: Dict[Hashable, Dict[Hashable, float]],
             start: Hashable) -> Dict[Hashable, float]:
    """Return shortest distances from ``start`` to all nodes (linear-scan variant).

    Instead of a heap, this version repeatedly selects the closest unvisited
    node by scanning the distance table. It is O(V^2) but simple and correct,
    which is fine for small graphs. Unreachable nodes keep an infinite
    distance.
    """
    inf = float("inf")
    distances: Dict[Hashable, float] = {node: inf for node in graph}
    distances[start] = 0
    visited: Set[Hashable] = set()

    while len(visited) < len(graph):
        # Pick the unvisited node with the smallest tentative distance.
        current = None
        current_dist = inf
        for node, dist in distances.items():
            if node not in visited and dist < current_dist:
                current = node
                current_dist = dist

        if current is None:
            break  # remaining nodes are unreachable

        visited.add(current)
        for neighbour, weight in graph[current].items():
            new_dist = current_dist + weight
            if new_dist < distances[neighbour]:
                distances[neighbour] = new_dist

    return distances
