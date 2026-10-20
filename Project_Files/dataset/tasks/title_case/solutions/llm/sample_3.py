def title_case(text: str) -> str:
    """Title-case ``text`` by scanning characters one at a time.

    A character is the start of a word if it is the very first character
    or if it immediately follows a space. The starting character is
    upper-cased and every other character is lower-cased; spaces are
    copied through unchanged so the layout is preserved.
    """
    result = []
    at_word_start = True
    for char in text:
        if char == " ":
            result.append(char)
            at_word_start = True
        elif at_word_start:
            result.append(char.upper())
            at_word_start = False
        else:
            result.append(char.lower())
    return "".join(result)
