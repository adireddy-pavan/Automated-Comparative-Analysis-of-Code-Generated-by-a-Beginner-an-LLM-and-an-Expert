from solution import longest_common_prefix


def test_core_prefix():
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"


def test_core_none():
    assert longest_common_prefix(["dog", "cat"]) == ""


def test_edge_empty_list():
    assert longest_common_prefix([]) == ""


def test_edge_single():
    assert longest_common_prefix(["a"]) == "a"


def test_edge_identical():
    assert longest_common_prefix(["abc", "abc", "abc"]) == "abc"


def test_edge_empty_string_member():
    assert longest_common_prefix(["", "abc"]) == ""
