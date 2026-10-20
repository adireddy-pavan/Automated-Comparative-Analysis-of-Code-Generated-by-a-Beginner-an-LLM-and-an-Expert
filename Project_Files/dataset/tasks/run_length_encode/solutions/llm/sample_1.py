def run_length_encode(s: str) -> str:
    """Encode ``s`` so each run of identical characters becomes the character
    followed by the length of the run.

    For example ``"aaabbc"`` becomes ``"a3b2c1"``. An empty string maps to an
    empty string.
    """
    if not s:
        return ""

    parts = []
    current = s[0]
    count = 1
    for ch in s[1:]:
        if ch == current:
            count += 1
        else:
            parts.append(f"{current}{count}")
            current = ch
            count = 1
    parts.append(f"{current}{count}")
    return "".join(parts)
