from collections import deque


def is_subsequence(s: str, t: str) -> bool:
    """Determine if ``s`` is a subsequence of ``t`` using a consuming queue.

    The characters of ``s`` are placed in a queue. As we scan ``t`` we pop the
    front of the queue whenever it matches. If the queue empties, every needed
    character was found in order and ``s`` is a subsequence.
    """
    if not s:
        return True
    pending = deque(s)
    for ch in t:
        if pending and pending[0] == ch:
            pending.popleft()
        if not pending:
            return True
    return len(pending) == 0
