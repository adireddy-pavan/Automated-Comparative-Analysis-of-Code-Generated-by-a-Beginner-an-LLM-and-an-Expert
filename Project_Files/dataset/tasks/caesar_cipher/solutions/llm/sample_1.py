def caesar_cipher(text: str, shift: int) -> str:
    """Encrypt ``text`` with a Caesar cipher using the given ``shift``.

    Each ASCII letter is rotated by ``shift`` positions within its own case
    (wrapping around the alphabet); all other characters pass through
    unchanged. Negative and large shifts are normalised modulo 26.
    """
    shift %= 26
    result = []
    for char in text:
        if "a" <= char <= "z":
            base = ord("a")
            result.append(chr((ord(char) - base + shift) % 26 + base))
        elif "A" <= char <= "Z":
            base = ord("A")
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return "".join(result)
