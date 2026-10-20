from solution import title_case


def test_core_basic():
    assert title_case("hello world") == "Hello World"


def test_core_three_words():
    assert title_case("the quick brown") == "The Quick Brown"


def test_edge_empty():
    assert title_case("") == ""


def test_edge_single_letter():
    assert title_case("a") == "A"


def test_edge_all_caps():
    assert title_case("HELLO") == "Hello"


def test_edge_mixed_case():
    assert title_case("miXeD cAse") == "Mixed Case"
