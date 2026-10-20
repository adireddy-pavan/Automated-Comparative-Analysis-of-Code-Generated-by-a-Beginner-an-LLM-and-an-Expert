from collections import deque
from typing import List


def coin_change(coins: List[int], amount: int) -> int:
    """Fewest coins via breadth-first search over remaining amounts.

    Each BFS level adds exactly one more coin, so the first time we reach 0 we
    have used the minimum possible number of coins. Visited remainders are
    pruned to avoid revisiting states.
    """
    if amount == 0:
        return 0

    usable = [c for c in coins if c > 0]
    visited = {amount}
    frontier = deque([amount])
    depth = 0

    while frontier:
        depth += 1
        for _ in range(len(frontier)):
            remaining = frontier.popleft()
            for coin in usable:
                nxt = remaining - coin
                if nxt == 0:
                    return depth
                if nxt > 0 and nxt not in visited:
                    visited.add(nxt)
                    frontier.append(nxt)
    return -1
