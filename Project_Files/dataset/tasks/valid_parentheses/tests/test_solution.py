from solution import valid_parentheses


def test_core_simple():
    assert valid_parentheses("()") is True


def test_core_multi():
    assert valid_parentheses("()[]{}") is True


def test_core_wrong():
    assert valid_parentheses("(]") is False


def test_edge_empty():
    assert valid_parentheses("") is True


def test_edge_interleaved():
    assert valid_parentheses("([)]") is False


def test_edge_unclosed():
    assert valid_parentheses("(") is False


def test_edge_only_close():
    assert valid_parentheses("]") is False


def test_edge_nested():
    assert valid_parentheses("([]{})") is True
