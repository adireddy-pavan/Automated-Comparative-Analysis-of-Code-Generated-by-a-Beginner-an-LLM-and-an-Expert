def title_case(text: str) -> str:
    """Capitalise the first letter of each space-separated word.

    Each word has its first character upper-cased and the remaining
    characters lower-cased. Splitting and re-joining on a single space
    preserves the original word spacing.
    """
    return " ".join(word.capitalize() for word in text.split(" "))
