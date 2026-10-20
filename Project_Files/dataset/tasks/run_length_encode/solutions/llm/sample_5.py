def run_length_encode(s: str) -> str:
    """Encode a string with run-length encoding.

    Walks the string while tracking the previous character and a running count;
    whenever the character changes, the completed run is flushed to the buffer.
    """
    buffer = []
    previous = None
    count = 0

    for ch in s:
        if ch == previous:
            count += 1
        else:
            if previous is not None:
                buffer.append(previous + str(count))
            previous = ch
            count = 1

    if previous is not None:
        buffer.append(previous + str(count))

    return "".join(buffer)
