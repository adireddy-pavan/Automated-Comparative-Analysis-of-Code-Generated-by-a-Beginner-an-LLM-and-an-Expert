from typing import List, Tuple


def _runs(s: str) -> List[Tuple[str, int]]:
    """Split a string into a list of ``(character, run_length)`` tuples."""
    runs: List[Tuple[str, int]] = []
    for ch in s:
        if runs and runs[-1][0] == ch:
            char, count = runs[-1]
            runs[-1] = (char, count + 1)
        else:
            runs.append((ch, 1))
    return runs


def run_length_encode(s: str) -> str:
    """Run-length encode ``s`` by first collecting runs, then formatting them.

    Separating the run detection from the formatting keeps each step small and
    independently testable.
    """
    return "".join(f"{char}{count}" for char, count in _runs(s))
