def caesar_cipher(text: str, shift: int) -> str:
    """Shift letters in ``text`` by ``shift``, wrapping within each case.

    Implementation detail: rather than special-casing upper vs. lower, we pick
    the correct base code point (65 for 'A', 97 for 'a') and apply one modular
    formula. Non-letters are emitted verbatim.
    """
    out = ""
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            offset = (ord(ch) - base + shift) % 26
            out += chr(base + offset)
        else:
            out += ch
    return out
