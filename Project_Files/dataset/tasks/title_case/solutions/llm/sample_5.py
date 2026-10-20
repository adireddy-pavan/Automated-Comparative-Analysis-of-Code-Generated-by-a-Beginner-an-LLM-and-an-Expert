def title_case(text: str) -> str:
    """Return ``text`` with each space-separated word capitalised."""
    return " ".join(
        part.lower().capitalize() if part else part
        for part in text.split(" ")
    )
