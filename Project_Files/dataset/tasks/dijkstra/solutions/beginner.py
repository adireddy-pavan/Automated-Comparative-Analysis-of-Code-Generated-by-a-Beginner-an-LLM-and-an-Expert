def dijkstra(graph, start):
    assert start in graph
    dist = {}
    dist[start] = 0
    visited = {}
    while len(visited) < len(dist):
        u = None
        for n in dist:
            if n in visited:
                continue
            if u is None or dist[n] < dist[u]:
                u = n
        if u is None:
            break
        visited[u] = True
        for v in graph[u]:
            nd = dist[u] + graph[u][v]
            if v not in dist or nd < dist[v]:
                dist[v] = nd
    return dist
