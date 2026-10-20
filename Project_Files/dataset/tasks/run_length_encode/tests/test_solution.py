from solution import run_length_encode


def test_core_basic():
    assert run_length_encode("aaabbc") == "a3b2c1"


def test_core_single_run():
    assert run_length_encode("aaaa") == "a4"


def test_core_alternating():
    assert run_length_encode("ababab") == "a1b1a1b1a1b1"


def test_edge_empty():
    assert run_length_encode("") == ""


def test_edge_single_char():
    assert run_length_encode("a") == "a1"


def test_edge_no_repeats():
    assert run_length_encode("abc") == "a1b1c1"


def test_edge_long_run():
    assert run_length_encode("zzzzzzzzzz") == "z10"
