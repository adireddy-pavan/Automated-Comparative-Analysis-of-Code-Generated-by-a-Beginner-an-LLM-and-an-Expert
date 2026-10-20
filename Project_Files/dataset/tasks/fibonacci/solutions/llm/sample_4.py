def fibonacci(n: int) -> int:
    """Return the n-th Fibonacci number (fib(0)=0, fib(1)=1)."""
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
