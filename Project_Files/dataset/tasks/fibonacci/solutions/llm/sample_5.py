"""Fibonacci numbers via integer matrix exponentiation.

Raising the matrix [[1, 1], [1, 0]] to the n-th power yields F(n) in its
top-right entry, giving an O(log n) algorithm through fast exponentiation.
"""

from typing import List

Matrix = List[List[int]]


def _multiply(x: Matrix, y: Matrix) -> Matrix:
    """Multiply two 2x2 integer matrices."""
    return [
        [
            x[0][0] * y[0][0] + x[0][1] * y[1][0],
            x[0][0] * y[0][1] + x[0][1] * y[1][1],
        ],
        [
            x[1][0] * y[0][0] + x[1][1] * y[1][0],
            x[1][0] * y[0][1] + x[1][1] * y[1][1],
        ],
    ]


def _matrix_power(base: Matrix, exponent: int) -> Matrix:
    """Return ``base`` raised to ``exponent`` by binary exponentiation."""
    result: Matrix = [[1, 0], [0, 1]]  # identity matrix
    while exponent > 0:
        if exponent & 1:
            result = _multiply(result, base)
        base = _multiply(base, base)
        exponent >>= 1
    return result


def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number using matrix exponentiation.

    Raises:
        ValueError: if ``n`` is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if n == 0:
        return 0
    powered = _matrix_power([[1, 1], [1, 0]], n)
    return powered[0][1]
