from itertools import groupby


def run_length_encode(s: str) -> str:
    """Run-length encode a string using :func:`itertools.groupby`.

    ``groupby`` collapses consecutive equal characters into groups, so the run
    length is simply the size of each group's run.
    """
    return "".join(f"{char}{len(list(group))}" for char, group in groupby(s))
