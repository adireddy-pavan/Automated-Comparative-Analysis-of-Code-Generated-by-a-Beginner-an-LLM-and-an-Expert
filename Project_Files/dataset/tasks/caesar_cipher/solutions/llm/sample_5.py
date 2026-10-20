from typing import Iterator


def _encode(text: str, shift: int) -> Iterator[str]:
    for char in text:
        code = ord(char)
        if 65 <= code <= 90:  # uppercase A-Z
            yield chr((code - 65 + shift) % 26 + 65)
        elif 97 <= code <= 122:  # lowercase a-z
            yield chr((code - 97 + shift) % 26 + 97)
        else:
            yield char


def caesar_cipher(text: str, shift: int) -> str:
    """Caesar-cipher ``text`` by ``shift`` positions.

    A generator walks the characters lazily and yields the transformed result,
    which the public function joins into the final string. Works for negative
    shifts and shifts greater than 26 thanks to modular arithmetic.
    """
    return "".join(_encode(text, shift))
