from solution import word_frequency


def test_core_basic():
    assert word_frequency("the cat the dog") == {"the": 2, "cat": 1, "dog": 1}


def test_core_single():
    assert word_frequency("hello") == {"hello": 1}


def test_core_repeat():
    assert word_frequency("a a a") == {"a": 3}


def test_edge_empty():
    assert word_frequency("") == {}


def test_edge_punctuation():
    assert word_frequency("Hi, hi!") == {"hi": 2}


def test_edge_case():
    assert word_frequency("The THE the") == {"the": 3}


def test_edge_mixed():
    assert word_frequency("Cat. cat? CAT!") == {"cat": 3}


def test_edge_numbers():
    assert word_frequency("a1 a1 b2") == {"a1": 2, "b2": 1}
