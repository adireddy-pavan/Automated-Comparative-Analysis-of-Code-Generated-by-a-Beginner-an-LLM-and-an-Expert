def run_length_encode(s: str) -> str:
    """Encode each maximal run of identical characters as ``char + count``.

    Uses an index-based scan: an inner loop advances over the current run, then
    the run length is recorded before moving on.
    """
    result = ""
    i = 0
    n = len(s)
    while i < n:
        char = s[i]
        run = i
        while run < n and s[run] == char:
            run += 1
        result += char + str(run - i)
        i = run
    return result
