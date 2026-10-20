import re


def title_case(text: str) -> str:
    """Title-case each space-separated word using a regular expression.

    The pattern captures any run of non-space characters and a callback
    upper-cases its first letter while lower-casing the rest. Whitespace
    between words is left exactly as it was found.
    """

    def _capitalise(match: "re.Match[str]") -> str:
        word = match.group(0)
        return word[:1].upper() + word[1:].lower()

    return re.sub(r"[^ ]+", _capitalise, text)
