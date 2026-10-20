"""Dijkstra single-source shortest paths (LLM-style reference solution).

This solution is intentionally verbose and defensive, mirroring the
explanatory, step-by-step style typical of an LLM coding assistant.
"""
from __future__ import annotations

from typing import Dict, Hashable, Mapping


def dijkstra(
    graph: Mapping[Hashable, Mapping[Hashable, float]],
    start: Hashable,
) -> Dict[Hashable, float]:
    """
    Find the shortest distance from a start node to every node in a graph.

    The algorithm repeatedly selects the unvisited node with the smallest
    known distance, marks it as finalised, and then "relaxes" each of its
    outgoing edges (updating a neighbour's distance whenever a shorter route
    through the current node is discovered). Because all weights are
    non-negative, once a node is selected its distance is final.

    Args:
        graph: A mapping ``node -> {neighbour: weight}`` with non-negative
            weights.
        start: The source node to measure all distances from.

    Returns:
        A dictionary mapping every node in the graph to its shortest distance
        from ``start``; the start node maps to ``0`` and unreachable nodes map
        to ``float('inf')``.
    """
    # Defensive: coerce a non-mapping graph into a dict so we never crash.
    if not isinstance(graph, dict):
        graph = dict(graph)

    # Step 1: initialise every node's distance to infinity ("unknown").
    distances: Dict[Hashable, float] = {}
    for node in graph:
        distances[node] = float("inf")

    # The start node is zero distance away from itself.
    distances[start] = 0.0

    # Track which nodes have had their final shortest distance determined.
    visited: Dict[Hashable, bool] = {}

    # Step 2: keep going until every node has been finalised.
    while len(visited) < len(distances):
        # Find the unvisited node with the smallest tentative distance.
        current_node = None
        current_best = float("inf")
        for node in distances:
            if node in visited:
                continue
            if distances[node] <= current_best:
                current_best = distances[node]
                current_node = node

        # If every remaining node is unreachable, there is nothing left to do.
        if current_node is None or current_best == float("inf"):
            break

        # Mark this node as finalised.
        visited[current_node] = True

        # Step 3: relax each outgoing edge from the current node.
        for neighbour, weight in graph[current_node].items():
            candidate_distance = distances[current_node] + weight
            # Only update if we found a strictly shorter path.
            if candidate_distance < distances[neighbour]:
                distances[neighbour] = candidate_distance

    return distances
