from solution import fizzbuzz


def test_core_basic():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_core_fizz():
    assert fizzbuzz(3) == ["1", "2", "Fizz"]


def test_core_fizzbuzz_word():
    assert fizzbuzz(15)[14] == "FizzBuzz"


def test_edge_zero():
    assert fizzbuzz(0) == []


def test_edge_one():
    assert fizzbuzz(1) == ["1"]


def test_edge_negative():
    assert fizzbuzz(-5) == []


def test_edge_buzz():
    assert fizzbuzz(10)[9] == "Buzz"
