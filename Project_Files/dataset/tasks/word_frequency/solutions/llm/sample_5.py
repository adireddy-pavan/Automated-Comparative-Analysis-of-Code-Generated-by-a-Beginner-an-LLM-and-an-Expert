from typing import Dict


def _clean_word(token: str) -> str:
    """Lower-case ``token`` and keep only its alphanumeric characters."""
    return "".join(ch for ch in token.lower() if ch.isalnum())


def word_frequency(text: str) -> Dict[str, int]:
    """Compute the frequency of each word in ``text``.

    Splitting is done on whitespace; each token is then reduced to its
    alphanumeric characters with case folded. Empty tokens (pure
    punctuation) are discarded before counting. This avoids regular
    expressions entirely in favour of explicit character filtering.
    """
    frequencies: Dict[str, int] = {}
    for token in text.split():
        word = _clean_word(token)
        if not word:
            continue
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies
