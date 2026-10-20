from solution import dijkstra

INF = float("inf")
GRAPH = {"A": {"B": 1, "C": 4}, "B": {"C": 2, "D": 5}, "C": {"D": 1}, "D": {}}


def test_core_basic():
    assert dijkstra(GRAPH, "A") == {"A": 0, "B": 1, "C": 3, "D": 4}


def test_core_chain():
    assert dijkstra({"X": {"Y": 2}, "Y": {"Z": 3}, "Z": {}}, "X") == {"X": 0, "Y": 2, "Z": 5}


def test_core_direct():
    assert dijkstra({"A": {"B": 10}, "B": {}}, "A") == {"A": 0, "B": 10}


def test_edge_single_node():
    assert dijkstra({"A": {}}, "A") == {"A": 0}


def test_edge_disconnected():
    assert dijkstra({"A": {"B": 1}, "B": {}, "C": {}}, "A") == {"A": 0, "B": 1, "C": INF}


def test_edge_unreachable_from_start():
    assert dijkstra(GRAPH, "D") == {"A": INF, "B": INF, "C": INF, "D": 0}


def test_edge_tie_shorter_path():
    assert dijkstra({"A": {"B": 1, "C": 1}, "B": {"D": 1}, "C": {"D": 1}, "D": {}}, "A") == {"A": 0, "B": 1, "C": 1, "D": 2}
