"""Tests for the Valid Palindrome task.

Imports the candidate as ``from solution import is_palindrome`` (the harness
copies each source file in as ``solution.py``).
"""
from solution import is_palindrome


# --------------------------- CORE behaviour --------------------------------- #
def test_core_simple_true():
    assert is_palindrome("racecar") is True


def test_core_simple_false():
    assert is_palindrome("hello") is False


def test_core_case_insensitive():
    assert is_palindrome("Madam") is True


def test_core_spaces_and_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


# --------------------------- EDGE behaviour --------------------------------- #
def test_edge_empty_string():
    # An empty string is conventionally a palindrome.
    assert is_palindrome("") is True


def test_edge_single_character():
    assert is_palindrome("a") is True


def test_edge_digits_only():
    assert is_palindrome("12321") is True


def test_edge_only_punctuation_cleans_to_empty():
    assert is_palindrome(".,!?") is True


def test_edge_alphanumeric_mixed():
    # Classic tricky case: "0P" is not a palindrome (0 != p).
    assert is_palindrome("0P") is False
